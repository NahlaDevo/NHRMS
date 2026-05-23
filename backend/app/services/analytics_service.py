import pandas as pd
import numpy as np
from typing import Dict, Any
from backend.app.database.excel_manager import employee_db
from backend.app.utils.helpers import logger


def get_analytics() -> Dict[str, Any]:
    try:
        df = employee_db.read_all()
        if df.empty:
            return {"total_employees": 0, "message": "No employee data available"}

        stats = employee_db.get_statistics()

        analytics = {
            "total_employees": int(stats.get("total_employees", 0)),
            "by_department": _safe_dict(stats.get("by_department", {})),
            "by_status": _safe_dict(stats.get("by_status", {})),
            "salary_stats": _safe_salary(stats.get("salary_stats", {})),
            "hiring_trends": _safe_dict(stats.get("hiring_trends", {})),
            "missing_data": stats.get("missing_data", {}),
        }

        if "Hiring Date" in df.columns:
            hiring = pd.to_datetime(df["Hiring Date"], errors="coerce")
            monthly = hiring.dt.to_period("M").value_counts().sort_index()
            analytics["monthly_onboarding"] = {
                str(k): int(v) for k, v in monthly.head(12).items()
            }
        else:
            analytics["monthly_onboarding"] = {}

        return analytics
    except Exception as e:
        logger.error(f"Analytics error: {e}", exc_info=True)
        return {"total_employees": 0, "error": str(e)}


def _safe_dict(d: Dict) -> Dict:
    result = {}
    for k, v in d.items():
        try:
            result[str(k)] = int(v)
        except (ValueError, TypeError):
            try:
                result[str(k)] = float(v)
            except (ValueError, TypeError):
                result[str(k)] = 0
    return result


def _safe_salary(d: Dict) -> Dict:
    result = {}
    for k, v in d.items():
        try:
            result[str(k)] = round(float(v), 2) if pd.notna(v) else None
        except (ValueError, TypeError):
            result[str(k)] = None
    return result


def get_department_breakdown() -> Dict[str, Any]:
    try:
        df = employee_db.read_all()
        if df.empty or "Department" not in df.columns:
            return {}
        breakdown = df["Department"].value_counts().to_dict()
        return {str(k): int(v) for k, v in breakdown.items()}
    except Exception as e:
        logger.error(f"Department breakdown error: {e}", exc_info=True)
        return {}


def get_salary_analysis() -> Dict[str, Any]:
    try:
        df = employee_db.read_all()
        if df.empty or "Salary" not in df.columns:
            return {}
        salary = pd.to_numeric(df["Salary"], errors="coerce").dropna()
        if salary.empty:
            return {}
        return {
            "avg": round(float(salary.mean()), 2),
            "median": round(float(salary.median()), 2),
            "min": round(float(salary.min()), 2),
            "max": round(float(salary.max()), 2),
            "total": round(float(salary.sum()), 2),
            "count": int(salary.count()),
        }
    except Exception as e:
        logger.error(f"Salary analysis error: {e}", exc_info=True)
        return {}
