import requests
from datetime import datetime
import os

# =====================
# 설정
# =====================
NOTION_TOKEN = os.getenv("NOTION_TOKEN") or "secret_xxx"
DATABASE_ID = os.getenv("NOTION_DB_ID") or "2ca286f326ff8024a64ef0dc1e189d2b"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def fetch_notion_rows():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    res = requests.post(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["results"]

def get_number(prop):
    return prop["number"] if prop and prop["number"] is not None else 0

def get_text(prop):
    if not prop or not prop["title"] and not prop["rich_text"]:
        return ""
    texts = prop.get("title") or prop.get("rich_text")
    return "".join([t["plain_text"] for t in texts])

def main():
    rows = fetch_notion_rows()

    print(f"총 {len(rows)}개 행")

    for row in rows:
        props = row["properties"]

        title = get_text(props["게시글 제목"])
        url = props["게시글 URL"]["url"]
        comment_count = get_number(props["댓글 수"])
        last_checked = props["마지막 수집"]["date"]

        last_comment_count = 0
        if last_checked:
            last_comment_count = comment_count  # 최초 기준

        has_new = comment_count > last_comment_count

        print("=" * 40)
        print("제목:", title)
        print("URL:", url)
        print("댓글 수:", comment_count)
        print("NEW 댓글:", has_new)

if __name__ == "__main__":
    main()
