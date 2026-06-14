import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.errors import raise_app_error
from app.database import get_db
from app.models.job_description import JobDescription
from app.models.user import User
from app.schemas.job_description import JobDescriptionCreateRequest, JobDescriptionResponse
from app.services.resume_job_matcher import extract_pdf_text, extract_txt_text
from app.services.security import get_current_user
from app.services.storage import build_job_description_storage_path, get_storage_service
from app.services.usage_tracking import EVENT_JD_UPLOADED, track_usage_event

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])
logger = logging.getLogger("careeros_api.job_descriptions")

MAX_JD_FILE_SIZE_BYTES = 5 * 1024 * 1024
JD_UPLOAD_ROOT = Path("uploads/job_descriptions")
SUPPORTED_JD_EXTENSIONS = {".pdf", ".txt"}


def _safe_file_name(file_name: str) -> str:
    name = Path(file_name).name.strip().replace(" ", "_")
    return name or "job-description.txt"


def _get_user_job_description(job_description_id: int, user_id: int, db: Session) -> JobDescription:
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_description_id, JobDescription.user_id == user_id)
        .first()
    )
    if job_description is None:
        raise_app_error(status.HTTP_404_NOT_FOUND, "Job description not found", "JOB_DESCRIPTION_NOT_FOUND")
    return job_description


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
        storage_path=None,
        source_url=payload.source_url,
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    logger.info("Job description created", extra={"user_id": current_user.id, "job_description_id": job_description.id})
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
        logger.warning("JD upload rejected: invalid file type", extra={"user_id": current_user.id, "file_name": original_file_name})
        raise_app_error(
            status.HTTP_400_BAD_REQUEST,
            "Only PDF and TXT job description files are supported",
            "INVALID_FILE_TYPE",
        )

    content_bytes = await file.read(MAX_JD_FILE_SIZE_BYTES + 1)
    if len(content_bytes) > MAX_JD_FILE_SIZE_BYTES:
        logger.warning("JD upload rejected: file too large", extra={"user_id": current_user.id, "file_name": original_file_name})
        raise_app_error(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Job description file must be 5MB or smaller", "FILE_TOO_LARGE")

    stored_file_name = f"{uuid4().hex}-{original_file_name}"
    storage = get_storage_service()
    storage_path_value: str | None = None
    local_storage_path: Path | None = None

    if storage.enabled:
        storage_path_value = build_job_description_storage_path(current_user.id, stored_file_name)
        storage.upload_bytes(storage_path_value, content_bytes, file.content_type or "application/octet-stream")
    else:
        user_upload_dir = JD_UPLOAD_ROOT / f"user_{current_user.id}"
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        local_storage_path = user_upload_dir / stored_file_name
        local_storage_path.write_bytes(content_bytes)
        storage_path_value = local_storage_path.as_posix()

    try:
        if extension == ".pdf":
            extraction_path = _write_temp_pdf_for_extraction(content_bytes) if storage.enabled else local_storage_path
            try:
                extracted_content = extract_pdf_text(str(extraction_path))
            finally:
                if storage.enabled and extraction_path is not None:
                    Path(extraction_path).unlink(missing_ok=True)
        else:
            extracted_content = extract_txt_text(content_bytes)
    except Exception:
        _delete_uploaded_file(storage_path_value)
        logger.exception("JD upload extraction failed", extra={"user_id": current_user.id})
        raise_app_error(status.HTTP_400_BAD_REQUEST, "Could not extract readable text from the uploaded job description file", "TEXT_EXTRACTION_FAILED")

    if not extracted_content.strip():
        _delete_uploaded_file(storage_path_value)
        logger.warning("JD upload rejected: empty extracted text", extra={"user_id": current_user.id})
        raise_app_error(status.HTTP_400_BAD_REQUEST, "Could not extract readable text from the uploaded job description file", "TEXT_EXTRACTION_FAILED")

    clean_title = (title or Path(original_file_name).stem).strip() or Path(original_file_name).stem
    job_description = JobDescription(
        user_id=current_user.id,
        title=clean_title[:255],
        company=(company or "").strip() or None,
        content=extracted_content,
        storage_path=storage_path_value,
        source_url=(source_url or "").strip() or None,
    )
    db.add(job_description)
    db.commit()
    db.refresh(job_description)
    logger.info("Job description uploaded", extra={"user_id": current_user.id, "job_description_id": job_description.id})
    track_usage_event(
        db,
        user_id=current_user.id,
        event_type=EVENT_JD_UPLOADED,
        metadata={"job_description_id": job_description.id, "file_type": extension.lstrip(".")},
    )
    return job_description


@router.get("/me", response_model=list[JobDescriptionResponse])
def get_my_job_descriptions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[JobDescription]:
    return db.query(JobDescription).filter(JobDescription.user_id == current_user.id).order_by(JobDescription.created_at.desc()).all()


@router.put("/{job_description_id}", response_model=JobDescriptionResponse)
def update_job_description(
    job_description_id: int,
    payload: JobDescriptionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDescription:
    job_description = _get_user_job_description(job_description_id, current_user.id, db)
    job_description.title = payload.title
    job_description.company = payload.company
    job_description.content = payload.content
    job_description.source_url = payload.source_url
    db.commit()
    db.refresh(job_description)
    logger.info("Job description updated", extra={"user_id": current_user.id, "job_description_id": job_description.id})
    return job_description


@router.delete("/{job_description_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_description(
    job_description_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    job_description = _get_user_job_description(job_description_id, current_user.id, db)
    storage_path = job_description.storage_path
    db.delete(job_description)
    db.commit()
    if storage_path:
        _delete_uploaded_file(storage_path)
    logger.info("Job description deleted", extra={"user_id": current_user.id, "job_description_id": job_description_id})


def _write_temp_pdf_for_extraction(content: bytes) -> Path:
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        return Path(temp_file.name)


def _delete_uploaded_file(path_value: str | None) -> None:
    if not path_value:
        return
    try:
        path = Path(path_value)
        if not path.exists():
            storage = get_storage_service()
            if storage.enabled:
                storage.delete_object(path_value)
            return
        resolved_path = path.resolve()
        upload_root = JD_UPLOAD_ROOT.resolve()
        if _is_relative_to(resolved_path, upload_root) and resolved_path.exists() and resolved_path.is_file():
            resolved_path.unlink()
    except OSError:
        logger.warning("Could not delete invalid JD upload file")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
