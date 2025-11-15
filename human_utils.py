import time
import random

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def human_type(
        element,
        text: str,
        min_delay: float = 0.2,
        max_delay: float = 1.0,
        typo_prob: float = 0.0,
):
    for ch in text:
        if typo_prob > 0 and random.random() < typo_prob:
            wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
            element.send_keys(wrong_char)
            time.sleep(random.uniform(min_delay, max_delay))
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(min_delay, max_delay))

        element.send_keys(ch)
        time.sleep(random.uniform(min_delay, max_delay))


def human_move_and_click(driver, element):
    actions = ActionChains(driver)
    time.sleep(random.uniform(0.3, 1.0))
    actions.move_to_element(element).pause(
        random.uniform(0.2, 0.7)
    ).click().perform()


def human_scroll(driver):
    scroll_amount = random.randint(-200, 400)
    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_amount)
    time.sleep(random.uniform(0.2, 0.8))
