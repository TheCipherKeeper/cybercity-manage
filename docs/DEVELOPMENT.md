# CyberCity Manage — Руководство разработчика

> **Кода пока нет.** Репозиторий — стартовая точка; этот документ
> описывает целевой стек и процесс, к которому идём. Разделы помечены TODO.

## Быстрый старт

> TODO: кода пока нет. Ниже — целевой quick start.

```bash
cd /path/to/cybercity-manage

# Установка окружения (целевое)
uv sync            # или pip install -e .[dev]

# Запуск тестов
pytest

# Линт и типы
ruff check .
mypy .

# Запуск оркестратора (требует реального Proxmox)
cybercity-manage --proxmox-host ... provision --plan plans/lab.yaml
```

## Целевой стек

- **Язык:** Python ≥ 3.12.
- **Гипервизор:** Proxmox API через `proxmoxer` (REST).
- **IaC как библиотека:** `python-terraform` / CDKTF (Pulumi).
- **Reset:** ZFS snapshot/clone (через Proxmox API).
- **Изоляция:** gVisor / Kata-containers для контейнерных целей.

## Инструментарий (целевой, по образцу `cybercity-data`)

> Зрелый Python-репозиторий `cybercity-data` задаёт конвенцию
> инструментария; manage планирует её перенять. Пока всё — TODO.

- **ruff** — линтер/форматтер (`E,F,I,B,UP`, line-length 100, py312).
- **mypy --strict** — статическая типизация (`warn_unused_ignores`,
  `show_error_codes`).
- **pytest + pytest-cov** — тесты с покрытием; целевой порог
  `--cov-fail-under=95` (как в `cybercity-data`).
- **hypothesis** — property-based тесты.
- **pre-commit** — git hooks (ruff, mypy).
- **Двойной CI** (как в data) — отдельные пайплайны на lint и test.

Эталон конфигурации —
[`cybercity-data/pyproject.toml`](https://github.com/TheCipherKeeper/cybercity-data/blob/main/pyproject.toml).

## Тестирование

> TODO: кода пока нет, тестировать нечего. Цель — по образцу `cybercity-data`.

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=cybercity_manage --cov-fail-under=95

# Конкретный модуль
pytest tests/test_provision.py -v
```

Планируемый подход:

- **Unit-тесты** на domain-логику (desired-state, quota, policy) — чистые,
  без гипервизора.
- **Property-based** через `hypothesis` — на аллокацию квот и policy.
- **Adapter-тесты** на fakes/mocks портов; реальный Proxmox — в
  интеграционных тестах, помеченных и запускаемых опционально (нужен
  гипервизор).

## Линтинг и проверки (целевые)

```bash
ruff check .
mypy .
```

## Стиль коммитов

Conventional Commits (см.
[`cybercity/CONVENTIONS.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/CONVENTIONS.md)):
`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `adr:`. Тело
коммита — на русском; summary line — английский допустим.

## Процесс ADR

Если изменение затрагивает архитектурное решение:

1. Написать или обновить ADR в `docs/adr/`.
2. Сослаться на него из `docs/ARCHITECTURE.md`.
3. Старые ADR помечать `superseded`, а не удалять.

## Связанные документы

- [`AGENTS.md`](../AGENTS.md) — правила для AI-агентов.
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — целевая архитектура.
- [`cybercity-data/pyproject.toml`](https://github.com/TheCipherKeeper/cybercity-data/blob/main/pyproject.toml) — эталон Python-инструментария.