import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.notifications.models import Notification
from backend.app.utils.helpers import logger


def create_notification(
    db: Session,
    company_id: str,
    user_id: str,
    title: str,
    message: str,
    type: str = "info",
    link: str = "",
):
    notif = Notification(
        company_id=company_id,
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    try:
        import asyncio
        from backend.app.notifications.websocket import broadcast_notification
        asyncio.create_task(broadcast_notification(user_id, {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "type": notif.type,
            "link": notif.link,
            "created_at": str(notif.created_at),
        }))
    except Exception:
        pass

    return notif


def list_notifications(
    db: Session,
    company_id: str,
    user_id: str,
    unread_only: bool = False,
):
    q = db.query(Notification).filter(
        Notification.company_id == company_id,
        Notification.user_id == user_id,
    )
    if unread_only:
        q = q.filter(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc()).limit(50)
    return q.all()


def mark_read(
    db: Session,
    notification_id: int,
    company_id: str,
    user_id: str,
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.company_id == company_id,
        Notification.user_id == user_id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()


def mark_all_read(
    db: Session,
    company_id: str,
    user_id: str,
):
    result = db.query(Notification).filter(
        Notification.company_id == company_id,
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return result


def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
):
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    if not smtp_server:
        logger.warning(f"SMTP not configured; skipping email to {to}")
        return {"sent": False, "reason": "SMTP not configured"}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to

    msg.attach(MIMEText(body, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [to], msg.as_string())
        logger.info(f"Email sent to {to}: {subject}")
        return {"sent": True}
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return {"sent": False, "reason": str(e)}
