import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def is_cafe_post_accessible(url: str) -> bool:
    if "cafe.naver.com" not in url:
        return False

    try:
        res = requests.get(
            url,
            headers=HEADERS,
            timeout=5,
            allow_redirects=True
        )

        if res.status_code != 200:
            return False

        text = res.text
        BLOCK_KEYWORDS = [
            "삭제되었거나 존재하지 않는 게시글",
            "존재하지 않는 카페",
            "접근이 제한된 카페",
            "권한이 없습니다",
        ]

        return not any(k in text for k in BLOCK_KEYWORDS)

    except requests.RequestException:
        return False