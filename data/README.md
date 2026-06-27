# 데이터 폴더 안내

이 폴더는 앱에 넣을 CSV/XLSX 데이터를 관리하는 곳입니다.

## 폴더 구분

- `raw/`: 공공데이터, 다나와, 교통 데이터 등 원본 파일을 그대로 보관합니다.
- `processed/`: 앱 DB 테이블 컬럼에 맞게 정리한 CSV 파일을 보관합니다.

## 권장 파일명

- `processed/oil_prices_monthly.csv`
- `processed/car_sales_monthly.csv`
- `processed/transit_usage_monthly.csv`
- `processed/gas_stations.csv`

## DB 적재

정리된 CSV는 아래 스크립트로 현재 `.env`가 가리키는 DB에 넣습니다.

```bash
python scripts/load_csv_to_db.py data/processed/oil_prices_monthly.csv oil_prices_monthly
```

`.env`가 SQLite 모드면 SQLite에 들어가고, SQLite 설정을 지우면 MySQL에 들어갑니다.

## 주의

원본 데이터가 너무 크거나 재배포 제한이 있으면 `raw/` 파일은 Git에 올리지 말고 출처와 다운로드 방법만 문서화합니다.
