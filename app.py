import random
import time

from fastapi import FastAPI
from pydantic import BaseModel

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from email_utils import get_latest_otp
from human_utils import human_type, human_move_and_click, human_scroll

import os

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

app = FastAPI()


class MessageRequest(BaseModel):
    url: str
    link: str
    message_text: str


class MessageResponse(BaseModel):
    status: str
    detail: str | None = None


def is_suspicious_page(driver) -> bool:
    html = driver.page_source.lower()
    return "suspicious" in html


def run_flow(login_url: str, profile_url: str, message_text: str) -> bool:
    driver = webdriver.Chrome()

    try:
        driver.set_window_size(
            random.randint(1000, 1400),
            random.randint(700, 900),
        )

        driver.get(login_url)
        driver.implicitly_wait(5)

        human_scroll(driver)

        username_input = driver.find_element(
            By.XPATH,
            "//input[@id='username' and @name='session_key']",
        )
        password_input = driver.find_element(
            By.XPATH,
            "//input[@id='password' and @name='session_password']",
        )

        human_move_and_click(driver, username_input)
        human_type(username_input, USER_EMAIL, 0.15, 0.6, typo_prob=0.03)

        time.sleep(random.uniform(0.2, 0.7))
        username_input.send_keys(Keys.TAB)
        time.sleep(random.uniform(0.2, 0.7))

        human_type(password_input, USER_PASSWORD, 0.15, 0.6, typo_prob=0.02)

        button = driver.find_element(
            By.XPATH,
            "//button[@data-litms-control-urn='login-submit']",
        )

        time.sleep(random.uniform(0.7, 1.8))

        if random.random() < 0.5:
            human_move_and_click(driver, button)
        else:
            password_input.send_keys(Keys.ENTER)

        time.sleep(random.uniform(3, 6))

        if is_suspicious_page(driver):
            otp = get_latest_otp(
                subject_filter="Your verification code",
                timeout=120,
                poll_interval=5,
            )
            if otp is None:
                return False

            otp_input = driver.find_element(
                By.XPATH,
                "//input[@name='otp' or @id='verification-code']",
            )
            human_move_and_click(driver, otp_input)
            human_type(otp_input, otp, 0.1, 0.3, typo_prob=0.0)

            confirm_button = driver.find_element(
                By.XPATH,
                "//button[contains(., 'Verify') or contains(., 'Continue')]",
            )
            time.sleep(random.uniform(0.5, 1.5))
            human_move_and_click(driver, confirm_button)
            time.sleep(random.uniform(3, 6))

        driver.get(profile_url)
        time.sleep(random.uniform(1, 3))

        message_button = driver.find_element(
            By.XPATH,
            "(//section//div[contains(@class,'entry-point')]/button"
            "[contains(@aria-label, 'Message') and contains(./span, 'Message')])[2]"
        )
        message_button.click()
        time.sleep(random.uniform(0.7, 1.8))

        message_box = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'msg-form__msg-content-container--scrollable scrollable')]",
        )
        message_box.send_keys(message_text)

        time.sleep(random.uniform(2.7, 3.8))

        return True

    except Exception as exc:
        return False

    finally:
        driver.quit()


@app.post("/send-message", response_model=MessageResponse)
def send_message(payload: MessageRequest) -> MessageResponse:
    ok = run_flow(
        login_url=payload.url,
        profile_url=payload.link,
        message_text=payload.message_text,
    )

    if ok:
        return MessageResponse(status="success", detail=None)
    return MessageResponse(status="failed", detail="Flow execution failed")
