# whatsapp_filter/cli.py
from __future__ import annotations
import argparse
import time
from pathlib import Path
from textwrap import dedent
from typing import Dict, Any, Optional

from .config import AppConfig, load_config_file, merge_config
from .io_utils import read_numbers_from_file, write_numbers, append_log
from .drivers import create_driver, prepare_worker_profiles
from .whatsapp import wait_for_login, WHATSAPP_WEB_URL
from .modes import (
    filter_numbers_single,
    filter_numbers_one_driver_threaded,
    filter_numbers_threaded,
)
from .logger import info, debug, warn, error


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Filter WhatsApp-registered numbers using WhatsApp Web automation."
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (YAML or JSON). Default: config.yaml in current directory.",
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Override config 'input' file path.",
    )
    parser.add_argument(
        "--valid-output",
        type=str,
        help="Override config 'valid_output'.",
    )
    parser.add_argument(
        "--invalid-output",
        type=str,
        help="Override config 'invalid_output'.",
    )
    parser.add_argument(
        "--browser",
        type=str,
        choices=["chrome", "firefox", "edge"],
        help="Override config 'browser'.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Override to headless=True.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        help="Override config 'delay'.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single", "threaded", "onedriver"],
        help="Override config 'mode'.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        help="Override config 'threads'.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Override config 'chunk_size'.",
    )
    parser.add_argument(
        "--driver-path",
        type=str,
        help="Override config 'driver_path'.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Override config 'log_file'.",
    )
    parser.add_argument(
        "--show-examples",
        action="store_true",
        help="Show CLI examples and exit.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run interactive setup: create/update config and sample files, then exit "
             "(unless --auto-run-after-setup is also provided).",
    )
    parser.add_argument(
        "--config-menu",
        action="store_true",
        help="Open interactive config menu (edit/update config.yaml), then exit.",
    )
    parser.add_argument(
        "--auto-run-after-setup",
        action="store_true",
        help="After a successful setup, automatically run the app once with the new config.",
    )
    return parser


def collect_cli_overrides(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "input": args.input,
        "valid_output": args.valid_output,
        "invalid_output": args.invalid_output,
        "browser": args.browser,
        "headless": args.headless if args.headless else None,
        "delay": args.delay,
        "mode": args.mode,
        "threads": args.threads,
        "chunk_size": args.chunk_size,
        "driver_path": args.driver_path,
        "log_file": args.log_file,
    }


def print_cli_examples(script_name: str = "whatsapp-filter") -> None:
    print("\n=== CLI Usage Examples ===\n")
    print("# 1) First-time interactive setup and auto-run")
    print(f"{script_name} --setup --auto-run-after-setup\n")
    print("# 2) Just interactive setup (no auto-run)")
    print(f"{script_name} --setup\n")
    print("# 3) Run using config.yaml from current folder")
    print(f"{script_name}\n")
    print("# 4) Open config menu again later")
    print(f"{script_name} --config-menu\n")
    print("# 5) Override input and mode from CLI")
    print(f"{script_name} -i data/input_numbers.txt --mode threaded --threads 4\n")
    print("# 6) One-driver threaded mode")
    print(f"{script_name} --mode onedriver --threads 4\n")
    print("# 7) Multi-driver threaded (requires single-mode login first)")
    print("# 7.1) Run single to create logged-in profile")
    print(f"{script_name} --mode single")
    print("# 7.2) Then run threaded")
    print(f"{script_name} --mode threaded --threads 4 --chunk-size 50")
    print("==========================\n")


# ---------- Interactive config menu helpers ----------

def _prompt_choice(prompt: str, choices: Dict[str, str], default: Optional[str] = None) -> str:
    while True:
        print(prompt)
        for key, label in choices.items():
            print(f"  {key}) {label}")
        if default is not None:
            print(f"Press ENTER for default [{default}]")
        resp = input("> ").strip()
        if not resp and default is not None:
            return default
        if resp in choices:
            return choices[resp]
        print("Invalid selection, try again.\n")


def _prompt_str(prompt: str, default: Optional[str] = None) -> str:
    if default:
        resp = input(f"{prompt} [{default}]: ").strip()
        return resp or default
    return input(f"{prompt}: ").strip()


def _prompt_float(prompt: str, default: float) -> float:
    while True:
        resp = input(f"{prompt} [{default}]: ").strip()
        if not resp:
            return default
        try:
            return float(resp)
        except ValueError:
            print("Please enter a valid number.")


def _prompt_int(prompt: str, default: int) -> int:
    while True:
        resp = input(f"{prompt} [{default}]: ").strip()
        if not resp:
            return default
        try:
            return int(resp)
        except ValueError:
            print("Please enter a valid integer.")


