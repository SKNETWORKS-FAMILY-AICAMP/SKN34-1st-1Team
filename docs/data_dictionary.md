# 데이터 사전

앱에서 사용하는 DB 테이블과 CSV 컬럼 정의입니다.

## oil_prices_monthly

월별/지역별 평균 유가입니다.

| 컬럼 | 설명 | 예시 |
| --- | --- | --- |
| month | 월 시작일 | 2025-01-01 |
| sido | 시도 | 서울 |
| product | 유종 | gasoline |
| avg_price | 평균 가격 | 1690 |

## car_sales_monthly

월별 자동차 판매 또는 등록 데이터입니다.

| 컬럼 | 설명 | 예시 |
| --- | --- | --- |
| month | 월 시작일 | 2025-01-01 |
| brand | 브랜드 | 현대 |
| model | 모델명 | 아반떼 |
| fuel_type | 연료 유형 | 가솔린 |
| segment | 차급 | 준중형 |
| units | 판매/등록 대수 | 1234 |
| avg_fuel_efficiency | 평균 연비 | 14.8 |

## transit_usage_monthly

월별 대중교통 이용량입니다.

| 컬럼 | 설명 | 예시 |
| --- | --- | --- |
| month | 월 시작일 | 2025-01-01 |
| sido | 시도 | 서울 |
| transport_type | 교통수단 | 지하철 |
| rides | 이용 건수 | 207000000 |

## gas_stations

주유소 가격 데이터입니다.

| 컬럼 | 설명 | 예시 |
| --- | --- | --- |
| station_code | 주유소 코드 | S001 |
| station_name | 주유소명 | 샘플주유소 |
| brand | 브랜드 | 알뜰 |
| sido | 시도 | 서울 |
| sigungu | 시군구 | 강남구 |
| address | 주소 | 서울 강남구 테헤란로 1 |
| latitude | 위도 | 37.4979 |
| longitude | 경도 | 127.0276 |
| gasoline_price | 휘발유 가격 | 1688 |
| diesel_price | 경유 가격 | 1510 |
| updated_at | 갱신 시각 | 2026-06-27 12:00:00 |
