import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import AppError, raise_app_error
from app.database import get_db
from app.models.career_profile import CareerProfile
from app.models.interview import InterviewAnswer, InterviewSession
from app.models.learning_roadmap import LearningRoadmap
from app.models.match_analysis import MatchAnalysis
from app.models.user import User
from app.schemas.interview import InterviewAnswerRequest, InterviewSessionResponse, InterviewStartRequest
from app.services.interview_evaluator import build_session_summary, evaluate_interview_answer
from app.services.interview_generator import generate_interview_questions, infer_target_role
from app.services.resume_job_matcher import analyze_resume_job_match
from app.services.security import get_current_user
from app.services.usage_tracking import EVENT_INTERVIEW_COMPLETED, EVENT_INTERVIEW_STARTED, track_usage_event

router = APIRouter(prefix="/api/interviews", tags=["interviews"])
logger = logging.getLogger("careeros_api.interviews")


@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def start_interview_session(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    profile = db.query(CareerProfile).filter(CareerProfile.user_id == current_user.id).first()
    analysis = _get_user_analysis(db, current_user.id, payload.analysis_id) if payload.analysis_id else None
    target_role = infer_target_role(profile, payload.target_role)
    missing_skills = _load_missing_skills(analysis) if analysis else []
    analysis_context = _build_analysis_context(analysis) if analysis else {}
    roadmap_items = _load_latest_roadmap_items(db, current_user.id, analysis.id if analysis else None)

    try:
        questions = generate_interview_questions(target_role, missing_skills=missing_skills, roadmap_items=roadmap_items, analysis_context=analysis_context)
        session = InterviewSession(user_id=current_user.id, analysis_id=analysis.id if analysis else None, target_role=target_role, status="in_progress")
        db.add(session)
        db.flush()

        for item in questions:
            db.add(
                InterviewAnswer(
                    session_id=session.id,
                    question=str(item["question"]),
                    expected_keywords=json.dumps(_question_payload(item), ensure_ascii=False),
                )
            )

        db.commit()
        db.refresh(session)
        logger.info("Interview session started", extra={"user_id": current_user.id, "session_id": session.id})
        track_usage_event(
            db,
            user_id=current_user.id,
            event_type=EVENT_INTERVIEW_STARTED,
            metadata={"session_id": session.id, "analysis_id": session.analysis_id, "target_role": session.target_role},
        )
        return _to_response(session)
    except Exception as exc:
        logger.exception("Interview start failed", extra={"user_id": current_user.id, "analysis_id": payload.analysis_id})
        raise AppError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not start interview session", code="INTERVIEW_START_FAILED") from exc


@router.get("/me", response_model=list[InterviewSessionResponse])
def get_my_interviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[InterviewSessionResponse]:
    sessions = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).order_by(InterviewSession.created_at.desc()).limit(20).all()
    return [_to_response(session) for session in sessions]


@router.get("/{session_id}", response_model=InterviewSessionResponse)
def get_interview_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InterviewSessionResponse:
    session = _get_user_session(db, current_user.id, session_id)
    return _to_response(session)


@router.post("/{session_id}/answer", response_model=InterviewSessionResponse)
def answer_interview_question(
    session_id: int,
    payload: InterviewAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InterviewSessionResponse:
    session = _get_user_session(db, current_user.id, session_id)
    if session.status == "finished":
        raise_app_error(status.HTTP_400_BAD_REQUEST, "Interview session already finished", "INTERVIEW_ALREADY_FINISHED")

    answer = next((item for item in session.answers if item.id == payload.answer_id), None)
    if answer is None:
        raise_app_error(status.HTTP_404_NOT_FOUND, "Interview question not found", "INTERVIEW_QUESTION_NOT_FOUND")

    try:
        expected_keywords = _load_keywords(answer.expected_keywords)
        evaluation = evaluate_interview_answer(answer.question, expected_keywords, payload.user_answer)
        answer.user_answer = payload.user_answer.strip()
        answer.score = float(evaluation["score"])
        answer.feedback = str(evaluation["feedback"])
        db.commit()
        db.refresh(session)
        logger.info("Interview answer evaluated", extra={"user_id": current_user.id, "session_id": session.id, "answer_id": answer.id})
        return _to_response(session)
    except Exception as exc:
        logger.exception("Interview answer evaluation failed", extra={"user_id": current_user.id, "session_id": session.id, "answer_id": payload.answer_id})
        raise AppError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not evaluate interview answer", code="INTERVIEW_ANSWER_FAILED") from exc


@router.post("/{session_id}/finish", response_model=InterviewSessionResponse)
def finish_interview_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> InterviewSessionResponse:
    session = _get_user_session(db, current_user.id, session_id)
    answered_scores = [float(answer.score) for answer in session.answers if answer.score is not None]
    if not answered_scores:
        logger.warning("Interview finish rejected: no answered questions", extra={"user_id": current_user.id, "session_id": session.id})
        raise_app_error(status.HTTP_400_BAD_REQUEST, "Answer at least one question before finishing the interview", "INTERVIEW_NO_ANSWERS")

    try:
        session.score = round(sum(answered_scores) / len(answered_scores), 1)
        session.summary = build_session_summary(answered_scores)
        session.status = "finished"
        db.commit()
        db.refresh(session)
        logger.info("Interview session finished", extra={"user_id": current_user.id, "session_id": session.id})
        track_usage_event(
            db,
            user_id=current_user.id,
            event_type=EVENT_INTERVIEW_COMPLETED,
            metadata={"session_id": session.id, "question_count": len(session.answers), "score": session.score},
        )
        return _to_response(session)
    except Exception as exc:
        logger.exception("Interview finish failed", extra={"user_id": current_user.id, "session_id": session.id})
        raise AppError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not finish interview session", code="INTERVIEW_FINISH_FAILED") from exc


def _get_user_session(db: Session, user_id: int, session_id: int) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id).first()
    if session is None:
        raise_app_error(status.HTTP_404_NOT_FOUND, "Interview session not found", "INTERVIEW_SESSION_NOT_FOUND")
    return session


