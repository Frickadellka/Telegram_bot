from psycopg import connect
from config import DB_CONFIG

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'employee')),
    telegram_id BIGINT UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

if __name__ == "__main__":
    with connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(create_users_table)
        conn.commit()

    print("Таблица users создана.")