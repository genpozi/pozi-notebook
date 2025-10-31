"""
Authentication router for Open Notebook API.
Provides endpoints for user authentication (signup, signin, status).
"""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from pydantic import BaseModel, EmailStr

from api.auth import create_jwt_token, hash_password, verify_password
from open_notebook.database.repository import repo_create, repo_query

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    """Request model for user signup"""
    email: EmailStr
    password: str
    name: str


class SigninRequest(BaseModel):
    """Request model for user signin"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication"""
    token: str
    user_id: str
    email: str
    name: str
    role: str


@router.get("/status")
async def get_auth_status():
    """
    Check if authentication is enabled.
    Always returns true for multi-user system.
    """
    return {
        "auth_enabled": True,
        "message": "Multi-user authentication is enabled"
    }


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """
    Register a new user account.
    
    Creates a new user with email, password (hashed with Argon2), and name.
    Returns a JWT token for immediate authentication.
    """
    try:
        # Check if user already exists
        existing_users = await repo_query(
            "SELECT id FROM user WHERE email = $email",
            {"email": request.email}
        )
        
        if existing_users and len(existing_users) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )
        
        # Create user directly with SurrealQL
        # Use crypto::argon2::generate for password hashing (SurrealDB built-in)
        created_users = await repo_query("""
            CREATE user CONTENT {
                email: $email,
                password: crypto::argon2::generate($password),
                name: $name,
                role: $role,
                created: time::now(),
                updated: time::now()
            }
        """, {
            "email": request.email,
            "password": request.password,
            "name": request.name,
            "role": "user"
        })
        
        if not created_users or len(created_users) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        user = created_users[0]
        user_id = str(user.get("id", ""))
        
        # Generate JWT token
        token = create_jwt_token(user_id, request.email, "user")
        
        return TokenResponse(
            token=token,
            user_id=user_id,
            email=request.email,
            name=request.name,
            role="user"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Signup error")
        error_msg = str(e)
        
        # Check for duplicate email (database constraint)
        if "already exists" in error_msg.lower() or "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists"
            )
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {error_msg}"
        )


@router.post("/signin", response_model=TokenResponse)
async def signin(request: SigninRequest):
    """
    Authenticate an existing user.
    
    Validates email and password, returns JWT token on success.
    """
    try:
        from surrealdb import AsyncSurreal
        from open_notebook.database.repository import get_database_url, get_database_password
        
        # Connect with root credentials to bypass permissions
        db = AsyncSurreal(get_database_url())
        await db.signin({
            "username": os.environ.get("SURREAL_USER"),
            "password": get_database_password(),
        })
        await db.use(
            os.environ.get("SURREAL_NAMESPACE"),
            os.environ.get("SURREAL_DATABASE")
        )
        
        # Query all users and filter in Python
        # This is a workaround for the permissions issue
        all_users = await db.query("SELECT * FROM user")
        
        # Find the user with matching email
        user = None
        for u in all_users:
            if u.get("email") == request.email:
                user = u
                break
        
        if not user:
            await db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        password_check = await db.query("""
            RETURN crypto::argon2::compare($hash, $password);
        """, {
            "hash": user.get("password"),
            "password": request.password
        })
        
        # password_check is a boolean value
        if not password_check or not password_check:
            await db.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        result = [user]
        
        await db.close()
        
        # result is a list of query results
        if not result or len(result) == 0 or result[0] is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = result[0]
        user_id = str(user.get("id", ""))
        user_email = user.get("email", request.email)
        user_name = user.get("name", "")
        user_role = user.get("role", "user")
        
        # Generate JWT token
        token = create_jwt_token(user_id, user_email, user_role)
        
        return TokenResponse(
            token=token,
            user_id=user_id,
            email=user_email,
            name=user_name,
            role=user_role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Signin error")
        error_msg = str(e)
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signin failed: {error_msg}"
        )
