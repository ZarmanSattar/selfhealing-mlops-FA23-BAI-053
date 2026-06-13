import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
SELENIUM_REMOTE_URL = os.environ.get("SELENIUM_REMOTE_URL")


def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    if SELENIUM_REMOTE_URL:
        driver = webdriver.Remote(command_executor=SELENIUM_REMOTE_URL, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    try:
        driver.get(BASE_URL)

        text_input = driver.find_element(By.ID, "text-input")
        text_input.send_keys("I really love this amazing product")

        submit_btn = driver.find_element(By.ID, "submit-btn")
        submit_btn.click()

        time.sleep(3)

        result = driver.find_element(By.ID, "result-output")
        result_text = result.text

        assert result_text.strip() != ""
        assert any(keyword in result_text for keyword in ["POSITIVE", "NEGATIVE", "Confidence"])
    finally:
        driver.quit()
