import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

CRAWL_URL = "https://stcis.go.kr/wps/dashBoard.do"
WAIT_TIMEOUT = 30

def init_driver(headless: bool = True) -> webdriver.Chrome:
    """Chrome 브라우저 드라이버 초기화"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

def wait_until_rendered(driver: webdriver.Chrome, timeout: int = WAIT_TIMEOUT) -> None:
    wait = WebDriverWait(driver, timeout)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    wait.until(lambda d: len(d.find_element(By.TAG_NAME, "body").text.strip()) > 100)
    time.sleep(0.5)

def fetch_rendered_html(url: str = CRAWL_URL, headless: bool = True) -> str:
    driver = init_driver(headless=headless)
    try:
        driver.get(url)
        wait_until_rendered(driver)
        html = driver.page_source
        return html
    finally:
        driver.quit()

def _to_int(text: str) -> int:
    return int(text.replace(",", ""))

def _parse_rate(text: str) -> float | None:
    match = text.split(" ")[1]
    if not match:
        return None
    return float(match)

def extract_total_use(soup: BeautifulSoup) -> dict | None:
    container = soup.find("div", id="container")
    total_use = container.find("div", class_="totalUse") if container else None
    if not total_use:
        return None

    date_el = total_use.select_one("h2")
    pass_el = total_use.find("span", id="nowUsePassCountSum")
    mem_el = total_use.find("span", id="nowUseMemCountSum")

    comparisons = {
        "전일대비": ("nowMinusBeforeDayRate", "nowMinusBeforeDay"),
        "전월평균대비": ("nowMinusBeforeMonthRate", "nowMinusBeforeMonth"),
        "전년평균대비": ("nowMinusBeforeYearRate", "nowMinusBeforeYear"),
    }
    compare_data = {}
    for label, (rate_id, value_id) in comparisons.items():
        rate_el = total_use.find("span", id=rate_id)
        value_el = total_use.find("span", id=value_id)
        rate_text = rate_el.find_parent("dd").get_text(" ", strip=True) if rate_el else ""
        compare_data[label] = {
            "rate": _parse_rate(rate_text),
            "value": _to_int(value_el.get_text(strip=True)) if value_el else None,
        }

    return {
        "date": date_el.get_text(strip=True) if date_el else None,
        "pass_count": _to_int(pass_el.get_text(strip=True)) if pass_el else None,
        "member_count": _to_int(mem_el.get_text(strip=True)) if mem_el else None,
        "compare": compare_data,
    }

def main():
    html = fetch_rendered_html(headless=True)
    soup = BeautifulSoup(html, "html.parser")
    total_use_data = extract_total_use(soup)
    if total_use_data:
        with open("data/processed/total_use_text.json", "w", encoding="utf-8") as f:
            json.dump(total_use_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
