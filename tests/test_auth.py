import pytest
from unittest.mock import patch, MagicMock
from backend.app.services.auth_service import register_user, authenticate_user
from backend.app.utils.security import hash_password, verify_password, create_access_token, decode_access_token


class TestAuth:
    def test_hash_password(self):
        hashed = hash_password("testpass123")
        assert hashed != "testpass123"
        assert verify_password("testpass123", hashed) is True
        assert verify_password("wrongpass", hashed) is False

    def test_create_and_decode_token(self):
        token = create_access_token({"sub": "testuser", "role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    @patch("backend.app.services.auth_service.user_db")
    def test_register_user(self, mock_db):
        mock_db.find_by_id.return_value = None
        result = register_user("newuser", "password123", "new@test.com")
        assert result["username"] == "newuser"
        mock_db.insert.assert_called_once()

    @patch("backend.app.services.auth_service.user_db")
    def test_register_duplicate_user(self, mock_db):
        mock_db.find_by_id.return_value = {"Username": "existing"}
        with pytest.raises(Exception):
            register_user("existing", "pass", "e@test.com")
