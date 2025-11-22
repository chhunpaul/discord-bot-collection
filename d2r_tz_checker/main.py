import os
import smtplib
import requests
from email.mime.text import MIMEText

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = os.environ.get("TZ_URL", "https://www.d2tz.info/online")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.environ.get("DISCORD_USER_ID")


def get_terror_zone_info():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)

        wait = WebDriverWait(driver, 20)

        # Find the table inside .mb-3.tz-table-container
        table = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".mb-3.tz-table-container table")
            )
        )

        # tbody -> first tr
        tbody = table.find_element(By.TAG_NAME, "tbody")
        first_tr = tbody.find_element(By.CSS_SELECTOR, "tr")
        cells = [td.text.strip().strip('Coming soon') for td in first_tr.find_elements(By.TAG_NAME, "td")]

        return cells
    finally:
        driver.quit()


def send_discord_message(content: str):
    if not DISCORD_WEBHOOK_URL:
        raise RuntimeError("DISCORD_WEBHOOK_URL not set")

    data = {"content": content}
    resp = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=10)
    resp.raise_for_status()


if __name__ == "__main__":
    cells = get_terror_zone_info()
    if not cells:
        body = f"<@{DISCORD_USER_ID}> Could not find first row in the TZ table."
    else:
        # Bold the last item
        *prefix, last = cells
        last_bold = f"**{last}**"

        # Join everything back together
        joined = " ".join(prefix + [last_bold])

        # Tag the user at the beginning
        body = f"<@{DISCORD_USER_ID}> {joined}"
    send_discord_message(body)
