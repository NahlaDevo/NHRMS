from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from datetime import datetime
import pandas as pd
from backend.app.services import auth_service, employee_service
from backend.app.database.excel_manager import employee_db, attendance_db, payroll_db
from backend.app.utils.security import require_permission, ROLE_ADMIN
from backend.app.utils.helpers import logger
from backend.app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
def list_users(
    _: dict = Depends(require_permission("admin.users.read")),
):
    users = auth_service.get_all_users()
    return {"total": len(users), "users": users}


@router.put("/users/{username}/role")
def update_user_role(
    username: str,
    role: str,
    _: dict = Depends(require_permission("admin.users.manage")),
):
    return auth_service.update_user_role(username, role)


@router.delete("/users/{username}")
def deactivate_user(
    username: str,
    _: dict = Depends(require_permission("admin.users.manage")),
):
    return auth_service.deactivate_user(username)


@router.get("/export")
def export_employees(
    _: dict = Depends(require_permission("employee.export")),
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = str(settings.DATA_DIR / f"export_{timestamp}.xlsx")
    employee_db.export_to_excel(output_path)
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"employee_records_{timestamp}.xlsx",
    )


@router.get("/audit")
def get_audit_log(
    _: dict = Depends(require_permission("admin.audit.read")),
):
    log_file = settings.BASE_DIR / "app.log"
    if not log_file.exists():
        return {"logs": []}
    with open(log_file, "r") as f:
        lines = f.readlines()
    return {"logs": lines[-100:]}


@router.get("/attendance/today")
def today_attendance_summary(
    _: dict = Depends(require_permission("admin.attendance.stats")),
):
    today = datetime.now().date().isoformat()
    df = attendance_db.read_all()
    today_df = df[df["date"].astype(str) == today]
    total = len(today_df)
    present = len(today_df[today_df["status"].astype(str).str.lower() == "present"])
    late = len(today_df[today_df["status"].astype(str).str.lower() == "late"])
    checked_out = len(today_df[today_df["check_out"].astype(str).str.strip() != ""])
    return {
        "date": today,
        "total_employees": total,
        "present": int(present),
        "late": int(late),
        "checked_out": int(checked_out),
        "still_active": int(total - checked_out),
    }


@router.get("/attendance/department/{department}")
def department_attendance(
    department: str,
    _: dict = Depends(require_permission("admin.attendance.stats")),
):
    today = datetime.now().date().isoformat()
    emp_df = employee_db.read_all()
    dept_ids = emp_df[
        emp_df["Department"].astype(str).str.lower() == department.lower()
    ]["Employee ID"].astype(str).tolist()

    att_df = attendance_db.read_all()
    today_df = att_df[att_df["date"].astype(str) == today]
    dept_att = today_df[today_df["employee_id"].astype(str).isin(dept_ids)]
    return {
        "department": department,
        "date": today,
        "total_employees_in_dept": len(dept_ids),
        "present_today": len(dept_att[dept_att["status"].astype(str).str.lower() == "present"]),
        "late_today": len(dept_att[dept_att["status"].astype(str).str.lower() == "late"]),
        "absent_today": len(dept_ids) - len(dept_att),
    }


@router.get("/attendance/stats")
def attendance_statistics(
    _: dict = Depends(require_permission("admin.attendance.stats")),
):
    df = attendance_db.read_all()
    if df.empty:
        return {"total_records": 0}
    df["hours"] = pd.to_numeric(df["hours_worked"], errors="coerce")
    return {
        "total_records": len(df),
        "total_hours_worked": round(float(df["hours"].sum()), 2),
        "avg_hours_per_day": round(float(df["hours"].mean()), 2),
        "status_breakdown": df["status"].value_counts().to_dict(),
    }


@router.get("/payroll/summary/{month}")
def admin_payroll_summary(
    month: str,
    _: dict = Depends(require_permission("admin.payroll.stats")),
):
    df = payroll_db.read_all()
    month_df = df[df["month"].astype(str) == month]
    if month_df.empty:
        return {"month": month, "total_employees": 0}
    return {
        "month": month,
        "total_employees": len(month_df),
        "total_net_salary": round(float(month_df["net_salary"].astype(float).sum()), 2),
        "total_overtime_pay": round(float(month_df["overtime_pay"].astype(float).sum()), 2),
        "total_deductions": round(float(month_df["deductions"].astype(float).sum()), 2),
        "average_salary": round(float(month_df["net_salary"].astype(float).mean()), 2),
    }


@router.get("/payroll/department/{month}")
def department_payroll(
    month: str,
    _: dict = Depends(require_permission("admin.payroll.stats")),
):
    emp_df = employee_db.read_all()
    pay_df = payroll_db.read_all()
    month_pay = pay_df[pay_df["month"].astype(str) == month].copy()
    if month_pay.empty:
        return {"month": month, "departments": {}}
    month_pay["emp_id_clean"] = month_pay["employee_id"].astype(str).str.split("_").str[0]
    merged = month_pay.merge(
        emp_df[["Employee ID", "Department"]],
        left_on="emp_id_clean",
        right_on="Employee ID",
        how="left",
    )
    dept_groups = merged.groupby("Department").agg(
        employee_count=("net_salary", "count"),
        total_net_salary=("net_salary", lambda x: round(float(x.astype(float).sum()), 2)),
        avg_net_salary=("net_salary", lambda x: round(float(x.astype(float).mean()), 2)),
    ).reset_index()
    return {"month": month, "departments": dept_groups.to_dict(orient="records")}
