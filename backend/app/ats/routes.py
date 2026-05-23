from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database.sa_setup import get_db
from backend.app.database.dependencies import get_company_id
from backend.app.ats import service as ats_service
from backend.app.ats.schemas import (
    JobCreate, JobUpdate, JobResponse,
    CandidateResponse, CandidateUpdate,
)
from backend.app.utils.security import require_permission

router = APIRouter(prefix="/api/ats", tags=["ATS"])


@router.post("/jobs", response_model=JobResponse)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.job.create")),
):
    return ats_service.create_job(db, company_id, data.model_dump())


@router.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    data: JobUpdate,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.job.update")),
):
    return ats_service.update_job(db, company_id, job_id, data.model_dump(exclude_none=True))


@router.get("/jobs", response_model=list[JobResponse])
def list_jobs(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.job.read")),
):
    return ats_service.list_jobs(db, company_id, status)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.job.read")),
):
    return ats_service.get_job(db, company_id, job_id)


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.job.delete")),
):
    ats_service.delete_job(db, company_id, job_id)
    return {"message": "Job deleted"}


@router.post("/candidate/upload")
def upload_cv(
    name: str = Form(...),
    email: str = Form(...),
    job_id: Optional[int] = Form(None),
    cv: UploadFile = File(...),
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.candidate.upload")),
):
    result = ats_service.upload_and_score_cv(db, company_id, name, email, cv, job_id)
    return result


@router.get("/candidates", response_model=list[CandidateResponse])
def list_candidates(
    status: Optional[str] = Query(None),
    job_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.candidate.read")),
):
    return ats_service.list_candidates(db, company_id, status, job_id)


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.candidate.read")),
):
    return ats_service.get_candidate(db, company_id, candidate_id)


@router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    data: CandidateUpdate,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.candidate.update")),
):
    return ats_service.update_candidate(db, company_id, candidate_id, data.model_dump(exclude_none=True))


@router.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    _: dict = Depends(require_permission("ats.dashboard")),
):
    return ats_service.get_dashboard_stats(db, company_id)
