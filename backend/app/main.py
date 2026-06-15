import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, async_session
from app.seed import seed_database

# Routers
from app.api.auth import router as auth_router
from app.api.customers import router as customers_router
from app.api.orders import router as orders_router
from app.api.segments import router as segments_router
from app.api.campaigns import router as campaigns_router
from app.api.ai import router as ai_router
from app.api.receipts import router as receipts_router

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("smartreach")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager to handle startup and shutdown events."""
    logger.info("Initializing database...")
    await init_db()
    
    logger.info("Running database seeding check...")
    async with async_session() as session:
        try:
            await seed_database(session)
        except Exception as e:
            logger.error(f"Error during database seed: {e}", exc_info=True)
            
    yield
    logger.info("Shutting down application.")

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-native customer engagement and campaign orchestration platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(segments_router)
app.include_router(campaigns_router)
app.include_router(ai_router)
app.include_router(receipts_router)

@app.get("/health")
async def health_check():
    """Health check endpoint for verification."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database": "sqlite (async)"
    }

@app.get("/")
async def root():
    """Root metadata endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} Backend API",
        "documentation": "/docs"
    }
