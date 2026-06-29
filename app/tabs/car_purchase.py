import plotly.express as px
import streamlit as st

from app.analytics import oil_car_dataset
from app.services import safe_load


def render() -> None:
    st.subheader("유가 상승에 따른 자동차 구매 변화")
    oil_df = safe_load("oil_prices_monthly")
    car_df = safe_load("car_sales_monthly")
    data = oil_car_dataset(oil_df, car_df)

    if data.empty:
        st.info("유가와 자동차 판매/등록 데이터를 먼저 적재하세요.")
        return

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
