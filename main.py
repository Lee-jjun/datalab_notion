from utils.run_lock import acquire_lock, release_lock

from config.notion_mapping import NOTION_DBS
from notion.client import query_database, update_page
from notion.fetch import get_checkbox
from logic.process import process_page

import traceback

try:
    acquire_lock()

    for name, cfg in NOTION_DBS.items():
        print(f"\n===== DB 처리 시작: {name} =====")

        try:
            pages = query_database(cfg["database_id"])
        except Exception as e:
            print("❌ DB 조회 실패:", e)
            continue   # 🔥 다음 DB로 넘어감

        print(f"[DB] {name} 페이지 수:", len(pages))

        force = any(get_checkbox(p, cfg["db_refresh_flag"]) for p in pages)

        for idx, page in enumerate(pages, start=1):
            print(f"[{idx}/{len(pages)}] processing")
            try:
                process_page(page, cfg, force=force)
            except Exception as e:
                print("❌ process_page 에러:", page["id"], e)
                traceback.print_exc()
                continue   # 🔥 절대 멈추지 않음

        # 🔥 여기서 NOTION 실패해도 절대 멈추면 안 됨
        if force:
            print("🔄 refresh flag 해제 중...")
            for p in pages:
                try:
                    update_page(p["id"], {
                        cfg["db_refresh_flag"]: {"checkbox": False}
                    })
                except Exception as e:
                    print("⚠️ refresh flag 해제 실패:", p["id"], e)
                    continue

        print(f"===== DB 처리 종료: {name} =====")

finally:
    release_lock()