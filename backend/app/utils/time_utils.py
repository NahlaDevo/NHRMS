from datetime import datetime, date, time, timedelta
from typing import Optional, Tuple
from backend.app.config import settings


def now_utc() -> datetime:
    return datetime.utcnow()


def today_str() -> str:
    return now_utc().date().isoformat()


def is_weekend(d: Optional[date] = None) -> bool:
    if d is None:
        d = now_utc().date()
    return d.weekday() in settings.WEEKEND_DAYS


def is_holiday(d: Optional[date] = None) -> bool:
    if d is None:
        d = now_utc().date()
    return d.isoformat() in settings.HOLIDAYS


def is_working_day(d: Optional[date] = None) -> bool:
    return not is_weekend(d) and not is_holiday(d)


def is_late(check_in_dt: datetime) -> Tuple[bool, int]:
    start = check_in_dt.replace(
        hour=settings.STANDARD_START_HOUR,
        minute=settings.STANDARD_START_MINUTE,
        second=0, microsecond=0,
    )
    if check_in_dt <= start:
        return False, 0
    late_minutes = int((check_in_dt - start).total_seconds() / 60)
    return late_minutes > settings.LATE_THRESHOLD_MINUTES, late_minutes


def auto_close_datetime(check_in_dt: datetime) -> datetime:
    return check_in_dt.replace(
        hour=settings.AUTO_CLOSE_HOUR,
        minute=settings.AUTO_CLOSE_MINUTE,
        second=0, microsecond=0,
    )


def compute_hours_worked(check_in: datetime, check_out: datetime) -> float:
    delta = check_out - check_in
    total = delta.total_seconds() / 3600
    return round(max(total, 0), 2)


def calculate_deductions(
    employee_id: str,
    month: str,
    attendance_df,
    late_deduction_rate: float = settings.LATE_DEDUCTION_PER_HOUR,
    missing_day_deduction: float = settings.MISSING_DAY_DEDUCTION,
) -> float:
    total_deductions = 0.0
    for _, row in attendance_df.iterrows():
        status = str(row.get("status", "Present"))
        if status == "Late":
            check_in = row.get("check_in", "")
            if check_in:
                try:
                    ci = datetime.fromisoformat(str(check_in))
                    _, late_mins = is_late(ci)
                    total_deductions += round((late_mins / 60) * late_deduction_rate, 2)
                except (ValueError, TypeError):
                    pass
        elif status == "Absent":
            total_deductions += missing_day_deduction
    return round(total_deductions, 2)
