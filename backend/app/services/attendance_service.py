from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from fastapi import HTTPException, status
from backend.app.database.excel_manager import attendance_db, employee_db
from backend.app.utils.helpers import logger
from backend.app.utils.time_utils import (
    now_utc, today_str, is_working_day, is_late,
    auto_close_datetime, compute_hours_worked,
)


def _find_today_row(df: pd.DataFrame, employee_id: str, day: Optional[str] = None) -> Optional[int]:
    if day is None:
        day = today_str()
    mask = (df["employee_id"].astype(str) == employee_id) & (df["date"] == day)
    matching = df[mask]
    if matching.empty:
        return None
    return matching.index[0]


def check_in(employee_id: str) -> Dict[str, Any]:
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")

    emp = employee_db.find_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    now = now_utc()
    day = today_str()

    if not is_working_day():
        logger.info(f"Check-in attempted on non-working day by {employee_id}")
        # Allow but flag it

    df = attendance_db.read_all()
    existing_idx = _find_today_row(df, employee_id, day)
    if existing_idx is not None:
        raise HTTPException(status_code=400, detail="Already checked in today")

    late_flag, late_minutes = is_late(now)
    status_val = "Late" if late_flag else "Present"

    new_row = {
        "employee_id": employee_id,
        "date": day,
        "check_in": now.isoformat(),
        "check_out": "",
        "hours_worked": 0,
        "status": status_val,
        "shift_date": day,
    }
    attendance_db.insert(new_row)
    logger.info(f"Check-in: {employee_id} at {now.isoformat()} status={status_val}")
    return {
        "message": "Check-in successful",
        "employee_id": employee_id,
        "time": now.isoformat(),
        "status": status_val,
        "late_minutes": late_minutes if late_flag else 0,
    }


def check_out(employee_id: str) -> Dict[str, Any]:
    if not employee_id or not employee_id.strip():
        raise HTTPException(status_code=400, detail="employee_id is required")

    emp = employee_db.find_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    df = attendance_db.read_all()
    day = today_str()
    idx = _find_today_row(df, employee_id, day)
    if idx is None:
        raise HTTPException(status_code=400, detail="No check-in found for today")

    current_check_out = str(df.loc[idx, "check_out"] or "")
    if current_check_out.strip():
        raise HTTPException(status_code=400, detail="Already checked out today")

    check_in_str = str(df.loc[idx, "check_in"])
    check_in_dt = datetime.fromisoformat(check_in_str)
    check_out_dt = now_utc()
    hours = compute_hours_worked(check_in_dt, check_out_dt)

    df.loc[idx, "check_out"] = check_out_dt.isoformat()
    df.loc[idx, "hours_worked"] = str(hours)
    attendance_db.write_all(df)

    logger.info(f"Check-out: {employee_id}, hours={hours}")
    return {
        "message": "Check-out successful",
        "employee_id": employee_id,
        "check_out": check_out_dt.isoformat(),
        "hours_worked": hours,
    }


def auto_close_missed_checkouts() -> int:
    df = attendance_db.read_all()
    day = today_str()
    mask = (df["date"] == day) & ((df["check_out"].isna()) | (df["check_out"].astype(str).str.strip() == ""))
    closed = 0
    for idx in df[mask].index:
        check_in_str = str(df.loc[idx, "check_in"])
        try:
            check_in_dt = datetime.fromisoformat(check_in_str)
            close_dt = auto_close_datetime(check_in_dt)
            hours = compute_hours_worked(check_in_dt, close_dt)
            df.loc[idx, "check_out"] = close_dt.isoformat()
            df.loc[idx, "hours_worked"] = str(hours)
            closed += 1
        except (ValueError, TypeError):
            continue
    if closed > 0:
        attendance_db.write_all(df)
        logger.info(f"Auto-closed {closed} missed check-outs for {day}")
    return closed


def get_attendance_history(employee_id: str) -> List[Dict[str, Any]]:
    df = attendance_db.read_all()
    records = df[df["employee_id"].astype(str) == employee_id].copy()
    records = records.sort_values("date", ascending=False)
    return records.to_dict(orient="records")


def get_all_attendance(
    date_filter: Optional[str] = None,
    department: Optional[str] = None,
) -> List[Dict[str, Any]]:
    df = attendance_db.read_all()
    if date_filter:
        df = df[df["date"].astype(str) == date_filter]
    if department:
        emp_df = employee_db.read_all()
        emp_ids = emp_df[emp_df["Department"].astype(str).str.lower() == department.lower()]["Employee ID"].astype(str).tolist()
        df = df[df["employee_id"].astype(str).isin(emp_ids)]
    df = df.sort_values("date", ascending=False)
    return df.to_dict(orient="records")
