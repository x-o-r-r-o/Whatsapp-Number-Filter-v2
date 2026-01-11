# whatsapp_filter/drivers.py
from __future__ import annotations
import platform
import shutil
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService

from .logger import info, warn, error


def print_manual_driver_instructions(browser: str) -> None:
    os_name = platform.system()
    info("Automatic WebDriver installation failed.")
    info(f"Please install the {browser} WebDriver manually.")

    if browser == "chrome":
        info("ChromeDriver download: https://chromedriver.chromium.org/downloads")
    elif browser == "firefox":
        info("GeckoDriver download: https://github.com/mozilla/geckodriver/releases")
    elif browser == "edge":
        info("Edge WebDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")

    if os_name == "Windows":
        info("Place driver in C:\\WebDrivers and add to PATH.")
    else:
        info("Place driver in /usr/local/bin or another PATH folder.")


def create_driver(
    browser: str,
    headless: bool = False,
    driver_path: Optional[str] = None,
    profile_suffix: Optional[str] = None,
) -> webdriver.Remote:
    base_profile_dir = Path.cwd() / "browser_profiles"
    base_profile_dir.mkdir(exist_ok=True)

    if profile_suffix is None:
        profile_suffix = "main"

    try:
        if browser == "chrome":
            options = webdriver.ChromeOptions()
            profile_dir = base_profile_dir / f"chrome_whatsapp_profile_{profile_suffix}"
            profile_dir.mkdir(exist_ok=True)
            options.add_argument(f"user-data-dir={profile_dir.resolve()}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

            service = ChromeService(executable_path=driver_path) if driver_path else ChromeService(
                ChromeDriverManager().install()
            )
            driver = webdriver.Chrome(service=service, options=options)

        elif browser == "firefox":
            options = webdriver.FirefoxOptions()
            profile_dir = base_profile_dir / f"firefox_whatsapp_profile_{profile_suffix}"
            profile_dir.mkdir(exist_ok=True)
            if headless:
                options.headless = True

            service = FirefoxService(executable_path=driver_path) if driver_path else FirefoxService(
                GeckoDriverManager().install()
            )
            driver = webdriver.Firefox(service=service, options=options)

        elif browser == "edge":
            options = webdriver.EdgeOptions()
            profile_dir = base_profile_dir / f"edge_whatsapp_profile_{profile_suffix}"
            profile_dir.mkdir(exist_ok=True)
            options.add_argument(f"user-data-dir={profile_dir.resolve()}")
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

            service = EdgeService(executable_path=driver_path) if driver_path else EdgeService(
                EdgeChromiumDriverManager().install()
            )
            driver = webdriver.Edge(service=service, options=options)

        else:
            raise ValueError(f"Unsupported browser: {browser}")

        return driver

    except (WebDriverException, Exception) as e:
        error(f"Failed to create WebDriver for {browser}: {e}")
        if not driver_path:
            print_manual_driver_instructions(browser)
        else:
            info("Check your --driver-path and executable permissions.")
        raise SystemExit(1)


def prepare_worker_profiles(browser: str, max_workers: int) -> None:
    base_profile_dir = Path.cwd() / "browser_profiles"

    if browser == "chrome":
        base_name = "chrome_whatsapp_profile"
    elif browser == "firefox":
        base_name = "firefox_whatsapp_profile"
    elif browser == "edge":
        base_name = "edge_whatsapp_profile"
    else:
        warn(f"Unsupported browser for profile cloning: {browser}")
        return

    single_profile = base_profile_dir / f"{base_name}_single"

    if not single_profile.exists():
        warn(f"Single-mode profile not found: {single_profile}")
        warn("Run once with mode 'single' to create and log in.")
        return

    info(f"Preparing worker profiles from base: {single_profile}")

    for worker_id in range(1, max_workers + 1):
        worker_profile = base_profile_dir / f"{base_name}_worker_{worker_id}"

        if worker_profile.exists():
            info(f"Worker profile already exists, skipping clone: {worker_profile}")
            continue

        try:
            info(f"Cloning profile to: {worker_profile}")
            shutil.copytree(single_profile, worker_profile)
        except Exception as e:
            warn(f"Failed to clone profile to {worker_profile}: {e}")