from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileUploadResponse(BaseModel):
    message: str
    file_key: str

class FileListResponse(BaseModel):
    key: str
    size: int
    last_modified: datetime
    etag: str

class PresignedURLResponse(BaseModel):
    download_url: str

class UserResponse(BaseModel):
    username: str
    email: str
    is_active: bool
