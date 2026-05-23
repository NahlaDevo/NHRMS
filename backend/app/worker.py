import asyncio
import sys
from typing import Optional

from backend.app.config import settings
from backend.app.utils.helpers import logger


async def score_cv_task(ctx, cv_bytes: bytes, job_keywords: Optional[list[str]] = None):
    from backend.app.ats.ai_scoring import extract_text_from_pdf, score_cv
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: score_cv(extract_text_from_pdf(cv_bytes), job_keywords)
    )
    logger.info(f"CV scored: {result['score']}")
    return result


async def generate_payroll_task(ctx, month: str, company_id: str):
    from backend.app.services import payroll_service
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: payroll_service.generate_all_payroll(month)
    )
    logger.info(f"Payroll generated for {month}: {len(result)} records")
    return result


async def send_email_task(ctx, to: str, subject: str, body: str, html_body: Optional[str] = None):
    from backend.app.services.notification_service import send_email
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: send_email(to=to, subject=subject, body=body, html_body=html_body)
    )
    return result


async def startup(ctx):
    logger.info("ARQ worker started — waiting for jobs")


async def shutdown(ctx):
    logger.info("ARQ worker shutting down")


def _build_redis_settings():
    url = settings.REDIS_URL
    if not url:
        logger.warning("REDIS_URL is not set. Worker will idle.")
        return None
    return url


class WorkerSettings:
    functions = [score_cv_task, generate_payroll_task, send_email_task]
    redis_settings = None
    on_startup = startup
    on_shutdown = shutdown
    poll_delay = 1.0
    max_tries = 3
    burst = True


redis_url = _build_redis_settings()
if redis_url:
    WorkerSettings.redis_settings = redis_url
    WorkerSettings.burst = False
else:
    logger.info("REDIS_URL not configured — worker will perform a no-op loop for Render healthchecks")


async def _noop_loop():
    """Idle loop so Render health check passes when no Redis is configured."""
    while True:
        await asyncio.sleep(60)
        logger.debug("Worker idle — no Redis configured")


if __name__ == "__main__":
    if WorkerSettings.redis_settings:
        from arq import create_pool
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(startup(None))
        try:
            from arq.worker import Worker as ARQWorker
            worker = ARQWorker(WorkerSettings)
            loop.run_until_complete(worker.run())
        except KeyboardInterrupt:
            loop.run_until_complete(shutdown(None))
    else:
        asyncio.run(_noop_loop())
