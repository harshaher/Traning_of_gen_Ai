"""
test_auth.py - Unit & Integration Tests for ShellSathi User Authentication

Covers:
  1. User database initialization and seed accounts.
  2. Registration of new users with valid and invalid email/password.
  3. Prevention of duplicate email registrations.
  4. Password hashing security (ensuring plaintext is never saved).
  5. Authentication verification (positive and negative cases).
  6. Password reset functionality.
"""

from pathlib import Path

from app.auth import (
    authenticate_user,
    get_user_by_email,
    hash_password,
    init_user_db,
    register_user,
    reset_password,
    validate_email,
)


def test_validate_email_formats():
    """Verify email format validation."""
    assert validate_email("user@example.com") is True
    assert validate_email("harsh.aher@college.ac.in") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@no-user.com") is False
    assert validate_email("") is False


def test_seed_user_authentication(tmp_path: Path):
    """Verify default seeded student and admin accounts."""
    db_file = tmp_path / "test_users.db"
    init_user_db(db_file)

    user, msg = authenticate_user("harsh@shellsathi.com", "Harsh@123", db_file)
    assert user is not None
    assert user["full_name"] == "Harsh Vilas Aher"
    assert user["email"] == "harsh@shellsathi.com"

    admin, _ = authenticate_user("admin@shellsathi.com", "Admin@123", db_file)
    assert admin is not None
    assert admin["full_name"] == "Administrator"


def test_user_registration_flow(tmp_path: Path):
    """Verify new user registration and authentication."""
    db_file = tmp_path / "test_users.db"
    init_user_db(db_file)

    # 1. Successful registration
    success, msg = register_user("neha@linux.org", "Neha Sharma", "StrongPass@2026", db_file)
    assert success is True
    assert "successfully" in msg.lower()

    # 2. Login with newly registered credentials
    user, auth_msg = authenticate_user("neha@linux.org", "StrongPass@2026", db_file)
    assert user is not None
    assert user["full_name"] == "Neha Sharma"

    # 3. Wrong password rejection
    bad_user, bad_msg = authenticate_user("neha@linux.org", "WrongPassword", db_file)
    assert bad_user is None
    assert "invalid" in bad_msg.lower()


def test_duplicate_registration_prevention(tmp_path: Path):
    """Verify duplicate email addresses are rejected."""
    db_file = tmp_path / "test_users.db"
    init_user_db(db_file)

    ok1, _ = register_user("unique@domain.com", "First User", "Password123", db_file)
    assert ok1 is True

    ok2, err2 = register_user("unique@domain.com", "Second User", "Password999", db_file)
    assert ok2 is False
    assert "already exists" in err2.lower()


def test_password_hashing_security(tmp_path: Path):
    """Verify passwords are securely hashed and salts differ."""
    db_file = tmp_path / "test_users.db"
    init_user_db(db_file)

    pwd = "MySecretPassword"
    salt1 = "salt_alpha_12345"
    salt2 = "salt_beta_67890"

    hash1 = hash_password(pwd, salt1)
    hash2 = hash_password(pwd, salt2)

    assert hash1 != hash2
    assert pwd not in hash1

    register_user("security@audit.com", "Audit Officer", pwd, db_file)
    record = get_user_by_email("security@audit.com", db_file)
    assert record is not None
    assert record["password_hash"] != pwd
    assert len(record["password_hash"]) == 64  # SHA-256 hex length
    assert len(record["salt"]) == 32  # 16-byte hex length


def test_password_reset(tmp_path: Path):
    """Verify forgot password / reset password workflow."""
    db_file = tmp_path / "test_users.db"
    init_user_db(db_file)

    register_user("recover@domain.com", "Recovery Test", "InitialPass123", db_file)

    # Reset password
    success, msg = reset_password("recover@domain.com", "BrandNewPass999", db_file)
    assert success is True

    # Old password no longer works
    old_login, _ = authenticate_user("recover@domain.com", "InitialPass123", db_file)
    assert old_login is None

    # New password works
    new_login, _ = authenticate_user("recover@domain.com", "BrandNewPass999", db_file)
    assert new_login is not None
