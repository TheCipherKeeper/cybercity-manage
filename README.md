# CyberCity — Manage

[![Part of CyberCity](https://img.shields.io/badge/CyberCity-composition-blueviolet)](https://github.com/TheCipherKeeper/cybercity)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)

`cybercity-manage` — **контрольная плоскость** кибер-полигона CyberCity (Go).
Единственный инфра-мутатор программы: оркеструет гипервизор (Proxmox API) и
реальный IaC (Terraform/Pulumi) для provisioning узлов, **reset/rollback** к
чистому состоянию (ZFS snapshot/clone для `vm`, pod restart для
`container`/`lite`), сетевой изоляции сегментов, квот/мульти-тенантности; generic
consumer `overlays`-артефакта (собирает образы через Packer/Ansible по
service-mapping + overlay-id, деплоит — семантики vuln не знает); публикует
infra/control-события в Redpanda и выставляет control API движку (HTTP/gRPC,
разрешённый control-plane edge). `engine` — регистратор целей, не симулятор:
слышит об изменениях инфры как о смене реестра целей.

**Стек:** Go (формально —
[ADR-0009](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0009-manage-implementation-language-go.md);
один сервис — один язык)
**Брокер:** Redpanda (`broker:9092`, publisher infra/control-событий)
**Хаб:** [TheCipherKeeper/cybercity](https://github.com/TheCipherKeeper/cybercity)
— COMPOSITION/CONVENTIONS/системный compose/ADR

**Статус: стартовая точка — кода контрольной плоскости пока нет.** Репозиторий
содержит stub-точку входа (`cmd/cybercity-manage/main.go`, HTTP-заглушка,
возвращает 501) для собираемости образа; реальная реализация — в `docs/BACKLOG.md`.
Документация описывает целевую архитектуру.

- Канон состава, контрактов и доверительной границы — в хабе:
  [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md).
- Методология (правила, процедуры, факты):
  [TheCipherKeeper/ai-project-template](https://github.com/TheCipherKeeper/ai-project-template)
  — роутер `docs/INDEX.md`.
- Правила работы в репозитории: [`AGENTS.md`](AGENTS.md).
- Документация: [`docs/`](docs/) —
  [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) (внутренняя архитектура + потоки +
  доверительная граница),
  [`BACKLOG.md`](docs/BACKLOG.md) (очередь задач),
  [`specs/`](docs/specs/) (контракты модулей),
  [`DEVELOPMENT.md`](docs/DEVELOPMENT.md) (целевой стек и тестирование).
- Архитектурные решения (ADR) — в хабе:
  [`cybercity/adr/`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/).

## Quick start

```bash
cp .env.example .env            # заполнить per-сервис конф (секретов в репо нет)
docker compose up --build       # брокер Redpanda + manage (stub на :8081)
```

Stub слушает на `:8081` (control API placeholder) и возвращает 501 — реальная
контрольная плоскость в работе (`docs/BACKLOG.md`).

Сборка бинарника (требуется установленный `go`; в окружении агента `go`
отсутствует — прогон отложен):

```bash
go build -o bin/cybercity-manage ./cmd/cybercity-manage
```

## Лицензия

- Код: [MIT](LICENSE)
- Документация: [CC BY 4.0](LICENSE-DOCS)