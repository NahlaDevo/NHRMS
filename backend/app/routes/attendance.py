from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.services import attendance_service
from backend.app.utils.security import get_current_user, require_permission
from backend.app.utils.helpers import logger

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/checkin")
def check_in(
    employee_id: str = Query(..., description="Employee ID"),
    _: dict = Depends(require_permission("attendance.checkin")),
):
    result = attendance_service.check_in(employee_id)
    logger.info(f"Check-in via API: {employee_id}")
    return result


@router.post("/checkout")
def check_out(
    employee_id: str = Query(..., description="Employee ID"),
    _: dict = Depends(require_permission("attendance.checkout")),
):
    result = attendance_service.check_out(employee_id)
    logger.info(f"Check-out via API: {employee_id}")
    return result


@router.post("/auto-close")
def auto_close(
    _: dict = Depends(require_permission("attendance.auto_close")),
):
    closed = attendance_service.auto_close_missed_checkouts()
    return {"message": f"Auto-closed {closed} records", "closed": closed}


@router.get("/today")
def get_today_attendance(
    _: dict = Depends(require_permission("attendance.read")),
):
    records = attendance_service.get_all_attendance()
    return {"records": records}


@router.get("/{employee_id}")
def get_employee_attendance(
    employee_id: str,
    _: dict = Depends(require_permission("attendance.read")),
):
    records = attendance_service.get_attendance_history(employee_id)
    return {"employee_id": employee_id, "records": records}
