import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from streamlit_folium import st_folium

from app.analytics import oil_car_dataset, oil_transit_dataset
from app.db import get_engine, read_sql
from app.map import build_gas_stations_map
from app.sources import fetch_opinet_avg_all_price, fetch_opinet_low_top10, opinet_api_key, search_community_posts


st.set_page_config(page_title="유가 기반 자동차/교통 분석", layout="wide")


@st.cache_data(ttl=60)
def load_table(table_name: str) -> pd.DataFrame:
    return read_sql(f"SELECT * FROM {table_name}")


def save_dataframe(df: pd.DataFrame, table_name: str) -> None:
    with get_engine().begin() as conn:
        df.to_sql(table_name, conn, if_exists="append", index=False)


def safe_load(table_name: str) -> pd.DataFrame:
    try:
        return load_table(table_name)
    except SQLAlchemyError as exc:
        st.error("MySQL 연결 또는 테이블 초기화가 필요합니다. README의 설정 순서를 확인하세요.")
        st.caption(str(exc))
        return pd.DataFrame()


def show_gas_stations(stations: pd.DataFrame, empty_message: str) -> None:
    if stations.empty:
        st.info(empty_message)
        return
    col1, col2 = st.columns(2)
    with col1:
        folium_map = build_gas_stations_map(stations)
        if folium_map is not None:
            st_folium(folium_map, width=None, height=600, returned_objects=[])
        else:
            st.caption("지도에 표시할 좌표가 없습니다.")
    with col2:
        st.dataframe(stations, use_container_width=True, hide_index=True)


st.title("유가 기반 자동차 구매, 주유소, 대중교통, 커뮤니티 분석")

tab1, tab2, tab3, tab4 = st.tabs(
    ["자동차 구매 변화", "저렴한 주유소", "대중교통 이용", "커뮤니티 검색"]
)

with tab1:
    st.subheader("유가 상승에 따른 자동차 구매 변화")
    oil_df = safe_load("oil_prices_monthly")
    car_df = safe_load("car_sales_monthly")
    data = oil_car_dataset(oil_df, car_df)

    if data.empty:
        st.info("유가와 자동차 판매/등록 데이터를 먼저 적재하세요.")
    else:
        fuel_types = sorted(data["fuel_type"].dropna().unique())
        selected = st.multiselect("연료 유형", fuel_types, default=fuel_types)
        filtered = data[data["fuel_type"].isin(selected)]

        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.line(filtered, x="month", y="units", color="fuel_type", markers=True, title="월별 자동차 구매/등록 대수"),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                px.line(filtered, x="month", y="avg_price", color="fuel_type", markers=True, title="월평균 유가"),
                use_container_width=True,
            )

        st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("유가가 제일 저렴한 주유소 찾기")
    key = opinet_api_key()

    PRODUCT_CODES = {"휘발유": "B027", "경유": "D047", "고급휘발유": "B034"}  # 유종 Opinet 코드
    AREA_CODES = {
        "전체": "",
        "서울특별시": "01",
        "경기도": "02",
        "강원특별자치도": "03",
        "충청북도": "04",
        "충청남도": "05",
        "전북특별자치도": "06",
        "전라남도": "07",
        "경상북도": "08",
        "경상남도": "09",
        "부산광역시": "10",
        "제주특별자치도": "11",
        "대구광역시": "14",
        "인천광역시": "15",
        "광주광역시": "16",
        "대전광역시": "17",
        "울산광역시": "18",
        "세종특별자치시": "19",
    }  # Opinet 지역 코드
    cola,colb= st.columns(2)
    with cola:
        product = st.selectbox("유종", PRODUCT_CODES.keys())
    with colb:
        area = st.selectbox("지역", AREA_CODES.keys())
    
    cnt = 20 # 주유소 조회 개수

    product_options = {"휘발유": "B027", "경유": "D047", "고급휘발유": "B034"}
    selected_product = st.selectbox("유종", list(product_options.keys()))
    product_code = product_options[selected_product]

    avg_prices = pd.DataFrame()
    if key:
        try:
            avg_prices = fetch_opinet_avg_all_price(key)
        except Exception as exc:
            st.warning(f"전국 평균 유가 조회에 실패했습니다: {exc}")

    if key and avg_prices.empty:
        st.info("전국 평균 유가 데이터가 조회되지 않았습니다. Opinet 응답 또는 API 권한을 확인하세요.")

    if not avg_prices.empty:
        trade_date = avg_prices["trade_date"].dropna().max()
        if pd.notna(trade_date):
            st.caption(f"전국 평균 유가 기준일: {trade_date:%Y-%m-%d}")

        metric_cols = st.columns(min(len(avg_prices), 5))
        for col, (_, row) in zip(metric_cols, avg_prices.iterrows()):
            diff_value = row["diff"]
            avg_price_value = row["avg_price"]
            delta = None if pd.isna(diff_value) else f"{diff_value:+.2f}원"
            col.metric(row["product_name"], f"{avg_price_value:,.2f}원", delta=delta)

        selected_avg = avg_prices[avg_prices["product_code"] == product_code]
        if not selected_avg.empty:
            selected_avg_price = selected_avg["avg_price"].iloc[0]
            st.caption(f"선택 유종 전국 평균: {selected_avg_price:,.2f}원")


    if key:
        area_code = st.text_input("지역 코드", placeholder="예: 서울 01, 경기 02 등 Opinet 코드")
        if st.button("저렴한 주유소 조회"):
            try:

                stations = fetch_opinet_low_top10(key, product_code=PRODUCT_CODES[product], area_code=AREA_CODES[area])
                show_gas_stations(stations, "조회된 주유소가 없습니다.")
                stations = fetch_opinet_low_top10(key, product_code=product_code, area_code=area_code)
                if stations.empty:
                    st.info("조회된 주유소가 없습니다.")
                else:
                    selected_avg = avg_prices[avg_prices["product_code"] == product_code] if not avg_prices.empty else pd.DataFrame()
                    if not selected_avg.empty and "gasoline_price" in stations.columns:
                        avg_price = selected_avg["avg_price"].iloc[0]
                        stations["national_avg_gap"] = stations["gasoline_price"] - avg_price
                    st.dataframe(stations, use_container_width=True, hide_index=True)

            except Exception as exc:
                st.error(f"주유소 조회에 실패했습니다: {exc}")
    else:
        stations = safe_load("gas_stations")
        if stations.empty:
            st.info("주유소 데이터를 먼저 적재하세요.")
        else:
            sido_options = ["전체"] + sorted(stations["sido"].dropna().unique())
            sido = st.selectbox("시도", sido_options)
            filtered = stations if sido == "전체" else stations[stations["sido"] == sido]
            keyword = st.text_input("주소/주유소명 검색")
            if keyword:
                mask = (
                    filtered["station_name"].fillna("").str.contains(keyword, case=False)
                    | filtered["address"].fillna("").str.contains(keyword, case=False)
                )
                filtered = filtered[mask]
            filtered = filtered.sort_values("gasoline_price", na_position="last").head(30)
            show_gas_stations(filtered, "표시할 주유소가 없습니다.")

