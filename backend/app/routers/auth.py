import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import raise_app_error
from app.database import get_db
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.services.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger("careeros_api.auth")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@router.post("/register", response_model=CurrentUserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    email = _normalize_email(payload.email)
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        logger.info("Register rejected: duplicate email", extra={"email": email})
        raise_app_error(status.HTTP_409_CONFLICT, "Email is already registered", "EMAIL_ALREADY_REGISTERED")

    user = User(email=email, full_name=payload.full_name.strip(), hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("User registered", extra={"user_id": user.id, "email": user.email})
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = _normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        logger.warning("Login failed", extra={"email": email})
        raise_app_error(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid email or password",
            "INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        logger.warning("Login rejected: inactive user", extra={"user_id": user.id})
        raise_app_error(status.HTTP_403_FORBIDDEN, "Inactive user", "INACTIVE_USER")

    access_token = create_access_token(subject=str(user.id))
    logger.info("Login succeeded", extra={"user_id": user.id})
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user