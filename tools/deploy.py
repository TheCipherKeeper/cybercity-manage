"""Запуск и HTTP-проверка собранного сервиса в тестовом окружении."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: deploy.py ARTIFACT_DIR COMMIT")
    artifact_dir = Path(sys.argv[1]).resolve()
    commit = sys.argv[2].strip()
    candidates = [path for path in artifact_dir.rglob("cybercity-manage") if path.is_file()]
    if not commit or len(candidates) != 1 or candidates[0].stat().st_size == 0:
        raise SystemExit("ожидались непустой commit и один бинарный файл cybercity-manage")

    executable = candidates[0]
    executable.chmod(executable.stat().st_mode | 0o100)
    port = free_port()
    environment = os.environ.copy()
    environment["MANAGE_HTTP_ADDR"] = f"127.0.0.1:{port}"
    process = subprocess.Popen(
        [str(executable)], env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    body = b""
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise SystemExit("сервис завершился до проверки готовности")
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            except urllib.error.HTTPError as error:
                body = error.read()
                if error.code == 501:
                    break
            except urllib.error.URLError:
                time.sleep(0.1)
        else:
            raise SystemExit("проверка готовности не дождалась HTTP-ответа")
        if body != "manage stub — not implemented\n".encode():
            raise SystemExit("быстрая проверка получила неожиданный HTTP-ответ")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    print(f"cybercity-manage {commit}: запуск, готовность и быстрая проверка успешны")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
