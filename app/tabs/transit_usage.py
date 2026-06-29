import plotly.express as px
import streamlit as st

from app.analytics import oil_transit_dataset
from app.services import safe_load


def render() -> None:
    st.subheader("유가 상승에 따른 대중교통 사용 빈도")
    oil_df = safe_load("oil_prices_monthly")
    transit_df = safe_load("transit_usage_monthly")
    data = oil_transit_dataset(oil_df, transit_df)

    if data.empty:
        st.info("유가와 대중교통 이용 데이터를 먼저 적재하세요.")
        return

    transport_types = sorted(data["transport_type"].dropna().unique())
    selected = st.multiselect("교통수단", transport_types, default=transport_types)
    filtered = data[data["transport_type"].isin(selected)]
    st.plotly_chart(
        px.line(filtered, x="month", y="rides", color="transport_type", markers=True, title="월별 대중교통 이용량"),
        use_container_width=True,
    )
    st.dataframe(filtered, use_container_width=True, hide_index=True)
