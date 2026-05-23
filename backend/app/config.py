import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "Nahla HR Management System"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "backend" / "static"
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    BACKUP_DIR: Path = BASE_DIR / "backups"

    EXCEL_FILE: str = str(DATA_DIR / "employee_records.xlsx")
    EXCEL_SHEET_NAME: str = "Employees"
    USERS_EXCEL_FILE: str = str(DATA_DIR / "users.xlsx")
    USERS_SHEET_NAME: str = "Users"

    ATTENDANCE_EXCEL_FILE: str = str(DATA_DIR / "attendance.xlsx")
    ATTENDANCE_SHEET_NAME: str = "Attendance"
    PAYROLL_EXCEL_FILE: str = str(DATA_DIR / "payroll.xlsx")
    PAYROLL_SHEET_NAME: str = "Payroll"

    # Payroll defaults
    STANDARD_MONTHLY_HOURS: float = 160.0
    OVERTIME_RATE_MULTIPLIER: float = 1.5
    DEFAULT_BASE_SALARY: float = 10000.0

    # Attendance rules
    AUTO_CLOSE_HOUR: int = 23
    AUTO_CLOSE_MINUTE: int = 59
    WEEKEND_DAYS: list = [5, 6]  # Saturday=5, Sunday=6
    HOLIDAYS: list = []  # populate as ["2026-01-01", "2026-12-25"]

    # Late threshold (minutes after 9:00 AM)
    LATE_THRESHOLD_MINUTES: int = 15
    STANDARD_START_HOUR: int = 9
    STANDARD_START_MINUTE: int = 0
    LATE_DEDUCTION_PER_HOUR: float = 50.0
    MISSING_DAY_DEDUCTION: float = 200.0

    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx"}
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent.parent.parent}/data/saas.db",
    )
    SAAS_DATABASE_URL: str = DATABASE_URL  # backward compat

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,.onrender.com").split(",")

    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,https://nhrms-api.onrender.com,https://nhrms-frontend.onrender.com"
    ).split(",")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://nhrms-frontend.onrender.com")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.BACKUP_DIR.mkdir(exist_ok=True)
settings.DATA_DIR.mkdir(exist_ok=True)
