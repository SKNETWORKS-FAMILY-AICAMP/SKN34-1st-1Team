# 유가 기반 자동차/교통 분석 Streamlit 앱

Streamlit + MySQL로 아래 3가지 기능을 구현한 VSCode용 프로젝트입니다.

1. 유가 상승에 따른 자동차 구매/등록 변화 통계
2. 유가가 제일 저렴한 주유소 검색
3. 기름값을 아낄 수 있는 자동차 관련 커뮤니티 검색 결과 수집

## 실행 방식

이 프로젝트는 두 가지 방식으로 실행할 수 있습니다.

- 개발/데모 단계: SQLite를 사용해서 MySQL 설치 없이 바로 화면과 기능을 확인합니다.
- 최종/공용 단계: MySQL에 실제 데이터를 적재하고 앱을 MySQL에 연결합니다.

팀 개발 중에는 SQLite 데모 모드로 빠르게 기능을 만들고, 데이터가 확정되면 MySQL로 전환하는 방식을 권장합니다.

## 개발용 SQLite 데모 실행

처음 프로젝트를 받은 팀원은 아래 순서로 바로 실행할 수 있습니다.

```bash
cd /Users/geonwookim/Desktop/skn34_project/SKN34-1st-1Team
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_sqlite.py
python scripts/seed_sample.py
streamlit run app.py
```

SQLite 데모 모드는 `.env`에 아래 설정이 있을 때 동작합니다.

```env
DB_BACKEND=sqlite
SQLITE_PATH=data_samples/demo.sqlite3
```

이 방식은 MySQL 없이도 개발을 시작하기 위한 용도입니다. 화면 개발, 필터, 그래프, 기본 기능 확인에 사용합니다.

## 최종 MySQL 실행

최종 개발/발표 환경에서는 MySQL을 사용합니다. `.env`에서 SQLite 설정을 삭제하거나 주석 처리합니다.

```env
# DB_BACKEND=sqlite
# SQLITE_PATH=data_samples/demo.sqlite3
```

그리고 MySQL 접속 정보를 입력합니다.

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=본인_MySQL_비밀번호
MYSQL_DATABASE=oil_car_app
OPINET_API_KEY=운영자가_내장할_오피넷_API_KEY
```

MySQL DB와 테이블을 생성합니다.

```bash
mysql -u root -p < sql/schema.sql
```
---추가--- 크롤링 데이터 json파일생성
```bash
python app/crawling_total_used.py
```

---추가--- csv데이터 적재
```bash
python scripts/load_csv_to_db.py data/processed/transit_usage.csv transit_usage --if-exists replace
python scripts/load_csv_to_db.py data/processed/gas_sales.csv gas_sales --if-exists replace
```

샘플 데이터를 넣고 실행합니다.

```bash
python scripts/seed_sample.py
streamlit run app.py
```

실제 서비스용 데이터가 준비되면 `oil_prices_monthly`, `car_sales_monthly`, `transit_usage_monthly`, `gas_stations` 테이블에 데이터를 미리 적재한 뒤 앱을 실행합니다.


## CSV 데이터 관리

앱 화면에서는 CSV 업로드 기능을 제공하지 않습니다. 대신 CSV/XLSX 파일을 프로젝트 폴더에서 관리하고, 스크립트로 DB에 적재합니다.

폴더 구조:

```text
data/
  raw/        # 원본 CSV/XLSX 보관
  processed/  # DB 컬럼에 맞게 정리한 CSV 보관
