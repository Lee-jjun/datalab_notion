from datetime import datetime, timezone
import time

from crawler.naver_cafe_pc_selenium import get_comment_and_view_pc
from utils.cafe_guard import is_cafe_post_accessible
from notion.client import update_page
from notion.fetch import (
    get_url,
    get_number,
    get_select,
)

# 🚫 크롤링 불가 도메인
BLOCKED_DOMAINS = [
    "gnun.link",
]


def is_blocked_url(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


def process_page(page, cfg, force=False):
    print("process_page 진입:", page["id"])

    try:
        # 1️⃣ 상태 체크
        status = get_select(page, cfg["status"])
        if status != "대기" and not force:
            return

        # 2️⃣ URL
        url = get_url(page, cfg["url"])
        if not url:
            return

        # 🚫 크롤링 불가 도메인 즉시 처리
        if is_blocked_url(url):
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "불가"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🚫 크롤링 불가 도메인 → 상태 불가:", url)
            return

        # 3️⃣ 네이버 카페 접근 불가
        if not is_cafe_post_accessible(url):
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "불가"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🚫 네이버 카페 아님/접근 불가:", url)
            return

        # 4️⃣ 이전 댓글 수
        prev_comment = get_number(page, cfg["count"]) or 0

        # 5️⃣ 크롤링
        title, comment, view, is_deleted = get_comment_and_view_pc(url)

        # 🗑 삭제글 처리
        if is_deleted:
            update_page(page["id"], {
                cfg["status"]: {"status": {"name": "삭제"}},
                cfg["last_run"]: {
                    "date": {"start": datetime.now(timezone.utc).isoformat()}
                }
            })
            print("🗑 삭제글 처리:", url)
            return

        print(
            f"[DEBUG] prev_comment={prev_comment}, "
            f"current_comment={comment}, "
            f"increased={comment > prev_comment}"
        )

        # 6️⃣ 기본 업데이트
        updates = {
            cfg["count"]: {"number": comment},
            cfg["view"]: {"number": view},
            cfg["last_run"]: {
                "date": {"start": datetime.now(timezone.utc).isoformat()}
            },
            cfg["status"]: {"status": {"name": "확인완료"}},
            "글 제목": {
                "rich_text": [
                    {"text": {"content": title or ""}}
                ]
            },
        }

        # 7️⃣ NEW 댓글 체크 (체크만)
        if comment > prev_comment:
            updates[cfg["new"]] = {"checkbox": True}

        update_page(page["id"], updates)

        # 🔒 보호 딜레이
        time.sleep(0.6)

    except Exception as e:
        print("❌ ERROR PAGE:", page["id"], e)
        return