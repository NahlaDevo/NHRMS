import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from backend.app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.BASE_DIR / "app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(settings.APP_NAME)

def validate_file_extension(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension {ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )
    return True

async def save_upload_file(upload_file: UploadFile, employee_id: str) -> str:
    validate_file_extension(upload_file.filename)
    employee_dir = settings.UPLOAD_DIR / employee_id
    employee_dir.mkdir(exist_ok=True)
    file_path = employee_dir / upload_file.filename
    with open(file_path, "wb") as buffer:
        content = await upload_file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB",
            )
        buffer.write(content)
    logger.info(f"File saved: {file_path}")
    return str(file_path)

def backup_excel(file_path: str) -> str:
    source = Path(file_path)
    if not source.exists():
        return ""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.stem}_backup_{timestamp}{source.suffix}"
    backup_path = settings.BACKUP_DIR / backup_name
    shutil.copy2(source, backup_path)
    logger.info(f"Backup created: {backup_path}")
    return str(backup_path)
