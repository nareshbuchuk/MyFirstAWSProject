import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET = os.getenv("S3_BUCKET")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
