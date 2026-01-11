# whatsapp_filter/logger.py
from __future__ import annotations
import sys
import time
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARN", "ERROR"]


def log(level: LogLevel, msg: str) -> None:
    """
    Simple stdout/stderr logger with timestamp and level.
    Example:
      [2026-01-12 02:45:26] [INFO] Message
    """
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    stream = sys.stdout if level in ("DEBUG", "INFO") else sys.stderr
    print(line, file=stream)


def debug(msg: str) -> None:
    log("DEBUG", msg)


def info(msg: str) -> None:
    log("INFO", msg)


def warn(msg: str) -> None:
    log("WARN", msg)


def error(msg: str) -> None:
    log("ERROR", msg)