# CyberCity — Manage

[![Part of CyberCity](https://img.shields.io/badge/CyberCity-composition-blueviolet)](https://github.com/TheCipherKeeper/cybercity)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)

Контрольная плоскость кибер-полигона CyberCity. Оркеструет инфраструктуру
цели: provisioning узлов, **reset/rollback** к чистому состоянию, изоляцию
сегментов, квоты и мульти-тенантность. Размещает и настраивает доверенный
out-of-band коллектор (`cybercity-collector`) на каждом хосте.

Пишется на **Python** и лежит **поверх реального IaC** — Proxmox API +
Terraform/Pulumi, — а не переписывает provisioning заново. Reset = откат
снапшота (ZFS/CoW) за секунды, не пересборка.

> Бывший `cybercity-blueprints` (IaC-шаблоны Ansible/Terraform). Переименован
> и переосмыслен в контрольную плоскость. Канон композиции —
> [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md).

## Зоны ответственности

- **Provisioning / reset / изоляция на уровне инфры** — здесь (гипервизор/фабрика).
  `cybercity-engine` только *слышит* об этом как о смене сим-состояния.
- **Размещение коллектора** — деплой `cybercity-collector` на каждый хост +
  политика сбора; передаёт ему control-канал.
- **Квоты / TTL / мульти-тенантность** — per-team бюджеты CPU/RAM/disk,
  автоуничтожение инстансов после TTL.
- **Сетевая изоляция** — VLAN/firewall сегментов (mgmt / corp / ot / public /
  red-team), отсутствие маршрута из range в mgmt.

## Стек (целевой)

- Python-оркестратор + Proxmox API (`proxmoxer` / REST) + Terraform/Pulumi
  как библиотека (`python-terraform` / CDKTF).
- ZFS snapshot/clone для мгновенного reset; золотые образы + linked clones.
- gVisor / Kata-containers для изоляции контейнерных целей в adversarial-режиме.

## Статус

**Стартовая точка.** Репозиторий переименован из `cybercity-blueprints`;
контрольная плоскость на Python + привязка к Proxmox/Terraform — в работе.

## Сегменты

| Сегмент | VLAN | Назначение |
|---|---|---|
| `mgmt` | 10 | control plane, коллектор, Kafka, SIEM, бэкапы |
| `corp` | 20 | рабочие станции, серверы организаций |
| `ot` | 30 | SCADA, контроллеры, эмуляторы АСУ ТП |
| `public` | 40 | DMZ, публичные порталы (Ingress) |
| `red-team` | 50 | изолированная сеть атакующего |

Изоляция: VLAN + firewall на Proxmox; в K8s — NetworkPolicy + Cilium.

## Лицензия

- Код: [MIT](LICENSE)
- Документация: [CC BY 4.0](LICENSE-DOCS)