#!/usr/bin/env python
import os
import time
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cleanup_cron.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get the absolute path to the Django project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANAGE_PY = os.path.join(BASE_DIR, "manage.py")

def run_cleanup():
    """Run the cleanup_expired_reservations management command"""
    try:
        logger.info(f"Running cleanup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result = subprocess.run(
            ["python3", MANAGE_PY, "cleanup_expired_reservations"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        
        if result.returncode == 0:
            logger.info(f"Cleanup successful: {result.stdout}")
        else:
            logger.error(f"Cleanup failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error running cleanup: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting cleanup scheduler")
    
    try:
        # Run cleanup every minute
        while True:
            run_cleanup()
            time.sleep(60)  # Wait for 60 seconds
    except KeyboardInterrupt:
        logger.info("Cleanup scheduler stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
