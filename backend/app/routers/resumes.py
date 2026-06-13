from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.security import get_current_user

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024
UPLOAD_ROOT = Path("uploads/resumes")


def _safe_file_name(file_name: str) -> str:
    name = Path(file_name).name.strip().replace(" ", "_")
    return name or "resume.pdf"


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resume:
    original_file_name = _safe_file_name(file.filename or "resume.pdf")
    if not original_file_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    content = await file.read(MAX_RESUME_SIZE_BYTES + 1)
    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume PDF must be 5MB or smaller",
        )

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
    return resume


@router.get("/me", response_model=list[ResumeResponse])
def get_my_resumes(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )
