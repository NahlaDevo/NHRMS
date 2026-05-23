import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.app.config import settings
from backend.app.utils.helpers import logger, backup_excel

EMPLOYEE_COLUMNS = [
    "Employee ID", "Full Name", "Department", "Position", "Email",
    "Phone Number", "Address", "National ID", "Date of Birth",
    "Hiring Date", "Salary", "Emergency Contact", "Manager Name",
    "Employment Status", "Notes", "Created At", "Updated At"
]

USER_COLUMNS = [
    "User ID", "Username", "Password Hash", "Email", "Role", "Is Active",
    "Created At", "Updated At"
]


class ExcelManager:
    def __init__(self, file_path: str, sheet_name: str, columns: list):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.columns = columns
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            df = pd.DataFrame(columns=self.columns)
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with pd.ExcelWriter(self.file_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=self.sheet_name, index=False)
            logger.info(f"Created Excel file: {self.file_path}")
        else:
            self._migrate_columns()

    def _migrate_columns(self):
        try:
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, dtype=str)
            missing = [c for c in self.columns if c not in df.columns]
            if missing:
                for c in missing:
                    df[c] = ""
                with pd.ExcelWriter(self.file_path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=self.sheet_name, index=False)
                logger.info(f"Migrated columns: added {missing}")
        except Exception:
            pass

    def read_all(self) -> pd.DataFrame:
        try:
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, dtype=str)
            df = df.fillna("")
            return df
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return pd.DataFrame(columns=self.columns)

    def write_all(self, df: pd.DataFrame):
        backup_excel(str(self.file_path))
        with pd.ExcelWriter(self.file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
        logger.info(f"Written {len(df)} rows to {self.file_path}")

    def find_by_id(self, record_id: str, id_column: str = "Employee ID") -> Optional[Dict[str, Any]]:
        df = self.read_all()
        if df.empty or id_column not in df.columns:
            return None
        mask = df[id_column].astype(str).str.strip() == str(record_id).strip()
        if mask.any():
            return df[mask].iloc[0].to_dict()
        return None

    def insert(self, record: Dict[str, Any]) -> Dict[str, Any]:
        df = self.read_all()
        now = datetime.now().isoformat()
        record["Created At"] = now
        record["Updated At"] = now
        for col in self.columns:
            if col not in record:
                record[col] = ""
        new_row = pd.DataFrame([record])
        df = pd.concat([df, new_row], ignore_index=True)
        self.write_all(df)
        logger.info(f"Inserted record: {record.get(list(record.keys())[0], 'N/A')}")
        return record

    def update(self, record_id: str, updates: Dict[str, Any], id_column: str = "Employee ID") -> Optional[Dict[str, Any]]:
        df = self.read_all()
        if df.empty or id_column not in df.columns:
            return None
        mask = df[id_column].astype(str).str.strip() == str(record_id).strip()
        if not mask.any():
            return None
        now = datetime.now().isoformat()
        updates["Updated At"] = now
        for key, value in updates.items():
            if key in df.columns:
                df.loc[mask, key] = value
        self.write_all(df)
        logger.info(f"Updated record {record_id}")
        return df[mask].iloc[0].to_dict()

    def delete(self, record_id: str, id_column: str = "Employee ID") -> bool:
        df = self.read_all()
        if df.empty or id_column not in df.columns:
            return False
        mask = df[id_column].astype(str).str.strip() == str(record_id).strip()
        if not mask.any():
            return False
        df = df[~mask]
        self.write_all(df)
        logger.info(f"Deleted record {record_id}")
        return True

    def get_all_sorted(self, sort_by: str = "Created At", ascending: bool = False) -> pd.DataFrame:
        df = self.read_all()
        if sort_by in df.columns:
            df = df.sort_values(by=sort_by, ascending=ascending)
        return df

    def search(self, query: str, fields: Optional[List[str]] = None) -> pd.DataFrame:
        df = self.read_all()
        if df.empty or not query:
            return df
        if fields is None:
            fields = df.columns.tolist()
        query = query.lower().strip()
        mask = pd.Series([False] * len(df))
        for field in fields:
            if field in df.columns:
                mask = mask | df[field].astype(str).str.lower().str.contains(query, na=False)
        return df[mask]

    def import_records(self, records: List[Dict[str, Any]]) -> int:
        count = 0
        for record in records:
            existing = self.find_by_id(record.get("Employee ID", ""))
            if existing:
                self.update(record["Employee ID"], record)
            else:
                self.insert(record)
            count += 1
        logger.info(f"Imported/Updated {count} records")
        return count

    def export_to_excel(self, output_path: str):
        df = self.read_all()
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)
        logger.info(f"Exported to {output_path}")
        return output_path

    def get_statistics(self) -> Dict[str, Any]:
        df = self.read_all()
        stats = {}
        if df.empty:
            return {"total_employees": 0}
        stats["total_employees"] = len(df)
        if "Department" in df.columns:
            stats["by_department"] = df["Department"].value_counts().to_dict()
        if "Employment Status" in df.columns:
            stats["by_status"] = df["Employment Status"].value_counts().to_dict()
        if "Salary" in df.columns:
            salary = pd.to_numeric(df["Salary"], errors="coerce")
            stats["salary_stats"] = {
                "avg": float(salary.mean()) if not salary.empty and pd.notna(salary.mean()) else 0,
                "min": float(salary.min()) if not salary.empty and pd.notna(salary.min()) else 0,
                "max": float(salary.max()) if not salary.empty and pd.notna(salary.max()) else 0,
                "median": float(salary.median()) if not salary.empty and pd.notna(salary.median()) else 0,
            }
        if "Hiring Date" in df.columns:
            hiring = pd.to_datetime(df["Hiring Date"], errors="coerce")
            stats["hiring_trends"] = hiring.dt.year.value_counts().sort_index().to_dict()
        if "Department" in df.columns:
            missing = df["Department"].isna().sum() + (df["Department"] == "").sum()
            stats["missing_data"] = {
                "department_missing": int(missing),
                "total_fields": len(df) * len(df.columns),
                "filled_fields": int(((df != "") & (df.notna())).sum().sum()),
            }
        return stats


employee_db = ExcelManager(
    file_path=settings.EXCEL_FILE,
    sheet_name=settings.EXCEL_SHEET_NAME,
    columns=EMPLOYEE_COLUMNS
)

user_db = ExcelManager(
    file_path=settings.USERS_EXCEL_FILE,
    sheet_name=settings.USERS_SHEET_NAME,
    columns=USER_COLUMNS
)

ATTENDANCE_COLUMNS = [
    "employee_id", "date", "check_in", "check_out",
    "hours_worked", "status", "shift_date"
]

PAYROLL_COLUMNS = [
    "employee_id", "month", "base_salary",
    "total_hours", "overtime", "deductions", "net_salary"
]

attendance_db = ExcelManager(
    file_path=settings.ATTENDANCE_EXCEL_FILE,
    sheet_name=settings.ATTENDANCE_SHEET_NAME,
    columns=ATTENDANCE_COLUMNS
)

payroll_db = ExcelManager(
    file_path=settings.PAYROLL_EXCEL_FILE,
    sheet_name=settings.PAYROLL_SHEET_NAME,
    columns=PAYROLL_COLUMNS
)
