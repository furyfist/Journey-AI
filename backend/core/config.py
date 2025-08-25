# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORTIA_API_KEY: str = os.getenv("PORTIA_API_KEY")

settings = Settings()