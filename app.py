import base64
from pathlib import Path

import streamlit as st

from app.tabs import car_purchase, community_search, gas_stations


ROOT = Path(__file__).resolve().parent
HERO_IMAGE = ROOT / "app" / "assets" / "fuelmate-hero.png"


def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


st.set_page_config(page_title="유가 기반 자동차/교통 분석", layout="wide")

st.markdown(
    """
    <style>
        .app-hero {
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(220px, 340px);
            align-items: center;
            gap: 1.25rem;
            padding: 1.1rem 0 1.35rem;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 1.2rem;
        }

        .app-eyebrow {
            color: #2563eb;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.32rem;
        }

        .app-title {
            color: #111827;
            font-size: 2.45rem;
            font-weight: 850;
            line-height: 1.12;
            letter-spacing: 0;
            margin: 0;
        }

        .app-title-accent {
            color: #2563eb;
        }

        .app-subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-top: 0.45rem;
        }

        .app-hero-visual {
            justify-self: end;
            width: min(100%, 340px);
            aspect-ratio: 16 / 9;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.12);
        }

        @media (max-width: 760px) {
            .app-hero {
                grid-template-columns: 1fr;
            }

            .app-title {
                font-size: 2rem;
            }

            .app-hero-visual {
                justify-self: start;
                width: 100%;
            }
        }
    </style>

    <header class="app-hero">
        <div>
            <div class="app-eyebrow">Smart Fuel Assistant</div>
            <h1 class="app-title">
                <span class="app-title-accent">FuelMate</span>-주유 도우미
            </h1>
            <div class="app-subtitle">유가 흐름, 저렴한 주유소, 커뮤니티 정보를 한곳에서 확인하세요.</div>
        </div>
        <img class="app-hero-visual" src="__HERO_IMAGE__" alt="FuelMate fuel visual" />
    </header>
    """.replace("__HERO_IMAGE__", image_data_uri(HERO_IMAGE)),
    unsafe_allow_html=True,
)

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
