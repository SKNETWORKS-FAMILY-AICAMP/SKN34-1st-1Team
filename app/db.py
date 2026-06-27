import os
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def mysql_url() -> str:
    user = os.getenv("MYSQL_USER", "root")
    password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "oil_car_app")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def database_url() -> str:
    if os.getenv("DB_BACKEND", "").lower() == "sqlite":
        db_path = Path(os.getenv("SQLITE_PATH", "data_samples/demo.sqlite3"))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"
    return mysql_url()


def get_engine():
    return create_engine(database_url(), pool_pre_ping=True)


def read_sql(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})


def execute_sql(query: str, params: Optional[dict] = None) -> None:
    with get_engine().begin() as conn:
        conn.execute(text(query), params or {})
