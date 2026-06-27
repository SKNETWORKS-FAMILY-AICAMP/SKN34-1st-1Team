import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data_samples" / "demo.sqlite3"
SCHEMA_PATH = ROOT / "sql" / "sqlite_schema.sql"


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    print(f"SQLite demo DB initialized: {DB_PATH}")


if __name__ == "__main__":
    main()
