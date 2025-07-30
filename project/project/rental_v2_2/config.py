import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "fleet.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

DEBUG = os.getenv("DEBUG") == "False"