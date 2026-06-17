# CyberCity Manage — Архитектура

## TL;DR

`cybercity-manage` — **контрольная плоскость** кибер-полигона CyberCity.
Она оркеструет гипервизор/фабрику: provisioning узлов, reset/rollback к
чистому состоянию, сетевую изоляцию сегментов, квоты и мульти-тенантность,
а также размещает и настраивает доверенный out-of-band коллектор
(`cybercity-collector`) на каждом хосте. `cybercity-engine` не мутирует
инфру напрямую — он только слышит об изменениях как о смене
сим-состояния.

> **Целевая архитектура.** Кода пока нет; этот документ описывает цель, к
> которой идёт репозиторий (стартовая точка). Системный контекст
> (диаграмма, таблица ответственностей, слои развёртывания, observability,
> модель безопасности на системном уровне) — в
> [`cybercity/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/ARCHITECTURE.md).
> Ниже — только внутреннее устройство контрольной плоскости.

## Роль в системе

- **Единственный инфра-мутатор.** `manage` — единственный компонент,
  который дёргает гипервизор/фабрику. `engine` слышит об этом как о смене
  сим-состояния; `collector` наблюдает снаружи и не действует над гостем.
- **Доверенная плоскость.** `manage` живёт в mgmt-сегменте вместе с
  `collector` и Kafka-брокером, без маршрута из range. На их потоке
  считается scoring (см.
  [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md)).

## Целевой стек

- **Python-оркестратор** + **Proxmox API** (`proxmoxer` / REST) для
  управления гостями (создание/удаление/старт/стоп, snapshot/clone).
- **Terraform/Pulumi как библиотека** (`python-terraform` / CDKTF) для
  декларативных частей инфры.
- **ZFS snapshot/clone** для мгновенного reset; золотые образы + linked
  clones.
- **gVisor / Kata-containers** для изоляции контейнерных целей в
  adversarial-режиме.

## Сетевые сегменты (целевые)

| Сегмент | VLAN | Назначение |
|---|---|---|
| `mgmt` | 10 | control plane, коллектор, Kafka, SIEM, бэкапы |
| `corp` | 20 | рабочие станции, серверы организаций |
| `ot` | 30 | SCADA, контроллеры, эмуляторы АСУ ТП |
| `public` | 40 | DMZ, публичные порталы (Ingress) |
| `red-team` | 50 | изолированная сеть атакующего |

Изоляция: VLAN + firewall на Proxmox; в K8s — NetworkPolicy + Cilium.
Ключевое свойство: **нет маршрута из range-сегментов в mgmt**.

## Размещение коллектора

`manage` размещает `cybercity-collector` (Rust) по одному на каждый хост:
деплой бинарника, политика сбора (что наблюдать), передаёт ему
control-канал («наблюдать X», «снапшот сейчас», «обновить политику»).
Коллектор наблюдает гостей **снаружи** (out-of-band, read-only), подписывает
события Ed25519 и отправляет в Kafka (mgmt-плоскость). Гости до брокера не
достукиваются структурно. In-guest данные — только best-effort, не для
scoring.

## Квоты / TTL / мульти-тенантность (целевые)

- per-team / per-tenant бюджеты CPU/RAM/disk.
- TTL на инстансы: автоуничтожение после истечения срока (sandbox-учения).
- Изоляция арендаторов через сегменты и сетевые политики.

## Reset / rollback (целевой)

Reset = откат к чистому состоянию через ZFS/CoW snapshot/clone за секунды,
не пересборка узла. Золотые образы (golden images) + linked clones дают
воспроизводимые стартовые точки для каждого учения.

## Доверительная граница

- **Trusted:** `cybercity-manage` + `cybercity-collector` + Kafka-брокер —
  mgmt-сегмент, без маршрута из range. На их потоке считается scoring.
- **Best-effort:** всё внутри гостей — никогда не источник для scoring.
- Действие над гостем (reset/изоляция) — через `manage`/фабрику, не через
  in-guest агента.

Канон — в
[`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md).

## Слои (целевой макет)

> TODO: кода пока нет. Ниже — целевая слойность, не текущая реализация.

```text
manage/
├── domain/          # чистая логика: desired-state, quota, policy (без IaC-зависимостей)
├── ports/           # интерфейсы: HypervisorPort, IaCPort, SnapshotPort, ...
├── adapters/        # proxmoxer, CDKTF, ZFS, gVisor/Kata, collector-placement
├── application/     # оркестрация команд: provision, reset, isolate, quota, place-collector
└── api/             # CLI/HTTP для команд от оператора/engine
```

`domain` не знает про Proxmox/Terraform/ZFS; все внешние действия — через
порты, как и onion-макет движка (см.
[`cybercity-engine/docs/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity-engine/blob/main/docs/ARCHITECTURE.md)).

## Связанные документы

- [`cybercity/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/ARCHITECTURE.md) — системная архитектура (контекст).
- [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md) — канон состава и границ ответственности.
- [`adr/0001-control-plane-over-real-iac.md`](adr/0001-control-plane-over-real-iac.md) — почему контрольная плоскость поверх реального IaC.
- [`DEVELOPMENT.md`](DEVELOPMENT.md) — целевой стек и тестирование.
- [`DATA_FLOW.md`](DATA_FLOW.md) — потоки manage ↔ гипервизор / engine / collector.