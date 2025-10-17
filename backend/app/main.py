"""
Zambian Farmer Support System — FastAPI Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import asyncio

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, create_indexes
from app.routes import auth, farmers, chiefs, inventory, sync


# ============================================
# Logging Configuration
# ============================================
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================
# Lifespan Context Manager
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown tasks"""
    logger.info("🚀 Starting Zambian Farmer Support System backend...")

    # Retry MongoDB connection a few times if container isn't ready
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await connect_to_mongo()
            await create_indexes()
            logger.info("✅ MongoDB connection established and indexes created.")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"MongoDB connection failed (attempt {attempt+1}/{max_retries}): {e}")
                await asyncio.sleep(5)
            else:
                logger.error("❌ Could not connect to MongoDB after multiple attempts.")
                raise

    yield  # Application runs here

    logger.info("🛑 Shutting down application...")
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete.")


# ============================================
# FastAPI Application
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Comprehensive API for managing farmer registration, inventory, and support across Zambia.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ============================================
# Middleware: CORS & Request Timing
# ============================================
allowed_origins = (
    settings.ALLOWED_ORIGINS
    if isinstance(settings.ALLOWED_ORIGINS, list)
    else [o.strip() for o in str(settings.ALLOWED_ORIGINS).split(",") if o.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to every response"""
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled exception during request processing")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    process_time = round(time.time() - start_time, 3)
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================
# Exception Handlers
# ============================================
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ============================================
# Health Check & Root Endpoints
# ============================================
@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with useful links"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# ============================================
# Routers
# ============================================
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(chiefs.router, prefix="/api/chiefs", tags=["Chiefs"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(sync.router, prefix="/api/sync", tags=["Synchronization"])


# ============================================
# Uvicorn Entry Point
# ============================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT if hasattr(settings, "API_PORT") else 8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
