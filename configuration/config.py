import base64
import logging
import os
import json

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


DB_USER = 'myuser'
DB_PASSWORD = 'password'
DB_HOST = 'localhost'
DB_NAME = 'pgvector_db'