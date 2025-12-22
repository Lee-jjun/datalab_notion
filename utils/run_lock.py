import os
import sys
import time

LOCK_FILE = "crawler.lock"


def acquire_lock():
    if os.path.exists(LOCK_FILE):
        print("⛔ 이미 실행 중입니다. 종료합니다.")
        sys.exit(0)

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def release_lock():
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except Exception:
            pass