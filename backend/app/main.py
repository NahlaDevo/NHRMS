from fastapi import FastAPI, Request, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.app.config import settings
from backend.app.routes import auth, employees, analytics, admin, attendance, payroll
from backend.app.ats.routes import router as ats_router
from backend.app.interviews.routes import router as interview_router
from backend.app.notifications.routes import router as notification_router
from backend.app.database.sa_setup import init_db, engine
from backend.app.utils.helpers import logger
from backend.app.utils.security import decode_access_token, normalize_role, get_current_user
from backend.app.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from backend.app.middleware import RequestLoggingMiddleware, GlobalExceptionMiddleware


connected_websockets: dict[str, list[WebSocket]] = {}

limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Nahla HR Management System API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        contact={"name": "NHRMS Team"},
    )

    init_db()

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(422, validation_exception_handler)
    app.add_exception_handler(500, unhandled_exception_handler)

    if settings.SENTRY_DSN:
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=float(settings.SENTRY_TRACES_SAMPLE_RATE),
            )
            logger.info("Sentry initialized")
        except Exception as e:
            logger.warning("Failed to init Sentry: %s", e)

    # Middleware order matters: outermost runs first
    app.add_middleware(GlobalExceptionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    app.include_router(auth.router)
    app.include_router(employees.router)
    app.include_router(analytics.router)
    app.include_router(admin.router)
    app.include_router(attendance.router)
    app.include_router(payroll.router)
    app.include_router(ats_router)
    app.include_router(interview_router)
    app.include_router(notification_router)

    return app


app = create_app()


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if not settings.DEBUG:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            payload = decode_access_token(token)
            request.state.user = {
                "username": payload.get("sub"),
                "role": normalize_role(payload.get("role", "EMPLOYEE")),
                "user_id": payload.get("user_id", ""),
            }
        except Exception:
            pass
    return await call_next(request)


try:
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# ── File Serving ──────────────────────────────────────────────────


@app.get("/api/uploads/{company_id}/{entity_type}/{filename}")
async def serve_upload(
    company_id: str,
    entity_type: str,
    filename: str,
    _: dict = Depends(get_current_user),
):
    file_path = settings.UPLOAD_DIR / company_id / entity_type / filename
    if not file_path.exists():
        return JSONResponse({"detail": "File not found"}, status_code=404)
    return FileResponse(str(file_path))


# ── WebSocket for real-time notifications ─────────────────────────


@app.websocket("/ws/notifications/{user_id}")
async def notification_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    if user_id not in connected_websockets:
        connected_websockets[user_id] = []
    connected_websockets[user_id].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets[user_id].remove(websocket)


# ── Health & SPA ──────────────────────────────────────────────────


@app.get("/api/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(conn.default_schema_name)
            conn.close()
        db_ok = True
    except Exception as exc:
        logger.warning("Health check DB failure: %s", exc)
    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def serve_spa():
    index_path = settings.STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/api/docs",
        "version": settings.VERSION,
    }


@app.api_route("/{path:path}", methods=["GET"], include_in_schema=False)
async def spa_fallback(path: str):
    excluded = ("api/", "static/", "docs/", "openapi.json", "redoc")
    if path.startswith(excluded):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    index_path = settings.STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"detail": "Not Found"}, status_code=404)
