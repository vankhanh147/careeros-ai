import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job_description import JobDescription
from app.models.match_analysis import MatchAnalysis
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import MatchAnalysisResponse, ResumeJobMatchRequest
from app.services.resume_job_matcher import analyze_resume_job_match, extract_pdf_text
from app.services.security import get_current_user

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/resume-job-match", response_model=MatchAnalysisResponse, status_code=status.HTTP_201_CREATED)
def run_resume_job_match(
    payload: ResumeJobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchAnalysisResponse:
    resume = (
        db.query(Resume)
        .filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    job_description = (
        db.query(JobDescription)
        .filter(
            JobDescription.id == payload.job_description_id,
            JobDescription.user_id == current_user.id,
        )
        .first()
    )
    if job_description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    if not resume.extracted_text:
        try:
            resume.extracted_text = extract_pdf_text(resume.storage_path)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume PDF file is missing on storage. Please upload the file again.",
            ) from exc

    result = analyze_resume_job_match(resume.extracted_text or "", job_description.content)
    analysis = MatchAnalysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_description_id=job_description.id,
        match_score=float(result["match_score"]),
        matched_skills=json.dumps(result["matched_skills"], ensure_ascii=False),
        missing_skills=json.dumps(result["missing_skills"], ensure_ascii=False),
        keyword_overlap=json.dumps(result["keyword_overlap"], ensure_ascii=False),
        summary=str(result["summary"]),
        suggestions=json.dumps(result["suggestions"], ensure_ascii=False),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return _to_response(analysis, result)


@router.get("/history", response_model=list[MatchAnalysisResponse])
def get_analysis_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[MatchAnalysisResponse]:
    analyses = (
        db.query(MatchAnalysis)
        .filter(MatchAnalysis.user_id == current_user.id)
        .order_by(MatchAnalysis.created_at.desc())
        .limit(20)
        .all()
    )
    return [_to_response(analysis) for analysis in analyses]


def _load_json_list(value: str) -> list[str]:
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def _to_response(analysis: MatchAnalysis, debug_result: dict[str, object] | None = None) -> MatchAnalysisResponse:
    if debug_result is None:
        resume_text = analysis.resume.extracted_text if analysis.resume else ""
        jd_text = analysis.job_description.content if analysis.job_description else ""
        debug_result = analyze_resume_job_match(resume_text or "", jd_text or "")

    return MatchAnalysisResponse(
        id=analysis.id,
        user_id=analysis.user_id,
        resume_id=analysis.resume_id,
        job_description_id=analysis.job_description_id,
        match_score=analysis.match_score,
        matched_skills=_load_json_list(analysis.matched_skills),
        missing_skills=_load_json_list(analysis.missing_skills),
        keyword_overlap=_load_json_list(analysis.keyword_overlap),
        summary=analysis.summary,
        suggestions=_load_json_list(analysis.suggestions),
        resume_text_preview=str(debug_result["resume_text_preview"]),
        jd_text_preview=str(debug_result["jd_text_preview"]),
        resume_detected_skills=[str(item) for item in debug_result["resume_detected_skills"]],
        jd_detected_skills=[str(item) for item in debug_result["jd_detected_skills"]],
        scoring_breakdown=debug_result["scoring_breakdown"],
        skill_gap_summary=str(debug_result["skill_gap_summary"]),
        prioritized_missing_skills=debug_result["prioritized_missing_skills"],
        improvement_plan=[str(item) for item in debug_result["improvement_plan"]],
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )