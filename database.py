import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def test_database():
    conn = get_connection()

    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        print("Database:", DB_PATH)
        print("Tables:", [table["name"] for table in tables])

    finally:
        conn.close()


if __name__ == "__main__":
    test_database()