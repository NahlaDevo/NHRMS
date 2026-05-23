import pytest
from unittest.mock import patch, MagicMock
from backend.app.database.excel_manager import ExcelManager, EMPLOYEE_COLUMNS
import tempfile
from pathlib import Path


class TestExcelManager:
    @pytest.fixture
    def manager(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        mgr = ExcelManager(path, "TestSheet", EMPLOYEE_COLUMNS)
        yield mgr
        Path(path).unlink(missing_ok=True)

    def test_create_file(self, manager):
        df = manager.read_all()
        assert list(df.columns) == EMPLOYEE_COLUMNS
        assert len(df) == 0

    def test_insert_and_find(self, manager):
        record = {
            "Employee ID": "EMP001",
            "Full Name": "John Doe",
            "Department": "Engineering",
            "Position": "Developer",
            "Email": "john@test.com",
            "Phone Number": "1234567890",
        }
        manager.insert(record)
        found = manager.find_by_id("EMP001")
        assert found is not None
        assert found["Full Name"] == "John Doe"

    def test_update(self, manager):
        record = {
            "Employee ID": "EMP001",
            "Full Name": "John Doe",
            "Department": "Engineering",
            "Position": "Developer",
            "Email": "john@test.com",
            "Phone Number": "1234567890",
        }
        manager.insert(record)
        manager.update("EMP001", {"Department": "Marketing"})
        updated = manager.find_by_id("EMP001")
        assert updated["Department"] == "Marketing"

    def test_delete(self, manager):
        record = {
            "Employee ID": "EMP001",
            "Full Name": "John Doe",
            "Department": "Engineering",
            "Position": "Developer",
            "Email": "john@test.com",
            "Phone Number": "1234567890",
        }
        manager.insert(record)
        assert manager.delete("EMP001") is True
        assert manager.find_by_id("EMP001") is None

    def test_search(self, manager):
        manager.insert({
            "Employee ID": "EMP001", "Full Name": "John Doe",
            "Department": "Engineering", "Position": "Developer",
            "Email": "john@test.com", "Phone Number": "123",
        })
        manager.insert({
            "Employee ID": "EMP002", "Full Name": "Jane Smith",
            "Department": "Marketing", "Position": "Analyst",
            "Email": "jane@test.com", "Phone Number": "456",
        })
        results = manager.search("jane")
        assert len(results) == 1
        assert results.iloc[0]["Full Name"] == "Jane Smith"

    def test_statistics(self, manager):
        manager.insert({
            "Employee ID": "EMP001", "Full Name": "John",
            "Department": "Engineering", "Position": "Dev",
            "Email": "j@t.com", "Phone Number": "1",
            "Employment Status": "Active", "Salary": "50000",
        })
        manager.insert({
            "Employee ID": "EMP002", "Full Name": "Jane",
            "Department": "Marketing", "Position": "Mgr",
            "Email": "ja@t.com", "Phone Number": "2",
            "Employment Status": "Active", "Salary": "60000",
        })
        stats = manager.get_statistics()
        assert stats["total_employees"] == 2
        assert stats["salary_stats"]["avg"] == 55000.0
