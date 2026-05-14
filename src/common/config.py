import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/fashion_selector",
)

DAILY_CRAWL_HOUR = int(os.getenv("DAILY_CRAWL_HOUR", "2"))
WEEKLY_CRAWL_DAY = os.getenv("WEEKLY_CRAWL_DAY", "monday")

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
IMAGE_RECOGNITION_API_KEY = os.getenv("IMAGE_RECOGNITION_API_KEY", "")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = os.getenv("LOG_DIR", "logs")
