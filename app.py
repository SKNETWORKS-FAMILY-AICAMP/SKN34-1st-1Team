import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from app.analytics import oil_car_dataset, oil_transit_dataset
from app.db import get_engine, read_sql
from app.sources import fetch_opinet_low_top10, opinet_api_key, search_community_posts


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
    product = st.selectbox("유종", {"휘발유": "B027", "경유": "D047", "고급휘발유": "B034"})
    area_code = st.text_input("지역 코드", placeholder="예: 서울 01, 경기 02 등 Opinet 코드")

    if key:
        if st.button("저렴한 주유소 조회"):
            try:
                stations = fetch_opinet_low_top10(key, product_code=product, area_code=area_code)
                if stations.empty:
                    st.info("조회된 주유소가 없습니다.")
                else:
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
            st.dataframe(filtered, use_container_width=True, hide_index=True)

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
