import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.core.errors import raise_app_error
from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.security import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["resumes"])
logger = logging.getLogger("careeros_api.resumes")

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024
UPLOAD_ROOT = Path("uploads/resumes")


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

    user_upload_dir = UPLOAD_ROOT / f"user_{current_user.id}"
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    stored_file_name = f"{uuid4().hex}_{original_file_name}"
    storage_path = user_upload_dir / stored_file_name
    storage_path.write_bytes(content)

    resume = Resume(
        user_id=current_user.id,
        file_name=original_file_name,
        storage_path=storage_path.as_posix(),
        file_url=None,
        extracted_text=None,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    logger.info("Resume uploaded", extra={"user_id": current_user.id, "resume_id": resume.id})
    return resume


@router.get("/me", response_model=list[ResumeResponse])
def get_my_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Resume]:
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    resume = _get_user_resume(resume_id, current_user.id, db)
    storage_path = Path(resume.storage_path)
    db.delete(resume)
    db.commit()
    _delete_local_resume_file(storage_path, current_user.id, resume_id)
    logger.info("Resume deleted", extra={"user_id": current_user.id, "resume_id": resume_id})


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