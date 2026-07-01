import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.analytics import gas_sales_table, prepare_gas_sales, prepare_transit_usage
from app.services import load_total_use_json, safe_load

GAS_TABLE_COLUMNS = {
    "month": "년/월",
    "normal_gasoline": "휘발유(원)",
    "diesel": "경유(원)",
}

PRODUCT_COLORS = {
    "휘발유": "#F4C430",
    "경유": "#2E8B57",
}

def _format_gas_table(df: pd.DataFrame) -> pd.DataFrame:
    display = df.sort_values("month", ascending=False).copy()
    display["month"] = display["month"].dt.strftime("%Y-%m")
    display["normal_gasoline"] = display["normal_gasoline"].map(lambda v: f"{v:,.2f}")
    display["diesel"] = display["diesel"].map(lambda v: f"{v:,.2f}")
    return display.rename(columns=GAS_TABLE_COLUMNS)


def _build_gas_transit_chart(gas_long: pd.DataFrame, transit_data: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for product in gas_long["product"].dropna().unique():
        subset = gas_long[gas_long["product"] == product]
        color = PRODUCT_COLORS.get(product)
        fig.add_trace(
            go.Scatter(
                x=subset["month"],
                y=subset["avg_price"],
                name=product,
                mode="lines+markers",
                line=dict(color=color),
                marker=dict(color=color),
            ),
            secondary_y=False,
        )

    if not transit_data.empty:
        fig.add_trace(
            go.Bar(
                x=transit_data["month"],
                y=transit_data["used"],
                name="교통카드 이용",
                opacity=0.35,
                marker_color="rgba(100, 149, 237, 0.6)",
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title="월별 유가 및 교통카드 이용",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="월")
    fig.update_yaxes(title_text="가격(원)", secondary_y=False)
    fig.update_yaxes(title_text="이용(건)", secondary_y=True)
    return fig


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

    gas_df = safe_load("gas_sales")
    transit_df = safe_load("transit_usage")

    gas_long = prepare_gas_sales(gas_df)
    gas_table = gas_sales_table(gas_df)
    transit_data = prepare_transit_usage(transit_df)
    if gas_long.empty:
        st.info("유가 데이터를 먼저 적재하세요.")
        st.caption("python scripts/load_csv_to_db.py data/processed/gas_sales.csv gas_sales")
        col1, col2 = st.columns([4, 3])
        with col2:
            total_use = load_total_use_json()
            if total_use:
                container = st.container(border=True)
                with container:
                    _render_total_use_panel(total_use)
            else:
                st.info("교통카드 이용 데이터가 없습니다.")
        return

    products = sorted(gas_long["product"].dropna().unique())
    gas_filtered = gas_long[gas_long["product"].isin(products)]

    st.plotly_chart(
        _build_gas_transit_chart(gas_filtered, transit_data),
        use_container_width=True,
    )
    col1, col2 = st.columns([4, 3])
    with col1:
        st.dataframe(_format_gas_table(gas_table), use_container_width=True, hide_index=True)

    with col2:
        total_use = load_total_use_json()
        if total_use:
            container = st.container(border=True)
            with container:
                _render_total_use_panel(total_use)
        else:
            st.info("교통카드 이용 데이터가 없습니다.")

    
