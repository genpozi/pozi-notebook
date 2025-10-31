# Multi-User Authentication & Account Management Implementation Plan

## Executive Summary

This document outlines the implementation plan for adding proper user authentication and account management to Open Notebook. The current system uses a single shared password with no user concept in the database. This plan migrates to a proper multi-user system with data isolation.

## Current State Analysis

### Authentication
- **Type**: Single shared password via Bearer token
- **Storage**: Environment variable `OPEN_NOTEBOOK_PASSWORD`
- **Middleware**: `PasswordAuthMiddleware` in `api/auth.py`
- **Frontend**: Simple login form with token storage in localStorage

### Database Schema
- **No user table** - all data is shared
- **Main tables**: `notebook`, `source`, `note`, `source_embedding`, `source_insight`, `transformation`, `podcast_config`
- **Relationships**: `reference` (source→notebook), `artifact` (note→notebook)
- **No ownership fields** - no way to associate data with users

## Recommended Architecture

### 1. Multi-Tenancy Pattern: **Shared Database with Row-Level Security**

**Why this approach:**
- Simplicity: Single database instance
- Cost-effective: No separate databases per user
- Enables future sharing features
- SurrealDB's record-level permissions are perfect for this

### 2. Authentication Strategy: **JWT with SurrealDB Record Access**

**Why JWT + SurrealDB:**
- Native SurrealDB 2.0+ support
- Stateless authentication
- Secure password hashing (Argon2)
- Built-in token expiration
- Perfect for distributed systems

### 3. Data Isolation: **User-Owned Resources**

Every resource will have a `user_id` field, and SurrealDB permissions will enforce isolation at the database level.

## Implementation Phases

### Phase 1: Database Schema Migration (Week 1)

#### Step 1.1: Create User Table
```surrealql
-- migrations/10.surrealql
DEFINE TABLE user SCHEMAFULL
  PERMISSIONS 
    FOR select, update, delete WHERE id = $auth.id
    FOR create WHERE true;

DEFINE FIELD email ON user TYPE string ASSERT string::is_email($value);
DEFINE FIELD password ON user TYPE string;
DEFINE FIELD name ON user TYPE string;
DEFINE FIELD role ON user TYPE string DEFAULT "user";
DEFINE FIELD created ON user DEFAULT time::now();
DEFINE FIELD updated ON user DEFAULT time::now();

DEFINE INDEX email_unique ON user FIELDS email UNIQUE;
```

#### Step 1.2: Define Record Access
```surrealql
DEFINE ACCESS user_access ON DATABASE TYPE RECORD
  SIGNUP (
    CREATE user SET 
      email = $email,
      name = $name,
      password = crypto::argon2::generate($password),
      role = "user"
  )
  SIGNIN (
    SELECT * FROM user 
    WHERE email = $email 
    AND crypto::argon2::compare(password, $password)
  )
  DURATION FOR TOKEN 24h, FOR SESSION 7d;
```

#### Step 1.3: Add User ID Fields
```surrealql
-- Add user_id to all main tables (nullable for migration)
DEFINE FIELD user_id ON TABLE notebook TYPE option<record<user>>;
DEFINE FIELD user_id ON TABLE source TYPE option<record<user>>;
DEFINE FIELD user_id ON TABLE note TYPE option<record<user>>;
DEFINE FIELD user_id ON TABLE transformation TYPE option<record<user>>;

-- Add indexes for performance
DEFINE INDEX user_idx ON notebook FIELDS user_id;
DEFINE INDEX user_idx ON source FIELDS user_id;
DEFINE INDEX user_idx ON note FIELDS user_id;
```

#### Step 1.4: Create Default Admin & Migrate Data
```surrealql
-- Create admin user for existing data
CREATE user:admin SET
  email = "admin@localhost",
  password = crypto::argon2::generate("change-me-immediately"),
  name = "System Administrator",
  role = "admin";

-- Assign existing data to admin
UPDATE notebook SET user_id = user:admin WHERE user_id = NONE;
UPDATE source SET user_id = user:admin WHERE user_id = NONE;
UPDATE note SET user_id = user:admin WHERE user_id = NONE;
UPDATE transformation SET user_id = user:admin WHERE user_id = NONE;
```

