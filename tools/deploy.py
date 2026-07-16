"""Локальная поставка бинарного файла в каталог тестовой среды."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: deploy.py ARTIFACT_DIR COMMIT")
    artifact_dir = Path(sys.argv[1]).resolve()
    commit = sys.argv[2]
    candidates = [path for path in artifact_dir.rglob("cybercity-manage") if path.is_file()]
    if len(candidates) != 1 or candidates[0].stat().st_size == 0:
        raise SystemExit("проверка готовности: бинарный файл отсутствует")
    target = Path(".deploy/test") / commit
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidates[0], target / "cybercity-manage")
    print(f"готовность: {target}")
    print("быстрая проверка: бинарный файл непуст")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
