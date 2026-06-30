import json
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from streamlit_folium import st_folium

from app.db import get_engine, read_sql
from app.map import build_gas_stations_map

ROOT = Path(__file__).resolve().parents[1]
TOTAL_USE_JSON = ROOT / "data" / "processed" / "total_use_text.json"


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


@st.cache_data(ttl=60)
def load_total_use_json() -> dict | None:
    if not TOTAL_USE_JSON.exists():
        return None
    return json.loads(TOTAL_USE_JSON.read_text(encoding="utf-8"))


def show_gas_stations(stations: pd.DataFrame, empty_message: str, map_key: str = "gas_stations_map") -> None:
    if stations.empty:
        st.info(empty_message)
        return

    col1, col2 = st.columns(2)
    with col1:
        folium_map = build_gas_stations_map(stations)
        if folium_map is not None:
            st_folium(folium_map, width=None, height=600, returned_objects=[], key=map_key)
        else:
            st.caption("지도에 표시할 좌표가 없습니다.")
    with col2:
        st.dataframe(stations, use_container_width=True, hide_index=True)
