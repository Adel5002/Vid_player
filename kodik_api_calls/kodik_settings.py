import os
from dotenv import load_dotenv

load_dotenv()

KODIK_SEARCH = os.getenv("SEARCH_FOR_SERIAL")
KODIK_TOKEN = os.getenv("KODIK_API_KEY")