import pandas as pd
import plotly.express as px
import streamlit as st

from app.analytics import oil_car_dataset
from app.services import load_total_use_json, safe_load


def _format_rate_markdown(rate) -> str:
    if rate is None or pd.isna(rate):
        return "-"
    text = f"{rate:.2f}"
    if rate > 0:
        return f":red[:material/trending_up: {text}%]"
    if rate < 0:
        return f":blue[:material/trending_down: {text}%]"
    return text


def _render_total_use_panel(data: dict) -> None:
    st.markdown("**교통카드 이용 현황**")
    if data.get("date"):
        st.caption(data["date"])

    metric_left, metric_right = st.columns(2)
    pass_count = data.get("pass_count")
    member_count = data.get("member_count")
    metric_left.metric("통행", f"{pass_count:,}건" if pass_count is not None else "-")
    metric_right.metric("이용수", f"{member_count:,}명" if member_count is not None else "-")

    compare = data.get("compare") or {}
    if compare:
        
        for label, item in compare.items():
            rate = item.get("rate")
            value = item.get("value")
            cols = st.columns([1.2, 1.2, 1,1.5]) #여백 1.5 추가
            cols[0].write(label)
            cols[1].markdown(f"{value:,}명" if value is not None else "-")
            cols[2].markdown(_format_rate_markdown(rate))


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
    col1, col2 = st.columns([4,3])
    with col1: # 자동차 구매/등록 대수 테이블
        st.dataframe(filtered, use_container_width=True, hide_index=True)
    
    with col2: # 교통카드 이용 현황
        total_use = load_total_use_json()
        if total_use:
            container = st.container(border=True)
            with container:
                _render_total_use_panel(total_use)
        else:
            st.info("교통카드 이용 데이터가 없습니다.")

    
