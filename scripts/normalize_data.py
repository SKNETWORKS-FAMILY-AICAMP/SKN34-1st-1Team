import argparse
from pathlib import Path

import pandas as pd

TEMPLATES = {
    "oil_prices_monthly": ["month", "sido", "product", "avg_price"],
    "car_sales_monthly": ["month", "brand", "model", "fuel_type", "segment", "units", "avg_fuel_efficiency"],
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
}


def read_input(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Only CSV/XLSX files are supported.")


def create_template(table: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=TEMPLATES[table]).to_csv(output, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create processed CSV templates or inspect raw data columns.")
    parser.add_argument("table", choices=sorted(TEMPLATES), help="Target table template")
    parser.add_argument("--input", type=Path, help="Optional raw CSV/XLSX to inspect")
    parser.add_argument("--output", type=Path, help="Output processed CSV template path")
    args = parser.parse_args()

    if args.input:
        df = read_input(args.input)
        print("Input columns:")
        for col in df.columns:
            print(f"- {col}")
        print("\nRequired processed columns:")
        for col in TEMPLATES[args.table]:
            print(f"- {col}")

    if args.output:
        create_template(args.table, args.output)
        print(f"Wrote template: {args.output}")

    if not args.input and not args.output:
        print("Required processed columns:")
        for col in TEMPLATES[args.table]:
            print(f"- {col}")


if __name__ == "__main__":
    main()
