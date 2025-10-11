from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import auth, farmers, chiefs, inventory
from contextlib import asynccontextmanager
from app.routes import sync, reports
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "message": "Internal server error"}
    )

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(farmers.router, prefix="/api/farmers", tags=["Farmers"])
app.include_router(chiefs.router, prefix="/api/chiefs", tags=["Chiefs"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(sync.router, prefix="/api/sync", tags=["Synchronization"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

@app.get("/")
async def root():
    return {
        "message": "Zambian Farmer Support System API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
