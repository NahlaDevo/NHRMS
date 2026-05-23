from typing import Optional, List, Dict, Any
from datetime import datetime
from io import BytesIO
import pandas as pd
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from backend.app.database.excel_manager import attendance_db, payroll_db, employee_db
from backend.app.utils.helpers import logger
from backend.app.utils.time_utils import calculate_deductions
from backend.app.config import settings


def generate_payroll(employee_id: str, month: str) -> Dict[str, Any]:
    emp = employee_db.find_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    base_salary_str = str(emp.get("Salary", "") or "").strip()
    base_salary = float(base_salary_str) if base_salary_str else settings.DEFAULT_BASE_SALARY

    att = attendance_db.read_all()
    att = att[
        (att["employee_id"].astype(str) == employee_id) &
        (att["date"].astype(str).str.startswith(month))
    ].copy()

    if att.empty:
        raise HTTPException(status_code=404, detail="No attendance records for this period")

    total_hours = att["hours_worked"].astype(float).sum()
    hourly_rate = base_salary / settings.STANDARD_MONTHLY_HOURS
    overtime_hours = max(0, round(total_hours - settings.STANDARD_MONTHLY_HOURS, 2))
    overtime_pay = round(overtime_hours * hourly_rate * settings.OVERTIME_RATE_MULTIPLIER, 2)
    deductions = calculate_deductions(employee_id, month, att)
    net_salary = round(base_salary + overtime_pay - deductions, 2)

    result = {
        "employee_id": employee_id,
        "month": month,
        "base_salary": base_salary,
        "total_hours": round(total_hours, 2),
        "overtime": overtime_hours,
        "overtime_pay": overtime_pay,
        "deductions": deductions,
        "net_salary": net_salary,
    }

    record_key = f"{employee_id}_{month}"
    existing = payroll_db.find_by_id(record_key, id_column="employee_id")
    if existing:
        payroll_db.update(record_key, result, id_column="employee_id")
    else:
        insert_record = dict(result)
        insert_record["employee_id"] = record_key
        payroll_db.insert(insert_record)

    logger.info(f"Payroll generated: {employee_id} for {month}, net={net_salary}")
    result["employee_id"] = employee_id
    return result


def get_payroll_report(month: str) -> List[Dict[str, Any]]:
    df = payroll_db.read_all()
    records = df[df["month"].astype(str) == month].to_dict(orient="records")
    for r in records:
        eid = str(r.get("employee_id", "") or "")
        if "_" in eid:
            r["employee_id"] = eid.split("_")[0]
    return records


def get_employee_payroll(employee_id: str) -> List[Dict[str, Any]]:
    df = payroll_db.read_all()
    records = df[df["employee_id"].astype(str).str.contains(employee_id, na=False)].to_dict(orient="records")
    for r in records:
        eid = str(r.get("employee_id", "") or "")
        if "_" in eid:
            r["employee_id"] = eid.split("_")[0]
    return records


def export_payroll_to_excel(month: str) -> StreamingResponse:
    records = get_payroll_report(month)
    if not records:
        raise HTTPException(status_code=404, detail="No payroll records for this month")

    df = pd.DataFrame(records)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"Payroll_{month}", index=False)
    output.seek(0)

    filename = f"payroll_{month}.xlsx"
    logger.info(f"Payroll exported: {filename}")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def generate_all_payroll(month: str) -> Dict[str, Any]:
    emp_df = employee_db.read_all()
    generated = []
    errors = []
    for _, row in emp_df.iterrows():
        eid = str(row.get("Employee ID", "") or "").strip()
        if not eid:
            continue
        try:
            result = generate_payroll(eid, month)
            generated.append(eid)
        except HTTPException as e:
            if e.status_code == 404:
                errors.append({"employee_id": eid, "reason": e.detail})
    return {
        "month": month,
        "generated": len(generated),
        "errors": errors,
    }


def get_payroll_summary(month: str) -> Dict[str, Any]:
    records = get_payroll_report(month)
    if not records:
        return {"month": month, "total_employees": 0}
    df = pd.DataFrame(records)
    return {
        "month": month,
        "total_employees": len(df),
        "total_net_salary": round(float(df["net_salary"].astype(float).sum()), 2),
        "total_overtime_pay": round(float(df["overtime_pay"].astype(float).sum()), 2),
        "total_deductions": round(float(df["deductions"].astype(float).sum()), 2),
        "average_salary": round(float(df["net_salary"].astype(float).mean()), 2),
    }