#### Step 1.5: Enable Permissions
```surrealql
-- After migration, enforce permissions
DEFINE TABLE notebook SCHEMAFULL
  PERMISSIONS 
    FOR select, create, update, delete 
    WHERE user_id = $auth.id OR $auth.role = "admin";

DEFINE TABLE source SCHEMAFULL
  PERMISSIONS 
    FOR select, create, update, delete 
    WHERE user_id = $auth.id OR $auth.role = "admin";

DEFINE TABLE note SCHEMAFULL
  PERMISSIONS 
    FOR select, create, update, delete 
    WHERE user_id = $auth.id OR $auth.role = "admin";
```

### Phase 2: Backend API Implementation (Week 2)

#### Step 2.1: Update Database Connection
```python
# open_notebook/database/repository.py
async def get_authenticated_db(token: str):
    """Get database connection with user authentication"""
    db = Surreal()
    await db.connect(SURREAL_URL)
    await db.authenticate(token)  # Use JWT token
    return db
```

#### Step 2.2: New Auth Endpoints
```python
# api/routers/auth.py
from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str

@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    async with db_connection() as db:
        result = await db.signup({
            "NS": "open_notebook",
            "DB": "production",
            "AC": "user_access",
            "email": request.email,
            "password": request.password,
            "name": request.name
        })
        return TokenResponse(
            token=result["token"],
            user_id=result["id"],
            email=request.email,
            name=request.name
        )

@router.post("/signin", response_model=TokenResponse)
async def signin(request: SigninRequest):
    async with db_connection() as db:
        result = await db.signin({
            "NS": "open_notebook",
            "DB": "production",
            "AC": "user_access",
            "email": request.email,
            "password": request.password
        })
        return TokenResponse(
            token=result["token"],
            user_id=result["id"],
            email=request.email,
            name=result.get("name", "")
        )
```

#### Step 2.3: Update Authentication Middleware
```python
# api/auth.py
class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/", "/health", "/docs", "/openapi.json", "/redoc",
            "/api/auth/signup", "/api/auth/signin", "/api/auth/status"
        ]
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode token (SurrealDB validates)
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get("ID")
            
            if not user_id:
                raise ValueError("Invalid token")
            
            # Store user info in request state
            request.state.user_id = user_id
            request.state.token = token
            
            return await call_next(request)
        except Exception:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
```

#### Step 2.4: Update Domain Models
```python
# open_notebook/domain/notebook.py
class Notebook(ObjectModel):
    table_name: ClassVar[str] = "notebook"
    name: str
    description: str
    archived: Optional[bool] = False
    user_id: Optional[str] = None  # Add user_id field
    
    async def create(self, user_id: str):
        """Create notebook with user ownership"""
        self.user_id = user_id
        return await super().create()
```

### Phase 3: Frontend Implementation (Week 3)

#### Step 3.1: Update Auth Store
```typescript
// frontend/src/lib/stores/auth-store.ts
interface User {
  id: string
  email: string
  name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  signup: (email: string, password: string, name: string) => Promise<void>
  signin: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      signup: async (email, password, name) => {
        const apiUrl = await getApiUrl()
        const response = await fetch(`${apiUrl}/api/auth/signup`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, name })
        })
        
        if (!response.ok) throw new Error('Signup failed')
        
        const data = await response.json()
        set({
          user: { id: data.user_id, email: data.email, name: data.name },
          token: data.token,
          isAuthenticated: true
        })
      },
      
      signin: async (email, password) => {
        const apiUrl = await getApiUrl()
        const response = await fetch(`${apiUrl}/api/auth/signin`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        })
        
        if (!response.ok) throw new Error('Signin failed')
        
        const data = await response.json()
        set({
          user: { id: data.user_id, email: data.email, name: data.name },
          token: data.token,
          isAuthenticated: true
        })
      },
      
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
      }
    }),
    { name: 'auth-storage' }
  )
)
```

#### Step 3.2: Create Signup Page
```typescript
// frontend/src/app/(auth)/signup/page.tsx
export default function SignupPage() {
  return <SignupForm />
}

// frontend/src/components/auth/SignupForm.tsx
export function SignupForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const { signup } = useAuthStore()
  const router = useRouter()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await signup(email, password, name)
      router.push('/notebooks')
    } catch (error) {
      // Handle error
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <Input type="text" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      <Input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <Input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <Button type="submit">Sign Up</Button>
    </form>
  )
}
```

