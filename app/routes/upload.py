from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from app.s3_client import upload_file_to_s3
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
def upload_form():
    return """
    <html>
        <body>
            <h2>Upload file to S3</h2>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file">
                <input type="submit">
            </form>
        </body>
    </html>
    """

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if upload_file_to_s3(file.file, file.filename):
        return {"message": f"Uploaded {file.filename} successfully!"}
    else:
        return {"error": "Upload failed."}
