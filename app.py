import streamlit as st

from app.tabs import car_purchase, community_search, gas_stations, transit_usage


st.set_page_config(page_title="유가 기반 자동차/교통 분석", layout="wide")
st.title("유가 기반 자동차 구매, 주유소, 대중교통, 커뮤니티 분석")

car_tab, station_tab, transit_tab, community_tab = st.tabs(
    ["자동차 구매 변화", "저렴한 주유소", "대중교통 이용", "커뮤니티 검색"]
)

with car_tab:
    car_purchase.render()

with station_tab:
    gas_stations.render()

with transit_tab:
    transit_usage.render()

with community_tab:
    community_search.render()
