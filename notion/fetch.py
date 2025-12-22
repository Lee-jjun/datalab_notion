def get_url(page, prop):
    try:
        return page["properties"][prop]["url"]
    except Exception:
        return None

def get_number(page, prop):
    try:
        return page["properties"][prop]["number"]
    except Exception:
        return None

def get_select(page, prop):
    try:
        return page["properties"][prop]["status"]["name"]
    except Exception:
        return None

def get_checkbox(page, prop):
    try:
        return page["properties"][prop]["checkbox"]
    except Exception:
        return False

def get_relation_page_ids(page, prop_name: str):
    """
    Relation 속성에 연결된 페이지 ID 리스트 반환
    """
    try:
        rel = page["properties"][prop_name]["relation"]
        return [r["id"] for r in rel]
    except Exception:
        return []

def get_page_title(page, title_prop="Name"):
    try:
        items = page["properties"][title_prop]["title"]
        return "".join(t["text"]["content"] for t in items)
    except Exception:
        return ""
    
def is_status_property(page, prop_name: str) -> bool:
    """
    해당 속성이 Status 타입인지 확인
    """
    try:
        return "status" in page["properties"][prop_name]
    except Exception:
        return False
    
def is_number_property(page, prop_name: str) -> bool:
    """
    해당 속성이 Number 타입인지 확인
    """
    try:
        return page["properties"][prop_name]["type"] == "number"
    except Exception:
        return False
    
def get_rich_text(page, prop):
    texts = page["properties"][prop]["rich_text"]
    return "".join(t["plain_text"] for t in texts)
