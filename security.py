from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from pwdlib import PasswordHash
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expires}, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_user_id(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, ValueError, KeyError, TypeError):
        return None
