from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from backend.app.database.sa_setup import Base


class TenantMixin:
    company_id = Column(String(50), nullable=False, index=True)


class SaasUser(Base, TenantMixin):
    __tablename__ = "saas_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="EMPLOYEE")
    email = Column(String(200), default="")
    is_active = Column(String(10), default="True")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("username", "company_id", name="uq_username_company"),
    )


class Candidate(Base, TenantMixin):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(50), default="")
    cv_text = Column(Text, default="")
    cv_filename = Column(String(255), default="")
    score = Column(Float, default=0.0)
    status = Column(String(50), default="new")
    skills = Column(Text, default="")
    experience_years = Column(Float, default=0.0)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Job(Base, TenantMixin):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), default="")
    description = Column(Text, default="")
    requirements = Column(Text, default="")
    keywords = Column(Text, default="")
    status = Column(String(50), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidates = relationship("Candidate", backref="job", lazy="select")
    interviews = relationship("Interview", backref="job", lazy="select")


class Interview(Base, TenantMixin):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(50), default="scheduled")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("Candidate", backref="interviews", lazy="select")

    __table_args__ = (
        UniqueConstraint("scheduled_time", "company_id", name="uq_slot_company"),
    )
