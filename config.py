import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dealership.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
