import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./certs.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CERTIFICATES_DIR = os.getenv("CERTIFICATES_DIR", "certificates")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
