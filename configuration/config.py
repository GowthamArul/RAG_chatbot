import logging
import os

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
SCHEMA_NAME = os.getenv("SCHEMA_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")