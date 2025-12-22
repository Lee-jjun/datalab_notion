import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# 🔑 전역 세션 (소켓 고갈 방지 핵심)
_session = requests.Session()
_session.headers.update(HEADERS)

DEFAULT_TIMEOUT = 10
RATE_LIMIT_SLEEP = 0.25   # 🔥 Notion 안정용


# =========================
# Database
# =========================
def query_database(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    all_results = []
    payload = {}

    while True:
        res = _session.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
        res.raise_for_status()

        data = res.json()
        all_results.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data.get("next_cursor")
        time.sleep(RATE_LIMIT_SLEEP)

    return all_results


def retrieve_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = _session.get(url, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP)
    return res.json()


# =========================
# Page Update
# =========================
def update_page(page_id, properties, retry=2):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"properties": properties}

    for attempt in range(1, retry + 1):
        try:
            res = _session.patch(url, json=payload, timeout=DEFAULT_TIMEOUT)
            res.raise_for_status()
            time.sleep(RATE_LIMIT_SLEEP)
            return
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Notion update retry {attempt}/{retry}:", e)
            time.sleep(1.5 * attempt)

    print("❌ Notion update failed permanently:", page_id)
    return


# =========================
# Block helpers
# =========================
def prepend_text_block(page_id: str, text: str):
    """
    페이지 본문 최상단에 텍스트 블록 추가
    """
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"

    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": text}}
                    ]
                }
            }
        ]
    }

    res = _session.patch(url, json=payload, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP)


def append_block_to_block(block_id: str, text: str):
    """
    특정 블록(callout, heading 등) 아래에 텍스트 블록 추가
    """
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"

    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": text}}
                    ]
                }
            }
        ]
    }

    res = _session.patch(url, json=payload, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP)


def delete_block(block_id: str):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    res = _session.delete(url, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP)


def retrieve_page_blocks(page_id: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    res = _session.get(url, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()
    time.sleep(RATE_LIMIT_SLEEP)
    return res.json().get("results", [])


def find_blocks_with_text(page_id: str, keyword: str):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    res = _session.get(url, timeout=DEFAULT_TIMEOUT)
    res.raise_for_status()

    blocks = res.json().get("results", [])
    matched = []

    for b in blocks:
        if b["type"] == "paragraph":
            texts = b["paragraph"]["rich_text"]
            content = "".join(t["plain_text"] for t in texts)
            if keyword in content:
                matched.append(b["id"])

    time.sleep(RATE_LIMIT_SLEEP)
    return matched

def append_link_block_to_block(block_id: str, *, title: str, url: str, time_text: str):
    endpoint = f"https://api.notion.com/v1/blocks/{block_id}/children"

    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "🔴 NEW 댓글!!\n"}
                        },
                        {
                            "type": "text",
                            "text": {"content": f"• 제목: {title}\n"}
                        },
                        {
                            "type": "text",
                            "text": {"content": f"• 시간: {time_text}\n"}
                        },
                        {
                            "type": "text",
                            "text": {
                                "content": "• 링크 바로가기",
                                "link": {"url": url}
                            }
                        },
                    ]
                }
            }
        ]
    }

    try:
        res = _session.patch(endpoint, json=payload, timeout=DEFAULT_TIMEOUT)
        res.raise_for_status()
        time.sleep(RATE_LIMIT_SLEEP)
    except requests.exceptions.RequestException as e:
        print("⚠️ append_link_block 실패:", e)