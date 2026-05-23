from fastapi import APIRouter, Depends
from backend.app.services import analytics_service
from backend.app.utils.security import require_permission

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_analytics(
    _: dict = Depends(require_permission("analytics.read")),
):
    return analytics_service.get_analytics()


@router.get("/departments")
def get_department_breakdown(
    _: dict = Depends(require_permission("analytics.read")),
):
    return analytics_service.get_department_breakdown()


@router.get("/salary")
def get_salary_analysis(
    _: dict = Depends(require_permission("analytics.read")),
):
    return analytics_service.get_salary_analysis()