#### Step 3.3: Update Login Form
```typescript
// frontend/src/components/auth/LoginForm.tsx
export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { signin } = useAuthStore()
  const router = useRouter()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await signin(email, password)
      router.push('/notebooks')
    } catch (error) {
      // Handle error
    }
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <Input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <Input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      <Button type="submit">Sign In</Button>
      <Link href="/signup">Don't have an account? Sign up</Link>
    </form>
  )
}
```

### Phase 4: Testing & Validation (Week 4)

#### Test Cases
1. **User Registration**
   - [ ] Can create new user with valid email/password
   - [ ] Cannot create user with duplicate email
   - [ ] Password is hashed in database
   - [ ] Token is returned on successful signup

2. **User Authentication**
   - [ ] Can login with correct credentials
   - [ ] Cannot login with incorrect password
   - [ ] Token is valid for 24 hours
   - [ ] Token expires after 24 hours

3. **Data Isolation**
   - [ ] User A cannot see User B's notebooks
   - [ ] User A cannot see User B's sources
   - [ ] User A cannot see User B's notes
   - [ ] User A cannot modify User B's data

4. **Admin Access**
   - [ ] Admin can see all users' data
   - [ ] Admin can modify all users' data

5. **Migration**
   - [ ] Existing data is assigned to admin user
   - [ ] Admin can access all pre-migration data
   - [ ] New users start with empty notebooks

## Rollback Plan

If issues arise, rollback steps:

1. **Disable new authentication**:
   - Revert `api/main.py` to use `PasswordAuthMiddleware`
   - Comment out JWT middleware

2. **Remove permissions**:
   ```surrealql
   -- Remove permissions from tables
   DEFINE TABLE notebook SCHEMAFULL PERMISSIONS FULL;
   DEFINE TABLE source SCHEMAFULL PERMISSIONS FULL;
   DEFINE TABLE note SCHEMAFULL PERMISSIONS FULL;
   ```

3. **Keep user_id fields** (for future retry):
   - Don't drop user_id columns
   - They'll be ignored without permissions

## Future Enhancements

### Phase 5: Advanced Features
- **OAuth Integration**: Google, GitHub, Microsoft
- **Team/Organization Support**: Multi-user notebooks
- **Sharing**: Share notebooks with other users
- **API Keys**: For programmatic access
- **2FA**: Two-factor authentication
- **Password Reset**: Email-based password recovery
- **User Profiles**: Avatar, bio, preferences
- **Activity Logs**: Audit trail of user actions

## Security Considerations

1. **Password Security**
   - Use Argon2 hashing (built into SurrealDB)
   - Enforce minimum password length (8 characters)
   - Consider password complexity requirements

2. **Token Security**
   - JWT tokens expire after 24 hours
   - Store tokens securely (httpOnly cookies in production)
   - Implement token refresh mechanism

3. **Rate Limiting**
   - Limit login attempts (5 per 15 minutes)
   - Limit signup attempts (3 per hour per IP)

4. **Input Validation**
   - Validate email format
   - Sanitize user inputs
   - Prevent SQL injection (SurrealDB parameterized queries)

5. **HTTPS**
   - Enforce HTTPS in production
   - Use secure cookies

## Performance Considerations

1. **Indexing**
   - Add indexes on user_id fields
   - Add index on email field

2. **Query Optimization**
   - Use specific field selection
   - Avoid SELECT * on large tables

3. **Caching**
   - Cache user info in request context
   - Cache frequently accessed data

## Documentation Updates

1. **README.md**: Update with new authentication info
2. **API Documentation**: Document new auth endpoints
3. **User Guide**: Add signup/login instructions
4. **Deployment Guide**: Update environment variables

## Timeline Summary

- **Week 1**: Database schema migration
- **Week 2**: Backend API implementation
- **Week 3**: Frontend implementation
- **Week 4**: Testing & validation
- **Total**: 4 weeks for full implementation

## Success Criteria

- [ ] Users can sign up with email/password
- [ ] Users can log in and receive JWT token
- [ ] Users can only see their own data
- [ ] Admin can see all data
- [ ] Existing data is preserved and accessible
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Performance is acceptable (< 100ms for auth checks)
