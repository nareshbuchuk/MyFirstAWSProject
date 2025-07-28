from fastapi import APIRouter, HTTPException, Request, status, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from typing import List, Optional
import uuid
from datetime import datetime

from app.s3_client import s3_client
from app.schemas import FileUploadResponse, FileListResponse, PresignedURLResponse
from app.auth import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()

@router.get("/", response_class=HTMLResponse)
async def upload_form():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>S3 File Upload</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .container { border: 1px solid #ccc; padding: 20px; border-radius: 5px; }
                .progress { width: 100%; height: 20px; background-color: #f0f0f0; border-radius: 10px; }
                .progress-bar { width: 0%; height: 100%; background-color: #4CAF50; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Upload file to S3</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input name="file" type="file" required>
                    <button type="submit">Upload</button>
                </form>
                <div class="progress">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <p id="status"></p>
            </div>
            <script>
                const form = document.getElementById('uploadForm');
                const status = document.getElementById('status');
                const progressBar = document.getElementById('progressBar');

                form.onsubmit = async (e) => {
                    e.preventDefault();
                    const formData = new FormData(form);
                    
                    try {
                        const response = await fetch('/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            status.textContent = result.message;
                            progressBar.style.width = '100%';
                        } else {
                            status.textContent = result.detail || 'Upload failed';
                        }
                    } catch (error) {
                        status.textContent = 'Upload failed: ' + error.message;
                    }
                };
            </script>
        </body>
    </html>
    """

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    max_size: int = 10_000_000,  # 10MB
    allowed_types: set = {"image/jpeg", "image/png", "application/pdf"}
):
    # Validate file size
    content = await file.read()
    await file.seek(0)
    
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    
    # Validate content type
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File type not supported"
        )
    
    # Generate secure filename
    ext = file.filename.split('.')[-1] if '.' in file.filename else ''
    secure_filename = f"{current_user['username']}/{uuid.uuid4()}.{ext}"
    
    # Add metadata
    metadata = {
        "username": current_user['username'],
        "original_filename": file.filename,
        "content_type": file.content_type,
        "upload_date": datetime.utcnow().isoformat()
    }
    
    success, error = await s3_client.upload_file(file, secure_filename, metadata)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error
        )
    
    return FileUploadResponse(
        message=f"Successfully uploaded {file.filename}",
        file_key=secure_filename
    )

@router.get("/files", response_model=List[FileListResponse])
async def list_files(
    current_user: dict = Depends(get_current_user),
    prefix: Optional[str] = None
):
    """List files for the current user"""
    user_prefix = f"{current_user['username']}/"
    if prefix:
        user_prefix = f"{user_prefix}{prefix}"
    
    files = await s3_client.list_files(prefix=user_prefix)
    return [FileListResponse(**file) for file in files]

@router.get("/files/{file_key}/download")
async def get_download_url(
    file_key: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate a presigned URL for file download"""
    # Verify the file belongs to the user
    if not file_key.startswith(f"{current_user['username']}/"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    url = s3_client.generate_presigned_url(file_key)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return PresignedURLResponse(download_url=url)
