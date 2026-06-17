# CyberCity Manage — Архитектура

## TL;DR

`cybercity-manage` — **контрольная плоскость** кибер-полигона CyberCity.
Она оркеструет гипервизор/фабрику: provisioning узлов, reset/rollback к
чистому состоянию, сетевую изоляцию сегментов, квоты и мульти-тенантность,
а также размещает и настраивает доверенный out-of-band коллектор
(`cybercity-collector`) на каждом хосте. `cybercity-engine` — регистратор целей,
не симулятор: он не мутирует инфру и не выдумывает исходы; все runtime-цели
(`vm`/`container`/`lite`) наблюдаются коллектором единообразно.

> **Целевая архитектура.** Кода пока нет; этот документ описывает цель, к
> которой идёт репозиторий (стартовая точка). Системный контекст
> (диаграмма, таблица ответственностей, слои развёртывания, observability,
> модель безопасности на системном уровне) — в
> [`cybercity/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/ARCHITECTURE.md).
> Ниже — только внутреннее устройство контрольной плоскости.

## Роль в системе

- **Единственный инфра-мутатор.** `manage` — единственный компонент,
  который дёргает гипервизор/фабрику. `engine` — регистратор целей (не симулятор):
  слышит об этом как о смене реестра целей; `collector` наблюдает снаружи и не
  действует над гостем.
- **Владелец service-mapping manifest.** `manage` назначает каждому сервису
  `runtime_kind ∈ {vm, container, lite}` (deployment-time, по умолчанию `lite`;
  см. ADR-0002 и umbrella ADR-0004).
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
- **`runtime_kind {vm, container, lite}` (deployment-time).** `manage` владеет
  service-mapping manifest, назначающим каждому сервису runtime-вид (по умолчанию
  `lite`). `vm` — реальная VM; `container` — обычный контейнер; `lite` — максимально
  лёгкий stub-контейнер (образ `cc-lite`), заменяющий прежнее понятие «simulated».
- **Образ `cc-lite`.** Параметризуемый stub-контейнер: биндит порты из топологии,
  подделанный баннер по `honeypot`-fingerprint, heartbeat коллектору. Реальная, но
  лёгкая runnable-сущность — массовка графа без нового класса доверия.

## Service-mapping manifest (целевой)

`manage` владеет manifest, сопоставляющим `service_id` (из `cybercity-data`)
runtime-виду и шаблону провижнинга. Это deployment-time конфигурация, НЕ часть
декларативной модели (`cybercity-data` про `runtime_kind` не знает):

```yaml
# deployment/<env>/services.yaml — manage-owned
services:
  bank-web:       { runtime_kind: vm,        template: debian12-nginx-cve2023xxxx }
  bank-log:       { runtime_kind: container,  template: nginx-log-collector }
  mall-pos-42:    { runtime_kind: lite }
  honeypot-ssh:   { runtime_kind: lite,      honeypot: true }
  # всё не перечисленное — по умолчанию runtime_kind: lite
```

`honeypot`-флаг здесь — лишь указание провижнингу исполнить lite-стаб как наживку
(fingerprint/баннер берётся из `cybercity-data`); само назначение-наживки —
топологическое свойство в data (см. data ADR-0019), ортогональное `runtime_kind`.

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
scoring. Коллектор кроет все runtime-виды единообразно — `vm` (на гипервизоре),
`container` и `lite` (на K8s-узле/хосте); `lite`-стабы — как любой runnable-гость
(баннер/socket-reachability + heartbeat). Класса «engine-synthesized service
events» нет: движок — регистратор, не симулятор.

## Квоты / TTL / мульти-тенантность (целевые)

- per-team / per-tenant бюджеты CPU/RAM/disk.
- TTL на инстансы: автоуничтожение после истечения срока (sandbox-учения).
- Изоляция арендаторов через сегменты и сетевые политики.

## Reset / rollback (целевой)

Reset = откат к чистому состоянию за секунды, не пересборка узла. Способ зависит
от `runtime_kind`:

- **`vm`** — ZFS/CoW snapshot/clone золотого образа; linked clones дают
  воспроизводимые стартовые точки для каждого учения.
- **`container` / `lite`** — пересоздание pod'а из образа (stateless, секунды);
  `lite`-стабы сбрасываются мгновенно, т.к. не имеют состояния.

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
├── adapters/        # proxmoxer, CDKTF, ZFS, gVisor/Kata, collector-placement, cc-lite
├── application/     # оркестрация команд: provision, reset, isolate, quota, place-collector, map-runtime-kind
└── api/             # CLI/HTTP для команд от оператора/engine
```

`domain` не знает про Proxmox/Terraform/ZFS; все внешние действия — через
порты, как и onion-макет движка (см.
[`cybercity-engine/docs/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity-engine/blob/main/docs/ARCHITECTURE.md)).

## Связанные документы

- [`cybercity/ARCHITECTURE.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/ARCHITECTURE.md) — системная архитектура (контекст).
- [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md) — канон состава и границ ответственности.
- [`adr/0001-control-plane-over-real-iac.md`](adr/0001-control-plane-over-real-iac.md) — почему контрольная плоскость поверх реального IaC.
- [`adr/0002-runtime-kind-manifest.md`](adr/0002-runtime-kind-manifest.md) — service-mapping manifest; `runtime_kind {vm, container, lite}`; образ `cc-lite`.
- [`DEVELOPMENT.md`](DEVELOPMENT.md) — целевой стек и тестирование.
- [`DATA_FLOW.md`](DATA_FLOW.md) — потоки manage ↔ гипервизор / engine / collector.