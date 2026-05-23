from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from backend.app.database.sa_setup import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    link = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
