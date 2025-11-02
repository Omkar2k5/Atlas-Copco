"""
AssemblyFlow Backend - Main Application Entry Point
FastAPI application for motion analysis and pose comparison.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import process_video, compare, session


# Create FastAPI application
app = FastAPI(
    title="AssemblyFlow API",
    description="Motion analysis and human pose comparison system backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
# Allow frontend origins
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",  # Alternative localhost
    # Add production origins here when deploying
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "service": "AssemblyFlow API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    from app.db.vector_db import get_vector_db
    from app.db.storage import get_storage
    
    try:
        # Check vector database
        vector_db = get_vector_db()
        embedding_count = vector_db.count()
        
        # Check storage
        storage = get_storage()
        session_count = len(storage.list_sessions())
        
        return {
            "status": "healthy",
            "vector_database": "connected",
            "embeddings_count": embedding_count,
            "sessions_count": session_count
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Register API routers
app.include_router(
    process_video.router,
    prefix="/api",
    tags=["Process Video"]
)

app.include_router(
    compare.router,
    prefix="/api",
    tags=["Compare Sessions"]
)

app.include_router(
    session.router,
    prefix="/api",
    tags=["Session Management"]
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for uncaught errors."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    from app.core.pose_model import load_model
    from app.db.vector_db import get_vector_db
    from app.db.storage import get_storage
    
    # Initialize pose model
    print("Loading pose estimation model...")
    load_model()
    print("✓ Pose model loaded")
    
    # Initialize vector database
    print("Connecting to vector database...")
    vector_db = get_vector_db()
    print(f"✓ Vector database connected ({vector_db.count()} embeddings)")
    
    # Initialize storage
    print("Initializing session storage...")
    storage = get_storage()
    print(f"✓ Session storage ready ({len(storage.list_sessions())} sessions)")
    
    print("\n🚀 AssemblyFlow API is ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("\n👋 Shutting down AssemblyFlow API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
