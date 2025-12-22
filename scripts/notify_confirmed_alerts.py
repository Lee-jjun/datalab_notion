from config.notion_mapping import NOTION_DBS
from notion.client import (
    query_database,
    update_page,
    retrieve_page_blocks,
    delete_block,
)
from notion.fetch import get_checkbox, get_relation_page_ids
import time

RATE_LIMIT = 0.3


def main():
    cfg = NOTION_DBS["병원 DB 이름"]  # 병원 DB

    hospitals = query_database(cfg["database_id"])
    targets = [h for h in hospitals if get_checkbox(h, "알림 확인")]

    print(f"🧹 알림 정리 대상 병원: {len(targets)}")

    for hospital in targets:
        hospital_id = hospital["id"]

        # 1️⃣ Callout 아래 알림 삭제
        blocks = retrieve_page_blocks(hospital_id)
        for b in blocks:
            if b.get("type") == "callout":
                callout_id = b["id"]
                children = retrieve_page_blocks(callout_id)
                for c in children:
                    delete_block(c["id"])
                    time.sleep(RATE_LIMIT)

        # 2️⃣ 연결된 여론 페이지 NEW 해제
        rumor_cfg = NOTION_DBS["윈느성형외과 여론"]
        rumor_ids = get_relation_page_ids(hospital, rumor_cfg["hospital_relation"])

        for pid in rumor_ids:
            update_page(pid, {
                rumor_cfg["new"]: {"checkbox": False}
            })
            time.sleep(RATE_LIMIT)

        # 3️⃣ 병원 확인 체크 해제
        update_page(hospital_id, {
            "알림 확인": {"checkbox": False}
        })

        print("✅ 알림 정리 완료:", hospital_id)


if __name__ == "__main__":
    main()
