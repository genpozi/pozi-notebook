from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.auth import JWTAuthMiddleware, PasswordAuthMiddleware
from api.routers import (
    auth,
    chat,
    config,
    context,
    embedding,
    embedding_rebuild,
    episode_profiles,
    insights,
    models,
    notebooks,
    notes,
    podcasts,
    search,
    settings,
    source_chat,
    sources,
    speaker_profiles,
    transformations,
)
from api.routers import commands as commands_router
from open_notebook.database.async_migrate import AsyncMigrationManager
from open_notebook.database.repository import db_connection, repo_query

# Import commands to register them in the API process
try:

    logger.info("Commands imported in API process")
except Exception as e:
    logger.error(f"Failed to import commands in API process: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    Runs database migrations automatically on startup.
    """
    # Startup: Run database migrations
    logger.info("Starting API initialization...")

    try:
        migration_manager = AsyncMigrationManager()
        current_version = await migration_manager.get_current_version()
        logger.info(f"Current database version: {current_version}")

        if await migration_manager.needs_migration():
            logger.warning("Database migrations are pending. Running migrations...")
            await migration_manager.run_migration_up()
            new_version = await migration_manager.get_current_version()
            logger.success(f"Migrations completed successfully. Database is now at version {new_version}")
        else:
            logger.info("Database is already at the latest version. No migrations needed.")
    except Exception as e:
        logger.error(f"CRITICAL: Database migration failed: {str(e)}")
        logger.exception(e)
        # Fail fast - don't start the API with an outdated database schema
        raise RuntimeError(f"Failed to run database migrations: {str(e)}") from e

    # Ensure admin user exists
    try:
        logger.info("Checking for admin user...")
        admin_check = await repo_query("SELECT * FROM user:admin")
        
        if not admin_check or len(admin_check) == 0:
            logger.warning("Admin user not found. Creating default admin user...")
            await repo_query("""
                CREATE user:admin SET
                  email = "admin@localhost",
                  password = crypto::argon2::generate("change-me-immediately"),
                  name = "System Administrator",
                  role = "admin",
                  created = time::now(),
                  updated = time::now()
            """)
            logger.success("Admin user created successfully. Email: admin@localhost, Password: change-me-immediately")
            logger.warning("⚠️  IMPORTANT: Change the admin password immediately after first login!")
        else:
            logger.info("Admin user already exists")
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        logger.warning("Continuing without admin user - you may need to create it manually")

    logger.success("API initialization completed successfully")

    # Yield control to the application
    yield

    # Shutdown: cleanup if needed
    logger.info("API shutdown complete")


app = FastAPI(
    title="Open Notebook API",
    description="API for Open Notebook - Research Assistant",
    version="0.2.2",
    lifespan=lifespan,
)

# Add JWT authentication middleware
# Exclude public endpoints from authentication
app.add_middleware(
    JWTAuthMiddleware,
    excluded_paths=[
        "/", "/health", "/docs", "/openapi.json", "/redoc",
        "/api/auth/signup", "/api/auth/signin", "/api/auth/status", "/api/config"
    ]
)
# Add JWT authentication middleware
# Exclude public endpoints from authentication
app.add_middleware(
    JWTAuthMiddleware,
    excluded_paths=[
        "/", "/health", "/docs", "/openapi.json", "/redoc",
        "/api/auth/signup", "/api/auth/signin", "/api/auth/status", "/api/config"
    ]
)
# Add JWT authentication middleware
# Exclude public endpoints from authentication
app.add_middleware(
    JWTAuthMiddleware,
    excluded_paths=[
        "/", "/health", "/docs", "/openapi.json", "/redoc",
        "/api/auth/signup", "/api/auth/signin", "/api/auth/status", "/api/config"
    ]
)

# Add CORS middleware last (so it processes first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(config.router, prefix="/api", tags=["config"])
app.include_router(notebooks.router, prefix="/api", tags=["notebooks"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(transformations.router, prefix="/api", tags=["transformations"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(embedding.router, prefix="/api", tags=["embedding"])
app.include_router(embedding_rebuild.router, prefix="/api/embeddings", tags=["embeddings"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(sources.router, prefix="/api", tags=["sources"])
app.include_router(insights.router, prefix="/api", tags=["insights"])
app.include_router(commands_router.router, prefix="/api", tags=["commands"])
app.include_router(podcasts.router, prefix="/api", tags=["podcasts"])
app.include_router(episode_profiles.router, prefix="/api", tags=["episode-profiles"])
app.include_router(speaker_profiles.router, prefix="/api", tags=["speaker-profiles"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(source_chat.router, prefix="/api", tags=["source-chat"])


@app.get("/")
async def root():
    return {"message": "Open Notebook API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