with tab3:
    st.subheader("유가 상승에 따른 대중교통 사용 빈도")
    oil_df = safe_load("oil_prices_monthly")
    transit_df = safe_load("transit_usage_monthly")
    data = oil_transit_dataset(oil_df, transit_df)

    if data.empty:
        st.info("유가와 대중교통 이용 데이터를 먼저 적재하세요.")
    else:
        transport_types = sorted(data["transport_type"].dropna().unique())
        selected = st.multiselect("교통수단", transport_types, default=transport_types)
        filtered = data[data["transport_type"].isin(selected)]
        st.plotly_chart(
            px.line(filtered, x="month", y="rides", color="transport_type", markers=True, title="월별 대중교통 이용량"),
            use_container_width=True,
        )
        st.dataframe(filtered, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("기름값을 아낄 수 있는 자동차 커뮤니티 검색")
    keyword = st.text_input("검색어", value="연비 좋은 차")
    col1, col2 = st.columns([1, 4])
    with col1:
        do_search = st.button("검색/크롤링")
    if do_search:
        try:
            posts = search_community_posts(keyword)
            if not posts.empty:
                save_dataframe(posts, "community_posts")
                st.cache_data.clear()
            st.success(f"{len(posts):,}건을 수집했습니다.")
        except Exception as exc:
            st.error(f"검색 수집에 실패했습니다: {exc}")

    posts = safe_load("community_posts")
    if posts.empty:
        st.info("검색 버튼을 눌러 공개 웹 검색 결과를 수집하세요.")
    else:
        for _, row in posts.sort_values("crawled_at", ascending=False).head(30).iterrows():
            st.markdown(f"**[{row['title']}]({row['url']})**")
            st.caption(f"{row.get('source', '')} · {row.get('keyword', '')} · {row.get('crawled_at', '')}")
            if row.get("snippet"):
                st.write(row["snippet"])
            st.divider()
