from fastapi import APIRouter, Depends, Query, UploadFile, File
from typing import Optional, List
from backend.app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from backend.app.services import employee_service
from backend.app.utils.security import get_current_user, require_permission
from backend.app.utils.helpers import save_upload_file

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.post("/", response_model=EmployeeResponse)
def create_employee(
    data: EmployeeCreate,
    _: dict = Depends(require_permission("employee.create")),
):
    return employee_service.create_employee(data)


@router.get("/", response_model=EmployeeListResponse)
def list_employees(
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    _: dict = Depends(require_permission("employee.read")),
):
    return employee_service.list_employees(search=search, department=department, status=status)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    _: dict = Depends(require_permission("employee.read")),
):
    return employee_service.get_employee(employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    _: dict = Depends(require_permission("employee.update")),
):
    return employee_service.update_employee(employee_id, data)


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    _: dict = Depends(require_permission("employee.delete")),
):
    return employee_service.delete_employee(employee_id)


@router.post("/{employee_id}/upload")
async def upload_document(
    employee_id: str,
    file: UploadFile = File(...),
    _: dict = Depends(require_permission("employee.upload_doc")),
):
    file_path = await save_upload_file(file, employee_id)
    return {"message": "File uploaded successfully", "file_path": file_path}


@router.post("/import")
def import_employees(
    records: List[dict],
    _: dict = Depends(require_permission("employee.import")),
):
    return employee_service.import_employees(records)
