from psycopg import connect
import bcrypt
from config import DB_CONFIG


def get_connection():
    return connect(**DB_CONFIG)


def get_user_by_username(username: str):
    query = """
    SELECT id, username, password_hash, role
    FROM users
    WHERE username = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (username,))
            return cur.fetchone()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )