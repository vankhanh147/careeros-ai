import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.errors import raise_app_error
from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeAccessUrlResponse, ResumeResponse
from app.services.security import get_current_user
from app.services.storage import build_resume_storage_path, get_storage_service
from app.services.usage_tracking import EVENT_RESUME_UPLOADED, track_usage_event

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
logger = logging.getLogger("careeros_api.resumes")

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024
UPLOAD_ROOT = Path("uploads/resumes")
RESUME_ACCESS_URL_EXPIRES_IN_SECONDS = 300


def _safe_file_name(file_name: str) -> str:
    name = Path(file_name).name.strip().replace(" ", "_")
    return name or "resume.pdf"


def _get_user_resume(resume_id: int, user_id: int, db: Session) -> Resume:
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    if resume is None:
        raise_app_error(status.HTTP_404_NOT_FOUND, "Resume not found", "RESUME_NOT_FOUND")
    return resume


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    original_file_name = _safe_file_name(file.filename or "resume.pdf")
    if not original_file_name.lower().endswith(".pdf"):
        logger.warning("Resume upload rejected: invalid file type", extra={"user_id": current_user.id, "file_name": original_file_name})
        raise_app_error(status.HTTP_400_BAD_REQUEST, "Only PDF files are allowed", "INVALID_FILE_TYPE")

    content = await file.read(MAX_RESUME_SIZE_BYTES + 1)
    if len(content) > MAX_RESUME_SIZE_BYTES:
        logger.warning("Resume upload rejected: file too large", extra={"user_id": current_user.id, "file_name": original_file_name})
        raise_app_error(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Resume PDF must be 5MB or smaller", "FILE_TOO_LARGE")

    stored_file_name = f"{uuid4().hex}-{original_file_name}"
    storage = get_storage_service()
    if storage.enabled:
        storage_path_value = build_resume_storage_path(current_user.id, stored_file_name)
        storage.upload_bytes(storage_path_value, content, "application/pdf")
    else:
        user_upload_dir = UPLOAD_ROOT / f"user_{current_user.id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        storage_path = user_upload_dir / stored_file_name
        storage_path.write_bytes(content)
        storage_path_value = storage_path.as_posix()

    resume = Resume(
        user_id=current_user.id,
        file_name=original_file_name,
        storage_path=storage_path_value,
        file_url=None,
        extracted_text=None,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    logger.info("Resume uploaded", extra={"user_id": current_user.id, "resume_id": resume.id})
    track_usage_event(db, user_id=current_user.id, event_type=EVENT_RESUME_UPLOADED, metadata={"resume_id": resume.id})
    return resume


@router.get("/me", response_model=list[ResumeResponse])
def get_my_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Resume]:
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}/access-url", response_model=ResumeAccessUrlResponse)
def get_resume_access_url(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeAccessUrlResponse:
    resume = _get_user_resume(resume_id, current_user.id, db)
    if not resume.storage_path.strip():
        raise_app_error(
            status.HTTP_409_CONFLICT,
            "CV chưa có đường dẫn lưu trữ hợp lệ.",
            "RESUME_STORAGE_PATH_MISSING",
        )

    storage = get_storage_service()
    if not storage.enabled:
        raise_app_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Chưa thể tạo liên kết xem CV trong môi trường lưu trữ hiện tại.",
            "RESUME_ACCESS_UNAVAILABLE",
        )

    try:
        access_url = storage.create_signed_url(
            resume.storage_path,
            RESUME_ACCESS_URL_EXPIRES_IN_SECONDS,
        )
    except (RuntimeError, ValueError):
        logger.exception(
            "Could not create resume signed URL",
            extra={"user_id": current_user.id, "resume_id": resume.id},
        )
        raise_app_error(
            status.HTTP_502_BAD_GATEWAY,
            "Không thể tạo liên kết xem CV. Vui lòng thử lại.",
            "RESUME_ACCESS_URL_FAILED",
        )

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=RESUME_ACCESS_URL_EXPIRES_IN_SECONDS)
    logger.info(
        "Resume access URL created",
        extra={"user_id": current_user.id, "resume_id": resume.id},
    )
    return ResumeAccessUrlResponse(
        resume_id=resume.id,
        access_url=access_url,
        expires_in_seconds=RESUME_ACCESS_URL_EXPIRES_IN_SECONDS,
        expires_at=expires_at,
        storage_provider="supabase",
        download_filename=resume.file_name,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    resume = _get_user_resume(resume_id, current_user.id, db)
    storage_path = resume.storage_path
    db.delete(resume)
    db.commit()
    _delete_resume_file(storage_path, current_user.id, resume_id)
    logger.info("Resume deleted", extra={"user_id": current_user.id, "resume_id": resume_id})


def _delete_resume_file(storage_path_value: str, user_id: int, resume_id: int) -> None:
    storage_path = Path(storage_path_value)
    if storage_path.exists():
        _delete_local_resume_file(storage_path, user_id, resume_id)
        return

    storage = get_storage_service()
    if storage.enabled:
        storage.delete_object(storage_path_value)


def _delete_local_resume_file(storage_path: Path, user_id: int, resume_id: int) -> None:
    upload_root = UPLOAD_ROOT.resolve()
    resolved_path = storage_path.resolve()
    if not _is_relative_to(resolved_path, upload_root):
        logger.warning("Skipped resume file delete outside upload root", extra={"user_id": user_id, "resume_id": resume_id})
        return
    if resolved_path.exists() and resolved_path.is_file():
        resolved_path.unlink()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
