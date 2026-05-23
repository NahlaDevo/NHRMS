import asyncio
from typing import Optional

from backend.app.config import settings
from backend.app.utils.helpers import logger


async def score_cv_task(ctx, cv_bytes: bytes, job_keywords: Optional[list[str]] = None):
    """Async CV scoring — runs the AI scorer in the background."""
    from backend.app.ats.ai_scoring import extract_text_from_pdf, score_cv

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: score_cv(extract_text_from_pdf(cv_bytes), job_keywords)
    )
    logger.info(f"CV scored: {result['score']}")
    return result


async def generate_payroll_task(ctx, month: str, company_id: str):
    """Async bulk payroll generation."""
    from backend.app.services import payroll_service

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: payroll_service.generate_all_payroll(month)
    )
    logger.info(f"Payroll generated for {month}: {len(result)} records")
    return result


async def send_email_task(
    ctx,
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
):
    """Send email asynchronously."""
    from backend.app.services.notification_service import send_email

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: send_email(to=to, subject=subject, body=body, html_body=html_body)
    )
    return result


async def startup(ctx):
    logger.info("ARQ worker started")


async def shutdown(ctx):
    logger.info("ARQ worker shutting down")


class WorkerSettings:
    functions = [score_cv_task, generate_payroll_task, send_email_task]
    redis_settings = settings.REDIS_URL
    on_startup = startup
    on_shutdown = shutdown
    poll_delay = 1.0
    max_tries = 3
