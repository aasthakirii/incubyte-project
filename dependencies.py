from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .security import decode_user_id

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    user_id = decode_user_id(credentials.credentials)
    user = db.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
