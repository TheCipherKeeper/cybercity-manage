"""Завершить проверку ошибкой, если gofmt называет хотя бы один файл."""

from __future__ import annotations

import subprocess


def main() -> int:
    completed = subprocess.run(
        ["gofmt", "-l", "."], check=True, capture_output=True, text=True
    )
    files = completed.stdout.strip()
    if files:
        print(files)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
