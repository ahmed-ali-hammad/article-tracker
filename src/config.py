import os
from pathlib import Path

from dotenv import load_dotenv

# Path for the .env file
env_path = Path(__file__).resolve().parent.parent / "conf" / ".env.example"

# Load environment variables from the .env file
load_dotenv(env_path)


class Config:
    """Base configuration class to load environment variables."""

    DATABASE_URI = os.getenv("DATABASE_URI")
    ASYNC_DATABASE_URI = os.getenv("ASYNC_DATABASE_URI")
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST")
    FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT")
    DEBUG = os.getenv("DEBUG")
