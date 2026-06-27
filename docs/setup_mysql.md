# MySQL 전환 방법

SQLite 데모 개발이 끝난 뒤 MySQL로 전환할 때의 절차입니다.

## 1. MySQL 서버 실행

각자 PC에 MySQL 서버가 설치되어 있고 실행 중이어야 합니다.

## 2. `.env` 수정

SQLite 설정을 삭제하거나 주석 처리합니다.

```env
# DB_BACKEND=sqlite
# SQLITE_PATH=data_samples/demo.sqlite3
```

MySQL 접속 정보를 입력합니다.

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=본인_MySQL_비밀번호
MYSQL_DATABASE=oil_car_app
OPINET_API_KEY=
```

## 3. 스키마 생성

```bash
mysql -u root -p < sql/schema.sql
```

## 4. 데이터 적재

샘플 데이터를 넣을 때:

```bash
python scripts/seed_sample.py
```

CSV를 넣을 때:

```bash
python scripts/load_csv_to_db.py data/processed/oil_prices_monthly.csv oil_prices_monthly
```

## 5. 앱 실행

```bash
streamlit run app.py
```