```

권장 파일명:

```text
data/processed/oil_prices_monthly.csv
data/processed/car_sales_monthly.csv
data/processed/transit_usage_monthly.csv
data/processed/gas_stations.csv
```

CSV를 현재 `.env`가 가리키는 DB에 넣는 방법:

```bash
python scripts/load_csv_to_db.py data/processed/oil_prices_monthly.csv oil_prices_monthly
python scripts/load_csv_to_db.py data/processed/car_sales_monthly.csv car_sales_monthly
python scripts/load_csv_to_db.py data/processed/transit_usage_monthly.csv transit_usage_monthly
python scripts/load_csv_to_db.py data/processed/gas_stations.csv gas_stations
```

원본 파일 컬럼을 확인하거나 빈 processed CSV 템플릿을 만들 때:

```bash
python scripts/normalize_data.py car_sales_monthly --input data/raw/source.xlsx
python scripts/normalize_data.py car_sales_monthly --output data/processed/car_sales_monthly.csv
```

테이블별 컬럼 설명은 `docs/data_dictionary.md`를 확인합니다.


## 커밋 기준

커밋해야 하는 파일:

- `app.py`
- `app/`
- `sql/schema.sql`
- `sql/sqlite_schema.sql`
- `scripts/init_sqlite.py`
- `scripts/seed_sample.py`
- `scripts/load_csv_to_db.py`
- `scripts/normalize_data.py`
- `data/README.md`
- `data/processed/*.csv`
- `docs/`
- `requirements.txt`
- `README.md`
- `.env.example`
- `.gitignore`

커밋하지 않는 파일:

- `.env`
- `.venv/`
- `__pycache__/`
- `data_samples/demo.sqlite3`
- 큰 원본 데이터 파일 또는 재배포 제한이 있는 `data/raw/*` 파일

`demo.sqlite3`는 로컬에서 `python scripts/init_sqlite.py`와 `python scripts/seed_sample.py`로 다시 만들 수 있으므로 Git에 올리지 않습니다.

## 실제 데이터 연결 방법

- 자동차 등록 현황: 공공데이터포털의 `국토교통부_자동차 등록 현황` XLSX를 내려받아 월별/연료별 형태로 정리한 뒤 `car_sales_monthly`에 적재합니다.
- 자동차 판매 실적: 다나와 자동차 판매실적 페이지에서 CSV/XLSX로 정리해 `car_sales_monthly`에 적재합니다. 페이지 구조가 바뀔 수 있어 앱은 미리 적재된 DB 데이터를 조회하는 방식을 기본으로 둡니다.
- 주유소 가격: 운영자가 앱 환경변수 `OPINET_API_KEY`에 키를 내장하면 앱에서 `lowTop10.do` API를 호출합니다. 키가 없는 개발/데모 환경에서는 `gas_stations` 테이블에 저장된 데이터를 조회합니다.
- 대중교통 이용량: 공공데이터포털/교통카드 통계 등을 월별 `transport_type`, `rides` 컬럼으로 정리해 `transit_usage_monthly`에 적재합니다.
- 커뮤니티 검색: 공개 검색 결과의 제목/URL/요약만 저장합니다. 사이트별 약관과 robots.txt를 확인하고, 본문 대량 수집은 피하는 구조로 시작하는 것이 좋습니다.

## 주요 파일

- `app.py`: Streamlit 화면과 3개 탭
- `app/db.py`: MySQL 연결
- `app/analytics.py`: 유가-자동차, 유가-대중교통 분석용 데이터 가공
- `app/sources.py`: Opinet API와 공개 검색 수집
- `sql/schema.sql`: MySQL 스키마
- `scripts/seed_sample.py`: 데모용 샘플 데이터 적재
- `scripts/load_csv_to_db.py`: CSV/XLSX를 DB에 적재
- `scripts/normalize_data.py`: 원본 데이터 컬럼 확인과 processed 템플릿 생성
- `data/`: 원본/정리 CSV 관리
- `docs/data_dictionary.md`: 테이블별 컬럼 설명

## DB 적재 컬럼 예시

`oil_prices_monthly`

```csv
month,sido,product,avg_price
2025-01-01,서울,gasoline,1690
```

`car_sales_monthly`

```csv
month,brand,model,fuel_type,segment,units,avg_fuel_efficiency
2025-01-01,현대,아반떼,가솔린,준중형,1234,14.8
```

`transit_usage_monthly`

```csv
month,sido,transport_type,rides
2025-01-01,서울,지하철,207000000
```
