from typing import Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import logging
from aws_xray_sdk.core import patch_all

logger = logging.getLogger(__name__)
patch_all()  # AWS X-Ray integration

class S3Client:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET

    async def upload_file(self, file_obj, filename: str, metadata: Optional[dict] = None) -> tuple[bool, str]:
        """Upload file to S3 with retries and metadata"""
        try:
            extra_args = {
                'Metadata': metadata or {},
                'ContentType': file_obj.content_type
            }
            
            self.client.upload_fileobj(
                file_obj.file, 
                self.bucket, 
                filename,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Uploaded {filename} to S3 bucket {self.bucket}")
            return True, ""
            
        except ClientError as e:
            error_msg = f"Failed to upload {filename}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for downloading a file"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {key}: {e}")
            return None

    async def list_files(self, prefix: str = "") -> list[dict]:
        """List files in the bucket with pagination support"""
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            files = []
            
            async for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append({
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'],
                            'etag': obj['ETag']
                        })
            
            return files
        except ClientError as e:
            logger.error(f"Failed to list files: {e}")
            return []

s3_client = S3Client()
