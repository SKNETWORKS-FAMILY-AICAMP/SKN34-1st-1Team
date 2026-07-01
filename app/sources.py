import os
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()

OPINET_BASE_URL = "https://www.opinet.co.kr/api"
OPINET_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/xml,text/xml,application/json,*/*",
}


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

    response = requests.get(f"{OPINET_BASE_URL}/lowTop10.do", params=params, headers=OPINET_HEADERS, timeout=15)

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


def fetch_opinet_avg_all_price(api_key: str) -> pd.DataFrame:
    """Fetch current national average oil prices from Opinet."""
    params = {
        "code": api_key,
        "out": "xml",
    }
    response = requests.get(f"{OPINET_BASE_URL}/avgAllPrice.do", params=params, headers=OPINET_HEADERS, timeout=15)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    rows = []
    for oil in root.findall(".//OIL"):
        rows.append(
            {
                "trade_date": pd.to_datetime(oil.findtext("TRADE_DT"), format="%Y%m%d", errors="coerce"),
                "product_code": oil.findtext("PRODCD"),
                "product_name": oil.findtext("PRODNM"),
                "avg_price": pd.to_numeric(oil.findtext("PRICE"), errors="coerce"),
                "diff": pd.to_numeric(oil.findtext("DIFF"), errors="coerce"),
            }
        )
    return pd.DataFrame(rows)

def clean_title(title: str) -> str:
    title = re.sub(r"\d{4}\.\d{1,2}\.\d{1,2}\.?", "", title)
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"\[[^\]]*\]", "", title)
    title = " ".join(title.split())
    return title


def calculate_relevance(title: str) -> int:
    score = 0

    weights = {
        "연비": 5,
        "유지비": 5,
        "기름값": 5,
        "주유비": 5,
        "전비": 4,
        "충전비": 4,
        "후기": 3,
        "주행": 2,
        "운행": 2,
        "절약": 2,
        "하이브리드": 2,
        "전기차": 2,
    }

    for word, weight in weights.items():
        if word in title:
            score += weight

    return score

def search_community_posts(keyword: str, limit: int = 20) -> pd.DataFrame:
    search_suffixes = [
        "연비",
        "유지비",
        "기름값 절약",
        "주유비 절약",
    ]

    target_sites = {
        "보배드림": "bobaedream.co.kr",
        "클리앙": "clien.net",
        "뽐뿌": "ppomppu.co.kr",
    }

    exclude_words = [
        "이미지", "지식iN", "동영상", "쇼핑", "뉴스", "어학사전",
        "지도", "인플루언서", "관련도순", "최신순", "전체",
        "1시간", "1일", "1주", "1개월", "3개월", "6개월", "1년",
        "옵션 초기화", "블로그", "카페"
    ]

    url = "https://search.naver.com/search.naver"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    rows = []

    for site_name, domain in target_sites.items():
        for suffix in search_suffixes:
            query = f"{keyword} {suffix} site:{domain}"

            response = requests.get(
                url,
                params={"where": "web", "query": query},
                headers=headers,
                timeout=15,
            )

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.select("a")

            for link in links:
                title = link.get_text(" ", strip=True)
                href = link.get("href")

                if not title or not href:
                    continue

                title = clean_title(title)

                if any(word in title for word in exclude_words):
                    continue

                if keyword not in title and "연비" not in title and "유지비" not in title and "기름값" not in title:
                    continue

                if domain not in href:
                    continue

                rows.append(
                    {
                        "source": site_name,
                        "title": title,
                        "url": href,
                        "snippet": "",
                        "keyword": keyword,
                        "published_at": None,
                        "crawled_at": datetime.now(),
                    }
                )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["relevance_score"] = df["title"].apply(calculate_relevance)

    df = df.drop_duplicates(subset=["url"])
    df = df.drop_duplicates(subset=["title"])
    df = df.sort_values("relevance_score", ascending=False)
    df = df.head(limit)

    return df.drop(columns=["relevance_score"])

def opinet_api_key() -> str:
    return os.getenv("OPINET_API_KEY", "").strip()
