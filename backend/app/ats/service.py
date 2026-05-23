from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from backend.app.database.sa_models import Job, Candidate, Interview, TenantMixin
from backend.app.ats.ai_scoring import extract_text_from_pdf
from backend.app.ats.llm_adapter import score_cv_with_llm as score_cv


def create_job(db: Session, company_id: str, data: dict) -> Job:
    job = Job(
        company_id=company_id,
        title=data["title"],
        department=data.get("department", ""),
        description=data.get("description", ""),
        requirements=data.get("requirements", ""),
        keywords=data.get("keywords", ""),
        status=data.get("status", "open"),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, company_id: str, job_id: int, data: dict) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == company_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, val in data.items():
        if val is not None and hasattr(job, key):
            setattr(job, key, val)
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, company_id: str, job_id: int) -> Optional[Job]:
    return db.query(Job).filter(Job.id == job_id, Job.company_id == company_id).first()


def list_jobs(db: Session, company_id: str, status: str = None) -> List[Job]:
    q = db.query(Job).filter(Job.company_id == company_id)
    if status:
        q = q.filter(Job.status == status)
    return q.order_by(desc(Job.created_at)).all()


def delete_job(db: Session, company_id: str, job_id: int):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == company_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()


def upload_and_score_cv(
    db: Session,
    company_id: str,
    name: str,
    email: str,
    file: UploadFile,
    job_id: Optional[int] = None,
) -> dict:
    file_bytes = file.file.read()
    cv_text = extract_text_from_pdf(file_bytes)

    from pathlib import Path
    from backend.app.config import settings
    cv_dir = settings.UPLOAD_DIR / company_id / "cvs"
    cv_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    cv_path = cv_dir / safe_name
    cv_path.write_bytes(file_bytes)
    job_keywords = []
    if job_id:
        job = db.query(Job).filter(Job.id == job_id, Job.company_id == company_id).first()
        if job and job.keywords:
            job_keywords = [k.strip() for k in job.keywords.split(",") if k.strip()]

    score_result = score_cv(cv_text, job_keywords)

    candidate = Candidate(
        company_id=company_id,
        name=name,
        email=email,
        cv_text=cv_text[:50000],
        cv_filename=safe_name,
        score=score_result["score"],
        status="new",
        skills=", ".join(score_result["skills"][:20]),
        experience_years=score_result["experience_years"],
        job_id=job_id,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return {
        "candidate": candidate,
        "score_result": score_result,
    }


def update_candidate(db: Session, company_id: str, candidate_id: int, data: dict) -> Candidate:
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.company_id == company_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    for key, val in data.items():
        if val is not None and hasattr(candidate, key):
            setattr(candidate, key, val)
    candidate.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(candidate)
    return candidate


def list_candidates(
    db: Session, company_id: str, status: str = None, job_id: int = None
) -> List[Candidate]:
    q = db.query(Candidate).filter(Candidate.company_id == company_id)
    if status:
        q = q.filter(Candidate.status == status)
    if job_id:
        q = q.filter(Candidate.job_id == job_id)
    return q.order_by(desc(Candidate.score)).all()


def get_candidate(db: Session, company_id: str, candidate_id: int) -> Optional[Candidate]:
    return db.query(Candidate).filter(
        Candidate.id == candidate_id, Candidate.company_id == company_id
    ).first()


def get_dashboard_stats(db: Session, company_id: str) -> dict:
    jobs = db.query(Job).filter(Job.company_id == company_id).all()
    candidates = db.query(Candidate).filter(Candidate.company_id == company_id).all()
    interviews = db.query(Interview).filter(Interview.company_id == company_id).all()

    return {
        "total_jobs": len(jobs),
        "open_jobs": sum(1 for j in jobs if j.status == "open"),
        "total_candidates": len(candidates),
        "avg_score": round(
            sum(c.score for c in candidates) / len(candidates), 2
        ) if candidates else 0.0,
        "status_breakdown": {
            s: sum(1 for c in candidates if c.status == s)
            for s in set(c.status for c in candidates)
        },
        "scheduled_interviews": sum(1 for i in interviews if i.status == "scheduled"),
    }
