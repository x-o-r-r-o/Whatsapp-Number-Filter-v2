# whatsapp_filter/modes.py
from __future__ import annotations
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from .io_utils import append_number
from .whatsapp import open_chat_for_number, wait_for_login, WHATSAPP_WEB_URL
from .drivers import create_driver
from .logger import info, debug

_driver_lock = threading.Lock()


def filter_numbers_single(
    driver: WebDriver,
    numbers: List[str],
    per_number_delay: float,
    valid_path: Path,
    invalid_path: Path,
) -> Tuple[List[str], List[str]]:
    valid: List[str] = []
    invalid: List[str] = []
    total = len(numbers)

    for idx, num in enumerate(numbers, start=1):
        info(f"Checking {idx}/{total}: {num}")
        is_registered, reason = open_chat_for_number(driver, num)
        debug(f"{num} -> {reason}")

        if is_registered:
            valid.append(num)
            append_number(valid_path, num)
        else:
            invalid.append(num)
            append_number(invalid_path, num)

        if per_number_delay > 0:
            time.sleep(per_number_delay)

    return valid, invalid


def _process_number_with_shared_driver(
    driver: WebDriver,
    phone_number: str,
    per_number_delay: float,
    valid_path: Path,
    invalid_path: Path,
) -> Tuple[bool, str]:
    with _driver_lock:
        is_registered, reason = open_chat_for_number(driver, phone_number)

    if is_registered:
        append_number(valid_path, phone_number)
    else:
        append_number(invalid_path, phone_number)

    if per_number_delay > 0:
        time.sleep(per_number_delay)

    return is_registered, reason


def filter_numbers_one_driver_threaded(
    driver: WebDriver,
    numbers: List[str],
    per_number_delay: float,
    valid_path: Path,
    invalid_path: Path,
    max_workers: int = 4,
) -> Tuple[List[str], List[str]]:
    all_valid: List[str] = []
    all_invalid: List[str] = []

    if not numbers:
        return all_valid, all_invalid

    total = len(numbers)
    info(f"One-driver threaded mode | Total numbers: {total} | Threads: {max_workers}")

    def worker_task(idx_num):
        idx, num = idx_num
        debug(f"[THREAD] Scheduled {idx + 1}/{total}: {num}")
        is_reg, reason = _process_number_with_shared_driver(
            driver=driver,
            phone_number=num,
            per_number_delay=per_number_delay,
            valid_path=valid_path,
            invalid_path=invalid_path,
        )
        return idx, num, is_reg, reason

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(worker_task, (idx, num)): (idx, num)
            for idx, num in enumerate(numbers)
        }

        for future in as_completed(futures):
            idx, num, is_reg, reason = future.result()
            debug(f"[THREAD] Done {idx + 1}/{total}: {num} -> {reason}")
            if is_reg:
                all_valid.append(num)
            else:
                all_invalid.append(num)

    return all_valid, all_invalid


def _chunk_list(lst: List[str], n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def _process_numbers_chunk(
    numbers_chunk: List[str],
    browser: str,
    headless: bool,
    driver_path: Optional[str],
    per_number_delay: float,
    valid_path: Path,
    invalid_path: Path,
    worker_id: int,
) -> Tuple[List[str], List[str]]:
    valid: List[str] = []
    invalid: List[str] = []

    profile_suffix = f"worker_{worker_id}"
    driver = create_driver(
        browser=browser,
        headless=headless,
        driver_path=driver_path,
        profile_suffix=profile_suffix,
    )

    driver.get(WHATSAPP_WEB_URL)

    try:
        wait_for_login(driver)
        total = len(numbers_chunk)
        for idx, num in enumerate(numbers_chunk, start=1):
            debug(f"[THREAD {worker_id}] Checking {idx}/{total}: {num}")
            is_registered, reason = open_chat_for_number(driver, num)
            debug(f"[THREAD {worker_id}] {num} -> {reason}")

            if is_registered:
                valid.append(num)
                append_number(valid_path, num)
            else:
                invalid.append(num)
                append_number(invalid_path, num)

            if per_number_delay > 0:
                time.sleep(per_number_delay)
    finally:
        driver.quit()

    return valid, invalid


def filter_numbers_threaded(
    numbers: List[str],
    per_number_delay: float,
    valid_path: Path,
    invalid_path: Path,
    browser: str,
    headless: bool,
    driver_path: Optional[str],
    max_workers: int = 2,
    chunk_size: int = 50,
) -> Tuple[List[str], List[str]]:
    all_valid: List[str] = []
    all_invalid: List[str] = []

    if not numbers:
        return all_valid, all_invalid

    chunks = list(_chunk_list(numbers, chunk_size))
    info(
        f"Total numbers: {len(numbers)} | "
        f"Chunks: {len(chunks)} | Threads: {max_workers} | Chunk size: {chunk_size}"
    )

    workers = min(max_workers, len(chunks))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for worker_id, chunk in enumerate(chunks, start=1):
            futures.append(
                executor.submit(
                    _process_numbers_chunk,
                    chunk,
                    browser,
                    headless,
                    driver_path,
                    per_number_delay,
                    valid_path,
                    invalid_path,
                    worker_id,
                )
            )

        for future in as_completed(futures):
            v, inv = future.result()
            all_valid.extend(v)
            all_invalid.extend(inv)

    return all_valid, all_invalid