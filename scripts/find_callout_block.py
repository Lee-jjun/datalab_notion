import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from notion.client import retrieve_page_blocks

PAGE_ID = "2cb286f326ff80758430e2a7a757ac5e"

blocks = retrieve_page_blocks(PAGE_ID)

for b in blocks:
    if b["type"] == "callout":
        text = "".join(
            t["plain_text"]
            for t in b["callout"]["rich_text"]
        )
        print("CALL_OUT_TEXT:", text)
        print("CALL_OUT_BLOCK_ID:", b["id"])