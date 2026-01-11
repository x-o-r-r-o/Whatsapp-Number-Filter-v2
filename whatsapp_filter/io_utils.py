# whatsapp_filter/io_utils.py
from __future__ import annotations
from pathlib import Path
from typing import List


def read_numbers_from_file(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    seen = set()
    cleaned: List[str] = []
    for line in lines:
        if not line:
            continue
        if line not in seen:
            seen.add(line)
            cleaned.append(line)
    return cleaned


def write_numbers(path: Path, numbers: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for n in numbers:
            f.write(n + "\n")
    print(f"[INFO] Wrote {len(numbers)} numbers to: {path.resolve()}")


def append_log(log_path: Path, text: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(text + "\n")


def append_number(path: Path, number: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(number + "\n")