def _get_user_analysis(db: Session, user_id: int, analysis_id: int | None) -> MatchAnalysis:
    analysis = db.query(MatchAnalysis).filter(MatchAnalysis.id == analysis_id, MatchAnalysis.user_id == user_id).first()
    if analysis is None:
        logger.warning("Interview rejected: analysis not found", extra={"user_id": user_id, "analysis_id": analysis_id})
        raise_app_error(status.HTTP_404_NOT_FOUND, "Analysis not found", "ANALYSIS_NOT_FOUND")
    return analysis


def _to_response(session: InterviewSession) -> InterviewSessionResponse:
    return InterviewSessionResponse(
        id=session.id,
        user_id=session.user_id,
        analysis_id=session.analysis_id,
        target_role=session.target_role,
        status=session.status,
        score=session.score,
        summary=session.summary,
        answers=[
            {
                "id": answer.id,
                "session_id": answer.session_id,
                "question": answer.question,
                "expected_keywords": _load_keywords(answer.expected_keywords),
                "question_reason": _load_question_metadata(answer.expected_keywords).get("reason"),
                "related_skills": _load_question_metadata(answer.expected_keywords).get("related_skills", []),
                "question_category": _load_question_metadata(answer.expected_keywords).get("category"),
                "better_answer_hint": _load_question_metadata(answer.expected_keywords).get("better_answer_hint"),
                "user_answer": answer.user_answer,
                "score": answer.score,
                "feedback": answer.feedback,
                "feedback_category": _extract_feedback_category(answer.feedback),
                "created_at": answer.created_at,
            }
            for answer in session.answers
        ],
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _load_keywords(value: str) -> list[str]:
    parsed = _load_json(value)
    if isinstance(parsed, dict):
        keywords = parsed.get("keywords", [])
        return [str(item) for item in keywords] if isinstance(keywords, list) else []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def _question_payload(item: dict[str, object]) -> dict[str, object]:
    return {
        "keywords": [str(keyword) for keyword in item.get("keywords", [])],
        "reason": str(item.get("reason", "")),
        "related_skills": [str(skill) for skill in item.get("related_skills", [])],
        "category": str(item.get("category", "")),
        "better_answer_hint": str(item.get("better_answer_hint", "")),
        "stack_group": str(item.get("stack_group", "")),
    }


def _load_question_metadata(value: str) -> dict[str, Any]:
    parsed = _load_json(value)
    if not isinstance(parsed, dict):
        return {}
    related_skills = parsed.get("related_skills", [])
    return {
        "reason": str(parsed.get("reason", "")) or None,
        "related_skills": [str(skill) for skill in related_skills] if isinstance(related_skills, list) else [],
        "category": str(parsed.get("category", "")) or None,
        "better_answer_hint": str(parsed.get("better_answer_hint", "")) or None,
        "stack_group": str(parsed.get("stack_group", "")) or None,
    }


def _extract_feedback_category(feedback: str | None) -> str | None:
    if not feedback:
        return None
    marker = "Ph\u00e2n lo\u1ea1i feedback: "
    if marker not in feedback:
        return None
    remainder = feedback.split(marker, 1)[1]
    return remainder.split(".", 1)[0].strip() or None


def _build_analysis_context(analysis: MatchAnalysis | None) -> dict[str, Any]:
    if analysis is None:
        return {}
    try:
        resume_text = analysis.resume.extracted_text if analysis.resume else ""
        jd_text = analysis.job_description.content if analysis.job_description else ""
        result = analyze_resume_job_match(resume_text or "", jd_text or "")
        scoring = result.get("scoring_breakdown", {}) if isinstance(result, dict) else {}
        if not isinstance(scoring, dict):
            scoring = {}
        return {
            "critical_skills": scoring.get("critical_skills", []),
            "role_family": scoring.get("jd_role_family", ""),
            "stack_groups": scoring.get("jd_stack_groups", []),
        }
    except Exception:
        logger.warning("Interview analysis context fallback", extra={"analysis_id": analysis.id})
        return {}


def _load_latest_roadmap_items(db: Session, user_id: int, analysis_id: int | None) -> list[dict[str, Any]]:
    query = db.query(LearningRoadmap).filter(LearningRoadmap.user_id == user_id)
    if analysis_id is not None:
        roadmap = query.filter(LearningRoadmap.analysis_id == analysis_id).order_by(LearningRoadmap.created_at.desc()).first()
        if roadmap is not None:
            return _load_roadmap_items(roadmap.items)
    roadmap = query.order_by(LearningRoadmap.created_at.desc()).first()
    return _load_roadmap_items(roadmap.items) if roadmap else []


def _load_roadmap_items(value: str) -> list[dict[str, Any]]:
    parsed = _load_json(value)
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _load_missing_skills(analysis: MatchAnalysis | None) -> list[str]:
    if analysis is None:
        return []
    parsed = _load_json(analysis.missing_skills)
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed]


def _load_json(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None
