"""
auth.py - Secure User Authentication & SQLite Management for ShellSathi

Features:
  - SQLite persistent database storage (data/users.db)
  - Cryptographic password hashing via PBKDF2-HMAC-SHA256 (200,000 iterations)
  - Per-user cryptographically random 16-byte salt
  - Constant-time password verification to prevent timing attacks
  - Email format and password length validation
  - Default user initialization for quick demonstrations
"""

import hashlib
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "users.db"
PBKDF2_ITERATIONS = 200_000
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def get_db_path(db_path: Optional[Path] = None) -> Path:
    """Resolve database path, ensuring parent directories exist."""
    path = db_path or DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Return SQLite connection configured with Row factory."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: str) -> str:
    """Compute PBKDF2-HMAC-SHA256 hex digest using cryptographic salt."""
    digest = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt.encode("utf-8"),
        iterations=PBKDF2_ITERATIONS,
    )
    return digest.hex()


def validate_email(email: str) -> bool:
    """Validate RFC-compliant email string format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def init_user_db(db_path: Optional[Path] = None) -> None:
    """Initialize SQLite users table and seed default accounts if missing."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

        # Seed default project presentation user if table is empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_users = [
                ("harsh@shellsathi.com", "Harsh Vilas Aher", "Harsh@123"),
                ("admin@shellsathi.com", "Administrator", "Admin@123"),
            ]
            for email, name, pwd in seed_users:
                salt = secrets.token_hex(16)
                pwd_hash = hash_password(pwd, salt)
                now_iso = datetime.now(timezone.utc).isoformat()
                with conn:
                    conn.execute(
                        """
                        INSERT INTO users (email, full_name, password_hash, salt, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (email.lower().strip(), name.strip(), pwd_hash, salt, now_iso),
                    )
    finally:
        conn.close()


def get_user_by_email(email: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve user dictionary by email address."""
    clean_email = (email or "").strip().lower()
    if not clean_email:
        return None

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (clean_email,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def register_user(
    email: str,
    full_name: str,
    password: str,
    db_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Register a new user with secure password hashing.

    Returns:
        (True, "Success message") or (False, "Error description")
    """
    clean_email = (email or "").strip().lower()
    clean_name = (full_name or "").strip()

    if not clean_email or not validate_email(clean_email):
        return False, "Please provide a valid email address."

    if not clean_name or len(clean_name) < 2:
        return False, "Full Name must be at least 2 characters long."

    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."

    init_user_db(db_path)
    if get_user_by_email(clean_email, db_path) is not None:
        return False, f"An account with email '{clean_email}' already exists."

    salt = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO users (email, full_name, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (clean_email, clean_name, pwd_hash, salt, now_iso),
            )
        return True, "Account created successfully! You can now log in."
    except sqlite3.IntegrityError:
        return False, f"An account with email '{clean_email}' already exists."
    except Exception as exc:
        return False, f"Registration failed: {exc}"
    finally:
        conn.close()


def authenticate_user(
    email: str,
    password: str,
    db_path: Optional[Path] = None,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Authenticate user credentials using constant-time comparison.

    Returns:
        (user_dict, "Success") or (None, "Invalid credentials")
    """
    clean_email = (email or "").strip().lower()
    if not clean_email or not password:
        return None, "Please enter both email and password."

    init_user_db(db_path)
    user = get_user_by_email(clean_email, db_path)
    if not user:
        return None, "Invalid email or password."

    computed_hash = hash_password(password, user["salt"])
    # secrets.compare_digest prevents timing attacks
    if not secrets.compare_digest(computed_hash, user["password_hash"]):
        return None, "Invalid email or password."

    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "created_at": user["created_at"],
    }, "Authentication successful."


def reset_password(
    email: str,
    new_password: str,
    db_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Reset password for an existing registered account.

    Returns:
        (True, "Password updated") or (False, "Error message")
    """
    clean_email = (email or "").strip().lower()
    if not clean_email or not validate_email(clean_email):
        return False, "Please enter a valid registered email address."

    if not new_password or len(new_password) < 6:
        return False, "New password must be at least 6 characters long."

    init_user_db(db_path)
    user = get_user_by_email(clean_email, db_path)
    if not user:
        return False, f"No registered account found for '{clean_email}'."

    new_salt = secrets.token_hex(16)
    new_hash = hash_password(new_password, new_salt)

    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET password_hash = ?, salt = ?
                WHERE email = ?
                """,
                (new_hash, new_salt, clean_email),
            )
        return True, "Password reset successfully! Please log in with your new password."
    except Exception as exc:
        return False, f"Password reset failed: {exc}"
    finally:
        conn.close()
