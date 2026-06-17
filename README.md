# CyberCity — Manage

[![Part of CyberCity](https://img.shields.io/badge/CyberCity-composition-blueviolet)](https://github.com/TheCipherKeeper/cybercity)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)

Контрольная плоскость кибер-полигона CyberCity. Оркеструет инфраструктуру
цели поверх реального IaC — Proxmox API (`proxmoxer`) + Terraform/Pulumi:
provisioning узлов, **reset/rollback** к чистому состоянию через ZFS/CoW
snapshot, сетевую изоляцию сегментов, квоты и мульти-тенантность, а также
размещение и настройку доверенного out-of-band коллектора
(`cybercity-collector`) на каждом хосте. `cybercity-engine` — регистратор целей,
не симулятор: не мутирует инфру и не выдумывает исходы; все runtime-цели
(`vm`/`container`/`lite`) наблюдаются коллектором единообразно. `manage` владеет
service-mapping manifest, назначающим каждому сервису `runtime_kind` (по умолчанию
`lite`; `lite` — лёгкий stub-контейнер `cc-lite`, заменяет «simulated») — см.
umbrella ADR-0004 и manage ADR-0002.

**Статус: стартовая точка — кода пока нет.** Репозиторий переименован из
`cybercity-blueprints` (IaC-шаблоны) и переосмыслен в контрольную
плоскость; реализация на Python поверх Proxmox/Terraform — в работе.
Документация описывает целевую архитектуру.

- Канон состава, контрактов и доверительной границы — в хабе:
  [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md).
- Правила работы в репозитории: [`AGENTS.md`](AGENTS.md).
- Документация: [`docs/`](docs/) —
  [`ARCHITECTURE.md`](docs/ARCHITECTURE.md),
  [`DEVELOPMENT.md`](docs/DEVELOPMENT.md),
  [`DATA_FLOW.md`](docs/DATA_FLOW.md),
  [`adr/`](docs/adr/).

## Лицензия

- Код: [MIT](LICENSE)
- Документация: [CC BY 4.0](LICENSE-DOCS)