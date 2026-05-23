from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from backend.app.database.sa_models import Interview, Candidate, Job


def schedule_interview(
    db: Session, company_id: str, data: dict
) -> Interview:
    candidate = db.query(Candidate).filter(
        Candidate.id == data["candidate_id"],
        Candidate.company_id == company_id,
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    job = db.query(Job).filter(
        Job.id == data["job_id"],
        Job.company_id == company_id,
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        scheduled = datetime.fromisoformat(data["scheduled_time"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO 8601.")

    existing = db.query(Interview).filter(
        Interview.scheduled_time == scheduled,
        Interview.company_id == company_id,
        Interview.status != "cancelled",
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Time slot already booked")

    interview = Interview(
        company_id=company_id,
        candidate_id=data["candidate_id"],
        job_id=data["job_id"],
        scheduled_time=scheduled,
        duration_minutes=data.get("duration_minutes", 60),
        notes=data.get("notes", ""),
        status="scheduled",
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def update_interview(
    db: Session, company_id: str, interview_id: int, data: dict
) -> Interview:
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.company_id == company_id,
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if "scheduled_time" in data and data["scheduled_time"] is not None:
        try:
            new_time = datetime.fromisoformat(data["scheduled_time"])
            data["scheduled_time"] = new_time

            existing = db.query(Interview).filter(
                Interview.scheduled_time == new_time,
                Interview.company_id == company_id,
                Interview.id != interview_id,
                Interview.status != "cancelled",
            ).first()
            if existing:
                raise HTTPException(status_code=409, detail="Time slot already booked")
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid datetime format")

    for key, val in data.items():
        if val is not None and hasattr(interview, key):
            setattr(interview, key, val)
    interview.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(interview)
    return interview


def list_interviews(
    db: Session, company_id: str, status: str = None, candidate_id: int = None
) -> List[dict]:
    q = db.query(Interview).filter(Interview.company_id == company_id)
    if status:
        q = q.filter(Interview.status == status)
    if candidate_id:
        q = q.filter(Interview.candidate_id == candidate_id)
    interviews = q.order_by(Interview.scheduled_time).all()

    result = []
    for i in interviews:
        candidate_name = ""
        job_title = ""
        if i.candidate:
            candidate_name = i.candidate.name
        if i.job:
            job_title = i.job.title
        result.append({
            "id": i.id,
            "candidate_id": i.candidate_id,
            "job_id": i.job_id,
            "scheduled_time": i.scheduled_time.isoformat(),
            "duration_minutes": i.duration_minutes,
            "status": i.status,
            "notes": i.notes,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "created_at": i.created_at.isoformat() if i.created_at else "",
            "updated_at": i.updated_at.isoformat() if i.updated_at else "",
        })
    return result


def get_interview(db: Session, company_id: str, interview_id: int) -> Optional[dict]:
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.company_id == company_id,
    ).first()
    if not interview:
        return None
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "job_id": interview.job_id,
        "scheduled_time": interview.scheduled_time.isoformat(),
        "duration_minutes": interview.duration_minutes,
        "status": interview.status,
        "notes": interview.notes,
        "candidate_name": interview.candidate.name if interview.candidate else "",
        "job_title": interview.job.title if interview.job else "",
        "created_at": interview.created_at.isoformat() if interview.created_at else "",
        "updated_at": interview.updated_at.isoformat() if interview.updated_at else "",
    }
