from datetime import datetime, timedelta, timezone

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError, raise_app_error
from app.database import get_db
from app.models.user import User

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> str:
    settings = get_settings()
    credentials_exception = AppError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        code="INVALID_TOKEN",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        return subject
    except JWTError as exc:
        raise credentials_exception from exc


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    subject = verify_access_token(token)
    try:
        user_id = int(subject)
    except ValueError as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            code="INVALID_TOKEN_SUBJECT",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise_app_error(
            status.HTTP_401_UNAUTHORIZED,
            "User not found",
            "USER_NOT_FOUND",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise_app_error(status.HTTP_403_FORBIDDEN, "Inactive user", "INACTIVE_USER")
    return user