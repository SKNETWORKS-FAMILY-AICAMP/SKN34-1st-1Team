import streamlit as st

from app.tabs import car_purchase, community_search, gas_stations


st.set_page_config(page_title="유가 기반 자동차/교통 분석", layout="wide")
st.title("FuelMate-주유 도우미")

MENU_ITEMS = {
    "car": "자동차 구매 변화",
    "station": "저렴한 주유소",
    "community": "커뮤니티 검색",
}


def query_page() -> str:
    page = st.query_params.get("page", "car")
    if isinstance(page, list):
        page = page[0] if page else "car"
    return page if page in MENU_ITEMS else "car"


def set_page(page: str) -> None:
    st.session_state["page"] = page
    st.query_params["page"] = page


def render_sidebar_nav() -> str:
    if "page" not in st.session_state:
        st.session_state["page"] = query_page()

    st.sidebar.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background: #f8fafc;
                border-right: 1px solid #e5e7eb;
            }

            .side-nav-title {
                color: #0f172a;
                font-size: 1.35rem;
                font-weight: 750;
                margin: 0.35rem 0 0.85rem;
            }

            section[data-testid="stSidebar"] div.stButton > button {
                justify-content: flex-start;
                min-height: 2.85rem;
                border-radius: 8px;
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="side-nav-title">Contents</div>', unsafe_allow_html=True)

    for key, label in MENU_ITEMS.items():
        is_active = st.session_state["page"] == key
        st.sidebar.button(
            label,
            key=f"nav_{key}",
            on_click=set_page,
            args=(key,),
            type="primary" if is_active else "secondary",
            use_container_width=True,
        )

    return st.session_state["page"]


page = render_sidebar_nav()

if page == "car":
    car_purchase.render()
elif page == "station":
    gas_stations.render()
else:
    community_search.render()
