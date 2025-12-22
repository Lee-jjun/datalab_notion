import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_comment_and_view_gnun(url: str):
    print("▶ 접속 URL(GNUN):", url)

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.text if soup.title else "NO TITLE"
        print("📰 GNUN TITLE:", title)

        # ❗ gnun은 댓글 DOM 없음 → 0이 정상
        comment = 0
        view = 0

        print(f"✅ 결과 → 댓글: {comment} | 조회: {view}")
        return comment, view

    except Exception as e:
        print("❌ GNUN 접근 실패:", e)
        return 0, 0