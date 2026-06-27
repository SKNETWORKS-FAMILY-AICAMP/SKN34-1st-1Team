import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db import get_engine

TABLE_COLUMNS = {
    "oil_prices_monthly": ["month", "sido", "product", "avg_price"],
    "car_sales_monthly": [
        "month",
        "brand",
        "model",
        "fuel_type",
        "segment",
        "units",
        "avg_fuel_efficiency",
    ],
    "transit_usage_monthly": ["month", "sido", "transport_type", "rides"],
    "gas_stations": [
        "station_code",
        "station_name",
        "brand",
        "sido",
        "sigungu",
        "address",
        "latitude",
        "longitude",
        "gasoline_price",
        "diesel_price",
        "updated_at",
    ],
    "community_posts": ["source", "title", "url", "snippet", "keyword", "published_at", "crawled_at"],
}

DATE_COLUMNS = {
    "oil_prices_monthly": ["month"],
    "car_sales_monthly": ["month"],
    "transit_usage_monthly": ["month"],
    "gas_stations": ["updated_at"],
    "community_posts": ["published_at", "crawled_at"],
}

NUMERIC_COLUMNS = {
    "oil_prices_monthly": ["avg_price"],
    "car_sales_monthly": ["units", "avg_fuel_efficiency"],
    "transit_usage_monthly": ["rides"],
    "gas_stations": ["latitude", "longitude", "gasoline_price", "diesel_price"],
}


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Only CSV/XLSX files are supported.")


def normalize_dataframe(df: pd.DataFrame, table: str) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    required = TABLE_COLUMNS[table]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for {table}: {missing}")

    df = df[required]

    for col in DATE_COLUMNS.get(table, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in NUMERIC_COLUMNS.get(table, []):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.where(pd.notna(df), None)


def load_csv(path: Path, table: str, if_exists: str) -> int:
    if table not in TABLE_COLUMNS:
        valid = ", ".join(TABLE_COLUMNS)
        raise ValueError(f"Unknown table: {table}. Valid tables: {valid}")

    df = normalize_dataframe(read_table(path), table)
    with get_engine().begin() as conn:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
    return len(df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load CSV/XLSX data into the configured SQLite or MySQL database.")
    parser.add_argument("path", type=Path, help="CSV/XLSX file path")
    parser.add_argument("table", choices=sorted(TABLE_COLUMNS), help="Target DB table")
    parser.add_argument(
        "--if-exists",
        choices=["append", "replace", "fail"],
        default="append",
        help="pandas.to_sql behavior when table already exists",
    )
    args = parser.parse_args()

    if not args.path.exists():
        raise FileNotFoundError(args.path)

    count = load_csv(args.path, args.table, args.if_exists)
    print(f"Loaded {count} rows into {args.table} from {args.path}")


if __name__ == "__main__":
    main()
