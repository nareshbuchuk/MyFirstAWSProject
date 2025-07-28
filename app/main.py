from fastapi import FastAPI
from app.routes import upload
from app.logger import setup_logging

setup_logging()

app = FastAPI(title="S3 File Upload Portal")
app.include_router(upload.router)
