import boto3
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def upload_file_to_s3(file_obj, filename):
    s3 = get_s3_client()
    try:
        s3.upload_fileobj(file_obj, settings.S3_BUCKET, filename)
        logger.info(f"Uploaded {filename} to S3 bucket {settings.S3_BUCKET}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {filename}: {e}")
        return False