def _prompt_bool(prompt: str, default: bool) -> bool:
    default_str = "y" if default else "n"
    while True:
        resp = input(f"{prompt} (y/n) [{default_str}]: ").strip().lower()
        if not resp:
            return default
        if resp in ("y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


def _detect_browsers() -> Dict[str, str]:
    return {
        "1": "chrome",
        "2": "firefox",
        "3": "edge",
    }


def interactive_config_menu(existing: Optional[AppConfig]) -> AppConfig:
    print("\n=== WhatsApp Filter Configuration Menu ===\n")

    browser_choices = _detect_browsers()
    if existing is None:
        print("No existing config found. Creating a new one.\n")
        default_input = "data/input_numbers.txt"
        default_valid = "data/valid_numbers.txt"
        default_invalid = "data/invalid_numbers.txt"
        default_browser = "chrome"
        default_headless = False
        default_delay = 2.0
        default_mode = "single"
        default_threads = 4
        default_chunk = 50
        default_driver_path = None
        default_log_file = "run_log.txt"
    else:
        print("Existing configuration detected. Press ENTER to keep current values.\n")
        default_input = existing.input
        default_valid = existing.valid_output
        default_invalid = existing.invalid_output
        default_browser = existing.browser
        default_headless = existing.headless
        default_delay = existing.delay
        default_mode = existing.mode
        default_threads = existing.threads
        default_chunk = existing.chunk_size
        default_driver_path = existing.driver_path
        default_log_file = existing.log_file

    input_path = _prompt_str("Input file path (phone numbers, one per line)", default_input)
    valid_output = _prompt_str("Valid output file path", default_valid)
    invalid_output = _prompt_str("Invalid output file path", default_invalid)

    print("\nSelect browser:")
    browser = _prompt_choice("Choose browser:", browser_choices, default=default_browser)

    headless = _prompt_bool("Run browser in headless mode?", default_headless)
    delay = _prompt_float("Delay in seconds between checks", default_delay)

    mode_choices = {"1": "single", "2": "onedriver", "3": "threaded"}
    print("\nSelect mode:")
    mode = _prompt_choice(
        "Choose mode: 1=single, 2=onedriver, 3=threaded",
        mode_choices,
        default=default_mode,
    )

    threads = _prompt_int("Number of threads for threaded modes", default_threads)
    chunk_size = _prompt_int("Chunk size for multi-driver threaded mode", default_chunk)

    driver_path = _prompt_str(
        "Optional WebDriver path (leave empty for auto-download)",
        default_driver_path or "",
    )
    driver_path = driver_path or None

    log_file = _prompt_str("Log file path", default_log_file)

    print("\nConfiguration summary:")
    print(f"  input         = {input_path}")
    print(f"  valid_output  = {valid_output}")
    print(f"  invalid_output= {invalid_output}")
    print(f"  browser       = {browser}")
    print(f"  headless      = {headless}")
    print(f"  delay         = {delay}")
    print(f"  mode          = {mode}")
    print(f"  threads       = {threads}")
    print(f"  chunk_size    = {chunk_size}")
    print(f"  driver_path   = {driver_path}")
    print(f"  log_file      = {log_file}")

    if not _prompt_bool("\nSave this configuration?", True):
        info("Configuration not saved (user cancelled).")
        return existing if existing is not None else AppConfig(input=input_path)

    cfg = AppConfig(
        input=input_path,
        valid_output=valid_output,
        invalid_output=invalid_output,
        browser=browser,
        headless=headless,
        delay=delay,
        mode=mode,
        threads=threads,
        chunk_size=chunk_size,
        driver_path=driver_path,
        log_file=log_file,
    )
    info("Configuration created/updated.")
    return cfg


# ---------- Setup & run ----------

def write_config_file(config_path: Path, cfg: AppConfig) -> None:
    config_text = dedent(
        f"""\
        # Configuration for whatsapp-filter

        input: "{cfg.input}"
        valid_output: "{cfg.valid_output}"
        invalid_output: "{cfg.invalid_output}"

        browser: "{cfg.browser}"
        headless: {str(cfg.headless).lower()}
        delay: {cfg.delay}

        mode: "{cfg.mode}"
        threads: {cfg.threads}
        chunk_size: {cfg.chunk_size}

        driver_path: {"null" if not cfg.driver_path else f'"{cfg.driver_path}"'}
        log_file: "{cfg.log_file}"
        """
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as f:
        f.write(config_text)
    info(f"Saved config to: {config_path}")


def ensure_data_files(cfg: AppConfig) -> None:
    cwd = Path.cwd()
    input_path = (cwd / cfg.input).resolve()
    valid_path = (cwd / cfg.valid_output).resolve()
    invalid_path = (cwd / cfg.invalid_output).resolve()

    input_path.parent.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        sample_content = dedent(
            """\
            # Sample phone numbers (remove '#' to use)
            # 923001234567
            # 923001234568
            """
        )
        with input_path.open("w", encoding="utf-8") as f:
            f.write(sample_content)
        info(f"Created sample input file: {input_path}")
    else:
        info(f"Input file exists: {input_path}")

    for p in (valid_path, invalid_path):
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()
            info(f"Created output file: {p}")
        else:
            info(f"Output file exists: {p}")


def verify_environment(cfg: AppConfig) -> bool:
    info("Verifying environment (WebDriver smoke test)...")
    try:
        driver = create_driver(
            browser=cfg.browser,
            headless=True,
            driver_path=cfg.driver_path,
            profile_suffix="env_check",
        )
        driver.quit()
        info("WebDriver check OK.")
        return True
    except SystemExit:
        return False
    except Exception as e:
        error(f"WebDriver environment check failed: {e}")
        return False


def run_setup(config_path: Path) -> Optional[AppConfig]:
    cwd = Path.cwd()
    info(f"Running setup in: {cwd}")
    existing_cfg: Optional[AppConfig] = None

    if config_path.exists():
        info(f"Existing config found: {config_path}")
        try:
            data = load_config_file(config_path)
            existing_cfg = AppConfig(**data)
        except Exception as e:
            warn(f"Could not load existing config ({e}), will recreate.")

    cfg = interactive_config_menu(existing_cfg)
    write_config_file(config_path, cfg)
    ensure_data_files(cfg)

    if verify_environment(cfg):
        info("Setup verification successful.")
        info("You can now run the app with: whatsapp-filter")
        info("Or re-open this menu anytime with: whatsapp-filter --config-menu")
        return cfg
    else:
        warn("Setup verification failed. Fix the above issues before running the app.")
        return None


def run_config_menu_only(config_path: Path) -> None:
    existing_cfg: Optional[AppConfig] = None
    if config_path.exists():
        try:
            data = load_config_file(config_path)
            existing_cfg = AppConfig(**data)
        except Exception as e:
            warn(f"Could not load existing config ({e}), starting fresh.")

    cfg = interactive_config_menu(existing_cfg)
    write_config_file(config_path, cfg)
    ensure_data_files(cfg)
    info("Config menu finished. You can now run: whatsapp-filter")


def run_from_config(cfg: AppConfig) -> None:
    start_ts = time.time()
    cwd = Path.cwd()
    info(f"Current working directory: {cwd}")
    info(f"Using config: {cfg}")

    input_path = (cwd / cfg.input).resolve()
    valid_path = (cwd / cfg.valid_output).resolve()
    invalid_path = (cwd / cfg.invalid_output).resolve()
    log_path = (cwd / cfg.log_file).resolve()

    info(f"Input file: {input_path}")
    info(f"Valid output: {valid_path}")
    info(f"Invalid output: {invalid_path}")
    info(f"Log file: {log_path}")

    if not input_path.exists():
        error(f"Input file not found: {input_path}")
        raise SystemExit(1)

    numbers = read_numbers_from_file(input_path)
    info(f"Loaded {len(numbers)} numbers from {input_path}")
    info(f"Browser: {cfg.browser}")
    info(f"Mode: {cfg.mode}")

    if cfg.driver_path:
        info(f"Using custom driver path: {cfg.driver_path}")

    if cfg.mode == "single":
        driver = create_driver(
            browser=cfg.browser,
            headless=cfg.headless,
            driver_path=cfg.driver_path,
            profile_suffix="single",
        )
        driver.get(WHATSAPP_WEB_URL)
        try:
            wait_for_login(driver)
            valid, invalid = filter_numbers_single(
                driver=driver,
                numbers=numbers,
                per_number_delay=cfg.delay,
                valid_path=valid_path,
                invalid_path=invalid_path,
            )
        finally:
            driver.quit()

    elif cfg.mode == "onedriver":
        driver = create_driver(
            browser=cfg.browser,
            headless=cfg.headless,
            driver_path=cfg.driver_path,
            profile_suffix="single",
        )
        driver.get(WHATSAPP_WEB_URL)
        try:
            wait_for_login(driver)
            valid, invalid = filter_numbers_one_driver_threaded(
                driver=driver,
                numbers=numbers,
                per_number_delay=cfg.delay,
                valid_path=valid_path,
                invalid_path=invalid_path,
                max_workers=cfg.threads,
            )
        finally:
            driver.quit()

    else:  # threaded
        prepare_worker_profiles(browser=cfg.browser, max_workers=cfg.threads)
        valid, invalid = filter_numbers_threaded(
            numbers=numbers,
            per_number_delay=cfg.delay,
            valid_path=valid_path,
            invalid_path=invalid_path,
            browser=cfg.browser,
            headless=cfg.headless,
            driver_path=cfg.driver_path,
            max_workers=cfg.threads,
            chunk_size=cfg.chunk_size,
        )

    write_numbers(valid_path, valid)
    write_numbers(invalid_path, invalid)

    duration = time.time() - start_ts
    summary = (
        f"Run finished: {time.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Duration: {duration:.1f}s | "
        f"Mode: {cfg.mode} | "
        f"Input: {input_path} | "
        f"Valid: {len(valid)} -> {valid_path} | "
        f"Invalid: {len(invalid)} -> {invalid_path}"
    )
    append_log(log_path, summary)
    info(summary)
    info(f"Log appended to: {log_path}")