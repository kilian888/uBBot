import datetime
import time

import yaml
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def time_in_range(start, end, now):
    """Check if x is in the range [start, end]."""
    if start <= end:
        return start <= now <= end
    else:
        return start <= now or now <= end


def make_reservation_on_end(browser, config):
    """This prepares everything and executes only the final click on time = end."""
    timezone = pytz.timezone(config["timezone"])
    browser.get("https://hbzwwws005.uzh.ch/booked-ubzh/Web/?")
    browser.find_element("id", "email").send_keys(config["mail"])
    browser.find_element("id", "password").send_keys(config["password"])

    action_chain = ActionChains(browser)
    login = browser.find_element("css selector", "div > button[type='submit']")
    action_chain.move_to_element(login).move_by_offset(0, 0).click().perform()
    browser.find_element("xpath", "//*[@id='schedules']/option[14]").click()
    next_datetime = datetime.datetime.now(timezone) + datetime.timedelta(days=1)
    browser.get(
        f"https://hbzwwws005.uzh.ch/booked-ubzh/Web/reservation.php?rid=1484&sid=22&rd={next_datetime.day}-{next_datetime.month}-{next_datetime.year}"
    )

    WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='BeginPeriod']/option[1]"))
    ).click()

    WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='EndPeriod']/option[24]"))
    ).click()

    WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='psiattribute5']/option[2]"))
    ).click()

    browser.find_element("id", "termsAndConditionsAcknowledgement").click()

    while True:
        if datetime.time(6, 0, 1) <= datetime.datetime.now(timezone).time():
            WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[@id='form-reservation']/div[5]/div/div/button[2]")
                )
            ).click()
            break
    browser.quit()


def main(config):
    """For continual use this checks every day."""
    chromeoptions = Options()
    chromeoptions.add_argument("--no-sandbox")
    chromeoptions.headless = True
    chromeoptions.Proxy = None
    chromeoptions.add_argument("--remote-debugging-port=9222")
    browser = webdriver.Chrome(
        executable_path="./chromedriver/chromedriver", options=chromeoptions
    )
    timezone = pytz.timezone(config["timezone"])

    while True:
        if time_in_range(
            start=datetime.time(5, 59, 30),
            end=datetime.time(6, 0, 1),
            now=datetime.datetime.now(timezone).time(),
        ):
            make_reservation_on_end(browser, config)
        time.sleep(1)


if __name__ == "__main__":
    with open("config.yml", "r") as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    main(conf)
