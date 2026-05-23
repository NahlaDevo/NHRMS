from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.services import payroll_service
from backend.app.utils.security import get_current_user, require_permission
from backend.app.utils.helpers import logger

router = APIRouter(prefix="/api/payroll", tags=["Payroll"])


@router.get("/generate/{employee_id}/{month}")
def generate_employee_payroll(
    employee_id: str,
    month: str,
    _: dict = Depends(require_permission("payroll.generate")),
):
    result = payroll_service.generate_payroll(employee_id, month)
    logger.info(f"Payroll generated via API: {employee_id} for {month}")
    return result


@router.post("/generate-all/{month}")
def generate_all_payroll(
    month: str,
    _: dict = Depends(require_permission("payroll.generate")),
):
    result = payroll_service.generate_all_payroll(month)
    logger.info(f"Bulk payroll generated for {month}")
    return result


@router.get("/report/{month}")
def get_payroll_report(
    month: str,
    _: dict = Depends(require_permission("payroll.read")),
):
    records = payroll_service.get_payroll_report(month)
    return {"month": month, "records": records}


@router.get("/summary/{month}")
def get_payroll_summary(
    month: str,
    _: dict = Depends(require_permission("payroll.read")),
):
    return payroll_service.get_payroll_summary(month)


@router.get("/export/{month}")
def export_payroll(
    month: str,
    _: dict = Depends(require_permission("payroll.export")),
):
    return payroll_service.export_payroll_to_excel(month)


@router.get("/{employee_id}")
def get_employee_payroll(
    employee_id: str,
    _: dict = Depends(require_permission("payroll.read")),
):
    records = payroll_service.get_employee_payroll(employee_id)
    return {"employee_id": employee_id, "records": records}
