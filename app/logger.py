import logging
import sys
from app.config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        stream=sys.stdout
    )
