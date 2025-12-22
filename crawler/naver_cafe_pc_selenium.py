from __future__ import annotations

import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)

from crawler.driver import get_driver, quit_driver


def _try_accept_alert(driver) -> str:
    """
    alert가 있으면 accept하고 텍스트 반환, 없으면 ""
    """
    try:
        alert = driver.switch_to.alert
        text = (alert.text or "").strip()
        alert.accept()
        return text
    except NoAlertPresentException:
        return ""
    except Exception:
        # alert 읽기 실패도 driver 상태가 꼬일 수 있으니 비워서 반환
        return ""


def _is_deleted_alert(text: str) -> bool:
    t = text.replace("\n", " ").strip()
    return ("삭제" in t) or ("존재하지" in t) or ("삭제되었" in t)


def get_comment_and_view_pc(url: str):
    """
    return: (title:str, comment:int, view:int, is_deleted:bool)

    ✅ 원칙:
    - alert(삭제/존재하지 않음) 뜨면 즉시 driver 폐기(quit_driver) 후 반환
    - 어떤 예외든 오래 붙잡지 말고 빠르게 반환
    """
    driver = get_driver()
    print("▶ 접속 URL(PC):", url)

    try:
        driver.set_page_load_timeout(20)

        # 항상 최상위
        driver.switch_to.default_content()
        driver.get(url)

        # ✅ get 직후 alert 선제 처리 (중요)
        alert_text = _try_accept_alert(driver)
        if alert_text:
            if _is_deleted_alert(alert_text):
                print("🗑 삭제/존재하지 않음 감지(alert):", alert_text)
                quit_driver()  # 🔥 핵심: 꼬인 driver 즉시 폐기
                return "", 0, 0, True

            print("⚠️ 알 수 없는 alert:", alert_text)
            quit_driver()
            return "", 0, 0, False

        wait = WebDriverWait(driver, 15)

        # iframe 진입
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "cafe_main")))

        # JS 렌더링 최소 대기
        time.sleep(0.7)

        html = driver.page_source

        # ✅ 제목
        title = ""
        title_selectors = [
            "h3.title_text",
            "strong.title_text",
            "div.title_text",
            "h3.tit",
        ]
        for sel in title_selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                title = el.text.strip()
                if title:
                    break
            except Exception:
                continue

        # ✅ 조회수
        view = 0
        m_view = re.search(r"조회\s*([0-9,]+)", html)
        if m_view:
            view = int(m_view.group(1).replace(",", ""))

        # ✅ 댓글수
        comment = 0
        m_comment = re.search(r"댓글\s*([0-9,]+)", html)
        if m_comment:
            comment = int(m_comment.group(1).replace(",", ""))
        else:
            selectors = [
                "a.comment em",
                "a.CommentLink em",
                "strong.num",
                "span.num",
            ]
            for sel in selectors:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, sel)
                    txt = el.text.replace(",", "").strip()
                    if txt.isdigit():
                        comment = int(txt)
                        break
                except Exception:
                    continue

        print(f"✅ 결과 → 제목: {title} | 댓글: {comment} | 조회: {view}")
        return title, comment, view, False

    except UnexpectedAlertPresentException:
        # ✅ iframe 진입 중 alert가 튀어나오는 케이스
        try:
            text = _try_accept_alert(driver)
        except Exception:
            text = ""

        if _is_deleted_alert(text):
            print("🗑 삭제/존재하지 않음 감지(UnexpectedAlert):", text)
            quit_driver()  # 🔥 핵심
            return "", 0, 0, True

        print("⚠️ 알 수 없는 alert(UnexpectedAlert):", text)
        quit_driver()
        return "", 0, 0, False

    except TimeoutException as e:
        print("⚠️ 페이지/iframe 타임아웃 → 스킵:", e)
        # 타임아웃도 driver가 꼬일 수 있어서 폐기 권장
        quit_driver()
        return "", 0, 0, False

    except WebDriverException as e:
        print("⚠️ Selenium 오류 → 스킵:", e)
        quit_driver()
        return "", 0, 0, False

    except Exception as e:
        print("❌ PC 크롤링 실패:", e)
        quit_driver()
        return "", 0, 0, False

    finally:
        # 정상 케이스는 driver 재사용을 위해 유지
        try:
            if driver:
                driver.switch_to.default_content()
        except Exception:
            pass