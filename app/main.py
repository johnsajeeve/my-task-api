"""
Main FastAPI application.
Sets up the web server, logging, and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from datetime import datetime

from app.database import init_db
from app.routes import router

# ============================================================================
# LOGGING SETUP (Phase 2)
# ============================================================================

# Create logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Task Processing API",
    description="Event-driven task processing system with Celery + Redis",
    version="3.0.0"
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE LOGGING MIDDLEWARE (Phase 2)
# ============================================================================

@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests and responses with timing"""
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Time the request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log response with timing
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    return response

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
def startup_event():
    """Initialize database when app starts"""
    logger.info("=" * 60)
    logger.info("🚀 TASK PROCESSING API STARTING")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now()}")
    logger.info("Initializing database...")
    
    init_db()
    
    logger.info("✅ Database initialized")
    logger.info("✅ App ready to receive requests")
    logger.info("=" * 60)

# ============================================================================
# SHUTDOWN EVENT
# ============================================================================

@app.on_event("shutdown")
def shutdown_event():
    """Log when app shuts down"""
    logger.info("=" * 60)
    logger.info("🛑 TASK PROCESSING API SHUTTING DOWN")
    logger.info(f"Shutdown time: {datetime.now()}")
    logger.info("=" * 60)

# ============================================================================
# INCLUDE ROUTES
# ============================================================================

app.include_router(router)

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    Returns 200 if API is running.
    """
    logger.info("Health check request")
    return {
        "status": "healthy",
        "message": "Task Processing API is running",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["info"])
def root():
    """Root endpoint with API information"""
    return {
        "name": "Task Processing API",
        "version": "3.0.0",
        "description": "Event-driven task processing with Celery + Redis",
        "docs": "/docs",
        "redoc": "/redoc"
    }