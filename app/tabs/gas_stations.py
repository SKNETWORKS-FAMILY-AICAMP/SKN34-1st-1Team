import pandas as pd
import streamlit as st

from app.services import safe_load, show_gas_stations
from app.sources import fetch_opinet_avg_all_price, fetch_opinet_low_top10, opinet_api_key


PRODUCT_CODES = {"휘발유": "B027", "경유": "D047", "고급휘발유": "B034"}
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
}


def render() -> None:
    st.subheader("유가가 제일 저렴한 주유소 찾기")
    key = opinet_api_key()

    cola, colb = st.columns(2)
    with cola:
        product = st.selectbox("유종", PRODUCT_CODES.keys(), key="gas_station_product")
    with colb:
        area = st.selectbox("지역", AREA_CODES.keys(), key="gas_station_area")

    product_code = PRODUCT_CODES[product]
    avg_prices = _load_average_prices(key, product_code)

    if key:
        _render_opinet_station_search(key, product_code, AREA_CODES[area], avg_prices)
    else:
        _render_saved_station_search()


def _load_average_prices(key: str, product_code: str) -> pd.DataFrame:
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

    return avg_prices


def _render_opinet_station_search(key: str, product_code: str, area_code: str, avg_prices: pd.DataFrame) -> None:
    if "opinet_station_results" not in st.session_state:
        st.session_state["opinet_station_results"] = pd.DataFrame()

    if st.button("저렴한 주유소 조회", key="search_opinet_stations"):
        try:
            stations = fetch_opinet_low_top10(key, product_code=product_code, area_code=area_code)
            if not stations.empty:
                selected_avg = avg_prices[avg_prices["product_code"] == product_code] if not avg_prices.empty else pd.DataFrame()
                if not selected_avg.empty and "gasoline_price" in stations.columns:
                    avg_price = selected_avg["avg_price"].iloc[0]
                    stations["national_avg_gap"] = stations["gasoline_price"] - avg_price
            st.session_state["opinet_station_results"] = stations
        except Exception as exc:
            st.error(f"주유소 조회에 실패했습니다: {exc}")

    stations = st.session_state.get("opinet_station_results", pd.DataFrame())
    if stations.empty:
        st.info("조회된 주유소가 없습니다.")
    else:
        show_gas_stations(stations, "조회된 주유소가 없습니다.", map_key="opinet_gas_stations_map")


def _render_saved_station_search() -> None:
    stations = safe_load("gas_stations")
    if stations.empty:
        st.info("주유소 데이터를 먼저 적재하세요.")
        return

    sido_options = ["전체"] + sorted(stations["sido"].dropna().unique())
    sido = st.selectbox("시도", sido_options, key="saved_station_sido")
    filtered = stations if sido == "전체" else stations[stations["sido"] == sido]
    keyword = st.text_input("주소/주유소명 검색", key="saved_station_keyword")
    if keyword:
        mask = (
            filtered["station_name"].fillna("").str.contains(keyword, case=False)
            | filtered["address"].fillna("").str.contains(keyword, case=False)
        )
        filtered = filtered[mask]
    filtered = filtered.sort_values("gasoline_price", na_position="last").head(30)
    show_gas_stations(filtered, "표시할 주유소가 없습니다.")
