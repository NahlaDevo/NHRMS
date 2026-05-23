from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database.sa_setup import get_db
from backend.app.database.dependencies import get_company_id
from backend.app.interviews import service as interview_service
from backend.app.interviews.schemas import InterviewCreate, InterviewUpdate
from backend.app.utils.security import require_permission

router = APIRouter(prefix="/api/interviews", tags=["Interviews"])


@router.post("")
def schedule_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("interview.create")),
):
    return interview_service.schedule_interview(db, company_id, data.model_dump())


@router.put("/{interview_id}")
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("interview.update")),
):
    return interview_service.update_interview(db, company_id, interview_id, data.model_dump(exclude_none=True))


@router.get("")
def list_interviews(
    status: Optional[str] = Query(None),
    candidate_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("interview.read")),
):
    return interview_service.list_interviews(db, company_id, status, candidate_id)


@router.get("/{interview_id}")
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("interview.read")),
):
    result = interview_service.get_interview(db, company_id, interview_id)
    if not result:
        raise HTTPException(status_code=404, detail="Interview not found")
    return result
