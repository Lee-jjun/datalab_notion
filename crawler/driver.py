from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

_driver = None

def get_driver():
    global _driver

    if _driver is not None:
        try:
            _driver.title
            return _driver
        except:
            _driver = None

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1200,900")

    _driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return _driver


def quit_driver():
    global _driver
    if _driver:
        try:
            _driver.quit()
        except:
            pass
        _driver = None