import pytest
from unittest.mock import MagicMock, patch
from app.services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    register_user,
)
from app.models.user import AccountStatus


# ─── Password Tests ────────────────────────────────────────────────────────────

def test_hash_password_returns_string():
    hashed = hash_password("securepassword123")
    assert isinstance(hashed, str)
    assert hashed != "securepassword123"


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


# ─── JWT Tests ─────────────────────────────────────────────────────────────────

def test_create_access_token():
    token, jti = create_access_token(user_id=1, email="test@example.com")
    assert isinstance(token, str)
    assert isinstance(jti, str)


def test_decode_valid_access_token():
    token, jti = create_access_token(user_id=42, email="user@test.com")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["email"] == "user@test.com"
    assert payload["type"] == "access"
    assert payload["jti"] == jti


def test_decode_invalid_token():
    payload = decode_token("this.is.not.valid")
    assert payload is None


def test_decode_refresh_token():
    token, jti = create_refresh_token(user_id=7)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "7"
    assert payload["type"] == "refresh"


def test_create_refresh_token():
    token, jti = create_refresh_token(user_id=1)
    assert isinstance(token, str)
    assert len(jti) > 0


# ─── Registration Tests ───────────────────────────────────────────────────────

def test_register_user_success():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    user = register_user(db, name="Alice", email="alice@example.com", password="password123")
    assert db.add.called
    assert db.commit.called


def test_register_duplicate_email():
    from app.models.user import User
    db = MagicMock()
    existing = User(user_id=1, name="Existing", email="exists@example.com", password_hash="x")
    db.query.return_value.filter.return_value.first.return_value = existing

    with pytest.raises(ValueError, match="already registered"):
        register_user(db, name="New", email="exists@example.com", password="pass12345")
