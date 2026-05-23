from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from backend.app.database.excel_manager import employee_db, EMPLOYEE_COLUMNS
from backend.app.utils.helpers import logger
from backend.app.schemas.employee import EmployeeCreate, EmployeeUpdate

FIELD_MAP = {
    "employee_id": "Employee ID",
    "full_name": "Full Name",
    "department": "Department",
    "position": "Position",
    "email": "Email",
    "phone_number": "Phone Number",
    "address": "Address",
    "national_id": "National ID",
    "date_of_birth": "Date of Birth",
    "hiring_date": "Hiring Date",
    "salary": "Salary",
    "emergency_contact": "Emergency Contact",
    "manager_name": "Manager Name",
    "employment_status": "Employment Status",
    "notes": "Notes",
    "created_at": "Created At",
    "updated_at": "Updated At",
}

REVERSE_MAP = {v: k for k, v in FIELD_MAP.items()}


def _to_excel(data: Dict[str, Any]) -> Dict[str, Any]:
    return {FIELD_MAP.get(k, k): v for k, v in data.items()}


def _from_excel(data: Dict[str, Any]) -> Dict[str, Any]:
    return {REVERSE_MAP.get(k, k): v for k, v in data.items()}


def create_employee(data: EmployeeCreate) -> Dict[str, Any]:
    existing = employee_db.find_by_id(data.employee_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with ID {data.employee_id} already exists",
        )
    record = _to_excel(data.model_dump())
    employee_db.insert(record)
    logger.info(f"Employee created: {data.employee_id}")
    return _from_excel(employee_db.find_by_id(data.employee_id) or record)


def get_employee(employee_id: str) -> Dict[str, Any]:
    emp = employee_db.find_by_id(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _from_excel(emp)


def update_employee(employee_id: str, data: EmployeeUpdate) -> Dict[str, Any]:
    existing = employee_db.find_by_id(employee_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Employee not found")
    raw = {k: v for k, v in data.model_dump().items() if v is not None}
    updates = _to_excel(raw)
    if not updates:
        return _from_excel(existing)
    employee_db.update(employee_id, updates)
    logger.info(f"Employee updated: {employee_id}")
    return _from_excel(employee_db.find_by_id(employee_id) or existing)


def delete_employee(employee_id: str) -> Dict[str, str]:
    deleted = employee_db.delete(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Employee not found")
    logger.info(f"Employee deleted: {employee_id}")
    return {"message": "Employee deleted successfully"}


def list_employees(search: Optional[str] = None, department: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
    df = employee_db.get_all_sorted()
    if search:
        df = employee_db.search(search)
    if department:
        df = df[df["Department"].astype(str).str.lower() == department.lower()]
    if status:
        df = df[df["Employment Status"].astype(str).str.lower() == status.lower()]
    employees = [_from_excel(r) for r in df.to_dict(orient="records")]
    return {"total": len(employees), "employees": employees}


def import_employees(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    excel_records = [_to_excel(r) for r in records]
    count = employee_db.import_records(excel_records)
    return {"message": f"Imported {count} records", "count": count}
