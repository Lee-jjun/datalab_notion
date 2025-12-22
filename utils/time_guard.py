from datetime import datetime, timezone, timedelta

def should_crawl(page, last_run_key: str, hours: int = 24) -> bool:
    prop = page["properties"].get(last_run_key)
    if not prop or not prop.get("date"):
        return True

    last = prop["date"].get("start")
    if not last:
        return True

    last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) - last_dt > timedelta(hours=hours)