from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.routes import upload, auth
from app.logger import setup_logging
from app.auth import get_current_user

setup_logging()

app = FastAPI(
    title="S3 File Upload Portal",
    description="A secure file upload portal using FastAPI and AWS S3",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(
    upload.router,
    prefix="/api/v1",
    tags=["files"],
    dependencies=[Depends(get_current_user)]
)
