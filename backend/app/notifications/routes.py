from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database.sa_setup import get_db
from backend.app.database.dependencies import get_company_id
from backend.app.notifications import service as notification_service
from backend.app.utils.security import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(
    unread_only: Optional[bool] = Query(False),
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    current_user: dict = Depends(get_current_user),
):
    return notification_service.list_notifications(
        db, company_id, current_user["user_id"], unread_only
    )


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    current_user: dict = Depends(get_current_user),
):
    notification_service.mark_read(db, notification_id, company_id, current_user["user_id"])
    return {"message": "Marked as read"}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
    current_user: dict = Depends(get_current_user),
):
    count = notification_service.mark_all_read(db, company_id, current_user["user_id"])
    return {"message": f"Marked {count} notifications as read"}
