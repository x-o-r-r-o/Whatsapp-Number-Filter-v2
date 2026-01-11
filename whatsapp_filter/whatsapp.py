# whatsapp_filter/whatsapp.py
from __future__ import annotations
import time
from typing import Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from .logger import info, debug, warn, error

WHATSAPP_WEB_URL = "https://web.whatsapp.com"


def wait_for_login(driver: WebDriver, timeout: int = 180) -> None:
    info("Waiting for WhatsApp Web login (scan the QR code if needed)...")
    end_time = time.time() + timeout
    last_state = None

    while time.time() < end_time:
        try:
            qr_elements = driver.find_elements(By.CSS_SELECTOR, "canvas[aria-label='Scan me!']")
            qr_containers = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='qrcode']")
            app_root = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='app']")
            chat_list = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Chats'], div[aria-label='Chat list']")
            conversation_header = driver.find_elements(By.CSS_SELECTOR, "header[data-testid='conversation-header']")

            if qr_elements or qr_containers:
                if last_state != "qr":
                    debug("QR code detected, waiting for scan...")
                    last_state = "qr"

            if app_root or chat_list or conversation_header:
                info("Logged into WhatsApp Web (main UI detected).")
                return
        except Exception:
            pass

        time.sleep(1)

    error("Timed out waiting for WhatsApp Web login.")
    try:
        driver.save_screenshot("whatsapp_login_timeout.png")
        info("Saved screenshot: whatsapp_login_timeout.png")
    except Exception as e:
        warn(f"Could not save screenshot: {e}")
    raise TimeoutException("WhatsApp Web login not detected in time")


def open_chat_for_number(
    driver: WebDriver,
    phone_number: str,
    timeout: int = 15
) -> Tuple[bool, str]:
    """
    Return (is_registered, reason).

    Logic:
    - Load /send?phone=...
    - If we see the classic 'phone number shared via url is invalid' popup -> invalid.
    - Else, if we see the main chat header within timeout -> valid.
    - Else, if we see retry/error banners, we treat as invalid (conservative).
    - Else, default to valid if no invalid-modal appears (original behavior),
      but log that we didn't see strong evidence.
    """
    sanitized = phone_number.strip().replace("+", "").replace(" ", "")
    url = f"{WHATSAPP_WEB_URL}/send?phone={sanitized}&text=&type=phone_number&app_absent=0"
    debug(f"Opening URL for {phone_number}: {url}")
    driver.get(url)
    time.sleep(3)

    # Original invalid-number modal
    invalid_modal_xpath = (
        "//div[@data-animate-modal-popup='true' and "
        "contains(@aria-label, 'Phone number shared via url is invalid')]"
        " | "
        "//div[@data-animate-modal-body='true']"
        "[.//div[contains(normalize-space(.), 'Phone number shared via url is invalid.')]]"
    )

    # Additional: retry / error banner
    retry_banner_xpath = (
        "//span[contains(., 'Click to retry') or "
        "contains(., 'Retry') or "
        "contains(., 'Trying to reach phone')]"
    )

    # Conversation header selector (for a real chat open)
    conversation_header_xpath = "//header[@data-testid='conversation-header']"

    end_time = time.time() + timeout
    saw_retry_banner = False

    while time.time() < end_time:
        try:
            invalid_modal = driver.find_elements(By.XPATH, invalid_modal_xpath)
            if invalid_modal:
                debug(f"Invalid-number modal detected for: {phone_number}")
                return False, "Invalid popup detected: phone number shared via url is invalid."

            retry_banner = driver.find_elements(By.XPATH, retry_banner_xpath)
            if retry_banner and not saw_retry_banner:
                saw_retry_banner = True
                warn(f"Retry/error banner seen for {phone_number}; may be transient.")

            conv_header = driver.find_elements(By.XPATH, conversation_header_xpath)
            if conv_header:
                debug(f"Conversation header detected for {phone_number}, treating as valid.")
                return True, "Conversation header detected: treating as valid."

        except Exception as e:
            warn(f"Error while checking popups for {phone_number}: {e!r}")
            time.sleep(1)
            continue

        time.sleep(0.5)

    if saw_retry_banner:
        debug(f"No invalid popup but retry banner seen for {phone_number}, treating as invalid.")
        return False, "Timeout with retry banner present: treating as invalid."

    debug(f"No invalid popup detected within timeout for {phone_number}, treating as valid.")
    return True, "No invalid popup detected within timeout: treating as valid."