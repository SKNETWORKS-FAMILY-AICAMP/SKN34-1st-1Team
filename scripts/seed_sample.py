from datetime import datetime
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_engine


def month_range():
    return pd.date_range("2024-01-01", "2025-12-01", freq="MS")


def seed_oil_prices() -> pd.DataFrame:
    prices = [
        1580, 1605, 1630, 1680, 1710, 1745, 1720, 1760, 1810, 1790, 1755, 1730,
        1690, 1665, 1700, 1740, 1795, 1840, 1865, 1830, 1805, 1770, 1745, 1715,
    ]
    return pd.DataFrame(
        {
            "month": month_range(),
            "sido": "서울",
            "product": "gasoline",
            "avg_price": prices,
        }
    )


def seed_car_sales() -> pd.DataFrame:
    rows = []
    fuels = {
        "가솔린": [9100, 8900, 8700, 8400, 8100, 7800, 7900, 7600, 7200, 7350, 7600, 7850,
                8000, 8150, 7900, 7600, 7100, 6800, 6500, 6700, 7000, 7300, 7550, 7800],
        "하이브리드": [4200, 4350, 4600, 4900, 5150, 5400, 5500, 5700, 6100, 6000, 5850, 5700,
                 5800, 6000, 6250, 6500, 6900, 7200, 7450, 7350, 7100, 6900, 6750, 6600],
        "전기": [2100, 2250, 2400, 2550, 2700, 2900, 3000, 3150, 3300, 3400, 3500, 3600,
               3700, 3850, 4000, 4150, 4300, 4450, 4600, 4700, 4800, 4900, 5000, 5100],
    }
    for fuel, units in fuels.items():
        for month, unit in zip(month_range(), units):
            rows.append(
                {
                    "month": month,
                    "brand": "샘플",
                    "model": f"{fuel} 대표 모델",
                    "fuel_type": fuel,
                    "segment": "중형",
                    "units": unit,
                    "avg_fuel_efficiency": {"가솔린": 12.5, "하이브리드": 18.4, "전기": None}[fuel],
                }
            )
    return pd.DataFrame(rows)


def seed_transit() -> pd.DataFrame:
    rows = []
    bus = [
        142000000, 141500000, 143000000, 146000000, 149000000, 151000000, 150000000, 152000000,
        156000000, 155000000, 153000000, 151000000, 150000000, 149000000, 151500000, 154000000,
        158000000, 161000000, 163000000, 162000000, 160000000, 158000000, 156000000, 154500000,
    ]
    subway = [
        198000000, 197500000, 199000000, 202000000, 205000000, 207000000, 206000000, 209000000,
        214000000, 213000000, 211000000, 208000000, 207000000, 206000000, 209000000, 212000000,
        217000000, 221000000, 224000000, 222000000, 220000000, 217000000, 214000000, 212000000,
    ]
    for transport_type, rides in {"버스": bus, "지하철": subway}.items():
        for month, ride in zip(month_range(), rides):
            rows.append(
                {
                    "month": month,
                    "sido": "서울",
                    "transport_type": transport_type,
                    "rides": ride,
                }
            )
    return pd.DataFrame(rows)


def seed_stations() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "station_code": "SAMPLE-001",
                "station_name": "샘플에너지 강남",
                "brand": "알뜰",
                "sido": "서울",
                "sigungu": "강남구",
                "address": "서울 강남구 테헤란로 1",
                "latitude": 37.4979,
                "longitude": 127.0276,
                "gasoline_price": 1688,
                "diesel_price": 1510,
                "updated_at": datetime.now(),
            },
            {
                "station_code": "SAMPLE-002",
                "station_name": "샘플주유소 서초",
                "brand": "자가상표",
                "sido": "서울",
                "sigungu": "서초구",
                "address": "서울 서초구 반포대로 10",
                "latitude": 37.4837,
                "longitude": 127.0324,
                "gasoline_price": 1695,
                "diesel_price": 1522,
                "updated_at": datetime.now(),
            },
        ]
    )


def main():
    data = {
        "oil_prices_monthly": seed_oil_prices(),
        "car_sales_monthly": seed_car_sales(),
        "transit_usage_monthly": seed_transit(),
        "gas_stations": seed_stations(),
    }
    with get_engine().begin() as conn:
        for table, df in data.items():
            existing = pd.read_sql(f"SELECT COUNT(*) AS count FROM {table}", conn)["count"].iloc[0]
            if existing:
                print(f"Skipped {table}: already has {existing} rows")
                continue
            df.to_sql(table, conn, if_exists="append", index=False)
            print(f"Inserted {len(df)} rows into {table}")


if __name__ == "__main__":
    main()
