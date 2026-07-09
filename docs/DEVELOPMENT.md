# CyberCity Manage — Руководство разработчика

> **Кода пока нет.** Репозиторий — стартовая точка; этот документ
> описывает целевой стек и процесс, к которому идём. Разделы помечены TODO.

## Быстрый старт

> TODO: кода пока нет. Ниже — целевой quick start.

```bash
cd /path/to/cybercity-manage

# Сборка
go build ./...

# Тесты (с race-детектором и покрытием)
go test -race -coverprofile=coverage.out ./...

# Линт и статика
go vet ./...
golangci-lint run

# Запуск оркестратора (требует реального Proxmox)
go run ./cmd/cybercity-manage --proxmox-host ... provision --plan plans/lab.yaml
```

## Целевой стек

- **Язык:** Go ≥ 1.23 (модуль `github.com/TheCipherKeeper/cybercity-manage`;
  см.
  [ADR-0009](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0009-manage-implementation-language-go.md)).
- **Гипервизор:** Proxmox API через `bpg/proxmox-go-sdk` (REST).
- **IaC как библиотека:** `hashicorp/terraform-exec` / **Pulumi Go SDK**
  (CDKTF-on-Go — опционально).
- **Reset:** ZFS snapshot/clone (через Proxmox API) — для `vm`; `container`/`lite`
  — пересоздание pod'а (stateless, секунды).
- **Изоляция:** gVisor / Kata-containers для контейнерных целей.
- **Конкурентность:** горутины + `context.Context` (сквозные отмены/таймауты)
  для параллельного provisioning/reset по множеству хостов.
- **Runtime-aware provisioning:** `runtime_kind ∈ {vm, container, lite}` из
  service-mapping manifest
  ([ADR-0004](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0004-runtime-kind-vm-container-lite.md))
  выбирает шаблон. `lite` — stub-образ `cc-lite`
  (реальный сокет + подделанный баннер), заменяет «simulated»; по умолчанию `lite`.

## Инструментарий (целевой)

> manage реализуется на Go
> ([ADR-0009](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0009-manage-implementation-language-go.md));
> ранее планировавшийся Python-инструментарий
> (по образцу `cybercity-data`: ruff/mypy/pytest/hypothesis) более не применяется.
> Концепция двойного CI (отдельные пайплайны на lint и test) сохраняется. Пока
> всё — TODO.

- **golangci-lint** — линтер (набор: `govet`, `staticcheck`, `errcheck`, `revive`,
  `gocritic`, `unused`, `lll` line-length 100).
- **go vet / staticcheck** — статический анализ.
- **go test** — тесты; `-race` (детектор гонок), `-coverprofile` (покрытие);
  целевой порог покрытия — по образцу `cybercity-data` 95% (aspiration, per-package).
- **`pgregory.net/rapid`** — property-based тесты (вместо `hypothesis`).
- **table-driven tests** (stdlib `testing`) / `testify` (опционально) — assertions.
- **goimports / gofumpt** — форматирование.
- **Двойной CI** (как в data) — отдельные пайплайны на lint и test.

## Тестирование

> TODO: кода пока нет, тестировать нечего. Цель — по образцу `cybercity-data`,
> адаптированному под Go.

```bash
# Все тесты
go test ./...

# С race-детектором и покрытием
go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Конкретный пакет
go test ./internal/domain -v

# Интеграционные тесты (требуют реального Proxmox)
go test -tags=integration ./internal/adapters/...
```

Планируемый подход:

- **Unit-тесты** на domain-логику (desired-state, quota, policy) — table-driven,
  чистые, без гипервизора.
- **Property-based** через `pgregory.net/rapid` — на аллокацию квот и policy.
- **Adapter-тесты** на fakes портов (Go-интерфейсы в `internal/ports`); реальный
  Proxmox — в интеграционных тестах за build-tag `integration`, запускаемых
  опционально (нужен гипервизор).

## Линтинг и проверки (целевые)

```bash
go vet ./...
golangci-lint run
```

## Стиль коммитов

Conventional Commits (см.
[`cybercity/CONVENTIONS.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/CONVENTIONS.md)):
`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `adr:`. Тело
коммита — на русском; summary line — английский допустим.

## Процесс ADR

ADR живут только в хабе `cybercity/adr/` (см.
[ADR-0005](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0005-adr-centralized-in-hub.md));
в этом репозитории `docs/adr/` не ведётся. Если изменение затрагивает
архитектурное решение:

1. Написать или обновить ADR в хабе `cybercity/adr/`.
2. Сослаться на него из `docs/ARCHITECTURE.md`.
3. Старые ADR помечать `superseded`, а не удалять.

## Связанные документы

- [`AGENTS.md`](../AGENTS.md) — правила для AI-агентов.
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — целевая архитектура.
- [`cybercity/adr/`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/) — все ADR (включая [ADR-0009](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0009-manage-implementation-language-go.md) — Go как язык реализации manage).
- [`cybercity-data/pyproject.toml`](https://github.com/TheCipherKeeper/cybercity-data/blob/main/pyproject.toml) — эталон Python-инструментария (более не применяется в manage; сохранён как референс двойного CI).