from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.job_description import JobDescriptionCreateRequest, JobDescriptionResponse
from app.services.resume_job_matcher import extract_pdf_text, extract_txt_text
from app.services.security import get_current_user

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])

MAX_JD_FILE_SIZE_BYTES = 5 * 1024 * 1024
JD_UPLOAD_ROOT = Path("uploads/job_descriptions")
SUPPORTED_JD_EXTENSIONS = {".pdf", ".txt"}


def _safe_file_name(file_name: str) -> str:
    name = Path(file_name).name.strip().replace(" ", "_")
    return name or "job-description.txt"


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    payload: JobDescriptionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescription:
    job_description = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        company=payload.company,
        content=payload.content,
        source_url=payload.source_url,
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    return job_description


@router.post("/upload", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def upload_job_description(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    company: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescription:
    original_file_name = _safe_file_name(file.filename or "job-description.txt")
    extension = Path(original_file_name).suffix.lower()
    if extension not in SUPPORTED_JD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and TXT job description files are supported in this MVP phase",
        )

    content_bytes = await file.read(MAX_JD_FILE_SIZE_BYTES + 1)
    if len(content_bytes) > MAX_JD_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Job description file must be 5MB or smaller",
        )

    user_upload_dir = JD_UPLOAD_ROOT / f"user_{current_user.id}"
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    stored_file_name = f"{uuid4().hex}_{original_file_name}"
    storage_path = user_upload_dir / stored_file_name
    storage_path.write_bytes(content_bytes)

    if extension == ".pdf":
        extracted_content = extract_pdf_text(storage_path.as_posix())
    else:
        extracted_content = extract_txt_text(content_bytes)

    if not extracted_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract readable text from the uploaded job description file",
        )

    clean_title = (title or Path(original_file_name).stem).strip() or Path(original_file_name).stem
    job_description = JobDescription(
        user_id=current_user.id,
        title=clean_title[:255],
        company=(company or "").strip() or None,
        content=extracted_content,
        source_url=(source_url or "").strip() or None,
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    return job_description


@router.get("/me", response_model=list[JobDescriptionResponse])
def get_my_job_descriptions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[JobDescription]:
    return (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )