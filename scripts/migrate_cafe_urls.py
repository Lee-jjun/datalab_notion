import os
import sys
import re
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from notion.client import query_database, update_page
from notion.fetch import get_url
from config.notion_mapping import NOTION_DBS


def extract_clubid_mobile_url(driver, raw_url: str):
    """
    https://cafe.naver.com/<alias>/<articleid>
    -> https://m.cafe.naver.com/ca-fe/web/cafes/<clubid>/articles/<articleid>

    ⚠️ articleid가 원본과 100% 일치할 때만 성공
    """

    # 원래 articleid
    m = re.search(r"/(\d+)(?:\?|$)", raw_url)
    if not m:
        return None
    expected_articleid = m.group(1)

    # alias
    m2 = re.search(r"cafe\.naver\.com/([^/]+)/\d+", raw_url)
    alias = m2.group(1) if m2 else None

    candidates = [
        raw_url,
    ]

    if alias:
        candidates += [
            f"https://m.cafe.naver.com/{alias}/{expected_articleid}",
            f"https://m.cafe.naver.com/ca-fe/web/cafes/{alias}/articles/{expected_articleid}",
        ]

    for u in candidates:
        try:
            print("  ▶ try:", u)
            driver.get(u)
            time.sleep(2)

            cur = driver.current_url
            m3 = re.search(r"cafes/(\d+)/articles/(\d+)", cur)
            if not m3:
                continue

            clubid, articleid = m3.groups()

            # 🔒 안전장치
            if articleid != expected_articleid:
                print(
                    f"  ⚠️ articleid mismatch "
                    f"(expected {expected_articleid}, got {articleid})"
                )
                continue

            final_url = (
                f"https://m.cafe.naver.com/ca-fe/web/cafes/"
                f"{clubid}/articles/{articleid}"
            )
            print("  ✅ resolved:", final_url)
            return final_url

        except Exception as e:
            print("  ❌ try failed:", e)
            continue

    return None


def main():
    options = Options()
    options.add_argument("--window-size=1200,900")
    # 처음엔 눈으로 확인 권장
    # options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        for name, cfg in NOTION_DBS.items():
            print(f"\n🔄 DB 변환 시작: {name}")
            pages = query_database(cfg["database_id"])

            for page in pages:
                raw_url = get_url(page, cfg["url"])
                if not raw_url:
                    continue

                # 이미 모바일 URL이면 스킵
                if "m.cafe.naver.com/ca-fe/web/cafes" in raw_url:
                    continue

                # 카페 URL만 대상
                if "cafe.naver.com" not in raw_url:
                    continue

                print("▶ 변환 시도:", raw_url)

                new_url = extract_clubid_mobile_url(driver, raw_url)
                if not new_url:
                    print("❌ 변환 실패 (DB 유지)")
                    continue

                update_page(page["id"], {
                    cfg["url"]: {"url": new_url}
                })
                print("✅ 변환 완료 →", new_url)
                time.sleep(0.5)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()