import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def to_mobile(url: str) -> str:
    """PC 카페 URL → 모바일 URL"""
    return url.replace("cafe.naver.com", "m.cafe.naver.com")


def get_comment_and_view(url: str) -> tuple[int, int]:
    """
    네이버 카페 게시글
    → (댓글 수, 조회 수) 반환
    실패 시 (0, 0)
    """
    try:
        url = to_mobile(url)
        res = requests.get(url, headers=HEADERS, timeout=5)
        res.raise_for_status()
    except Exception:
        return 0, 0

    soup = BeautifulSoup(res.text, "html.parser")

    # =========================
    # 댓글 수
    # =========================
    comment_selectors = [
        "em.num",
        "span.num",
        ".comment_area .num",
        "a.comment em",
    ]

    comment_count = 0
    for sel in comment_selectors:
        tag = soup.select_one(sel)
        if tag and tag.text.strip().isdigit():
            comment_count = int(tag.text.strip())
            break

    # =========================
    # 조회 수
    # =========================
    view_selectors = [
        "span.count",
        "em.count",
        ".post_info .count",
        ".article_info .count",
    ]

    view_count = 0
    for sel in view_selectors:
        tag = soup.select_one(sel)
        if not tag:
            continue

        text = (
            tag.text
            .replace("조회", "")
            .replace(",", "")
            .strip()
        )

        if text.isdigit():
            view_count = int(text)
            break

    return comment_count, view_count

