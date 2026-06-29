import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


OPINET_BASE_URL = "https://www.opinet.co.kr/api"


def fetch_opinet_low_top10(api_key: str, product_code: str="B027", area_code: str = "") -> pd.DataFrame:
    """Fetch low-price gas stations from Opinet when an API key is available."""
    type =  {"B027": "휘발유",
             "D047": "경유",
             "B034": "고급휘발유"}
    params = {
        "code": api_key,
        "out": "json",
        "prodcd": product_code,
        "cnt": 20,
    }
    if area_code:
        params["area"] = area_code

    # response = requests.get(f"https://www.opinet.co.kr/api/lowTop10.do?out=json&code=F260626947&prodcd=B027&area=0101&cnt=20", timeout=15)
    response = requests.get(f"{OPINET_BASE_URL}/lowTop10.do", params=params, timeout=15)
    # print(response.text)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("RESULT", {}).get("OIL", [])
    if isinstance(rows, dict):
        rows = [rows]

    normalized = []
    for row in rows:
        normalized.append(
            {
                "station_code": row.get("UNI_ID"),
                "oil_type": type[product_code],
                "station_name": row.get("OS_NM"),
                "brand": row.get("POLL_DIV_CD"),
                "address": row.get("NEW_ADR") or row.get("VAN_ADR"),
                "gasoline_price": pd.to_numeric(row.get("PRICE"), errors="coerce"),
                "gis_x_coor": pd.to_numeric(row.get("GIS_X_COOR"), errors="coerce"),
                "gis_y_coor": pd.to_numeric(row.get("GIS_Y_COOR"), errors="coerce"),
                "updated_at": datetime.now(),
            }
        )
    return pd.DataFrame(normalized)


def search_community_posts(keyword: str, limit: int = 20) -> pd.DataFrame:
    """Search public web results. Keep this lightweight and store only title/snippet/url."""
    query = f"{keyword} 기름값 연비 자동차 커뮤니티"
    url = "https://duckduckgo.com/html/"
    response = requests.get(url, params={"q": query}, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    for result in soup.select(".result")[:limit]:
        link = result.select_one(".result__a")
        snippet = result.select_one(".result__snippet")
        if not link:
            continue
        rows.append(
            {
                "source": "DuckDuckGo",
                "title": link.get_text(" ", strip=True),
                "url": link.get("href"),
                "snippet": snippet.get_text(" ", strip=True) if snippet else "",
                "keyword": keyword,
                "crawled_at": datetime.now(),
            }
        )
    return pd.DataFrame(rows)


def opinet_api_key() -> str:
    return os.getenv("OPINET_API_KEY", "").strip()
