import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
SERVER_HOST = os.environ.get("SERVER_HOST", "localhost")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
ES_INDEX_NAME = os.environ.get("ES_INDEX_NAME", "movies")
