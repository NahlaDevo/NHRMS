from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.database.sa_setup import get_db


def get_company_id(request: Request) -> str:
    company_id = request.headers.get("X-Company-ID")
    if not company_id:
        raise HTTPException(status_code=400, detail="Missing X-Company-ID header")
    return company_id


def get_db_and_company(
    db: Session = Depends(get_db),
    company_id: str = Depends(get_company_id),
):
    return db, company_id
