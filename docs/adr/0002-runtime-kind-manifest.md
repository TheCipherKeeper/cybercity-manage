# ADR-0002: Service-mapping manifest — `runtime_kind {vm, container, lite}`

## Status

Accepted

## Context

Сквозное решение (umbrella ADR-0004) упрощает runtime-модель: вместо
`{real, simulated, decoy}` — `runtime_kind ∈ {vm, container, lite}` (deployment-time)
+ ортогональный флаг назначения `honeypot`. «simulated» (хост, который движок
*выдумывал*, не существовал как runnable-сущность и не снампился по TCP) заменён на
`lite` — максимально лёгкий stub-контейнер с реальным сокетом и подделанным баннером.
Движок при этом становится **регистратором**, а не симулятором: класса
«engine-synthesized service events» больше нет, все runtime-цели наблюдаются
коллектором единообразно.

`runtime_kind` — deployment-time concern, он НЕ принадлежит декларативной модели
(`cybercity-data` про него не знает). Значит, его должен владеть `cybercity-manage` —
единственный инфра-мутатор и место, где provisioning встречается с топологией.

## Decision

`cybercity-manage` владеет **service-mapping manifest**, сопоставляющим `service_id`
(из `cybercity-data`) с runtime-видом и шаблоном провижнинга:

```yaml
# deployment/<env>/services.yaml — manage-owned
services:
  bank-web:       { runtime_kind: vm,        template: debian12-nginx-cve2023xxxx }
  bank-log:       { runtime_kind: container,  template: nginx-log-collector }
  mall-pos-42:    { runtime_kind: lite }
  honeypot-ssh:   { runtime_kind: lite,      honeypot: true }
  # всё не перечисленное — по умолчанию runtime_kind: lite
```

- **`vm`** — реальная VM (Proxmox): golden image + ZFS/CoW linked clone.
- **`container`** — обычный контейнер (gVisor/Kata в adversarial-режиме).
- **`lite`** (по умолчанию) — stub-контейнер на образе **`cc-lite`**: параметризуемый
  бинарь, биндит порты из топологии, подделанный баннер по `honeypot`-fingerprint,
  heartbeat коллектору. Реальная, но лёгкая runnable-сущность — заменяет «simulated».
- **`honeypot`** в manifest — лишь указание провижнингу исполнить lite-стаб как наживку
  (fingerprint/баннер берётся из `cybercity-data`); само назначение-наживки —
  топологическое свойство в data (см. data ADR-0019), ортогональное `runtime_kind`.

Reset зависит от вида: `vm` — ZFS snapshot/clone; `container`/`lite` — пересоздание
pod'а из образа (stateless, секунды; `lite` мгновенно, т.к. без состояния). Коллектор
кроет все три вида единообразно (out-of-band): `vm` — на гипервизоре, `container`/
`lite` — на K8s-узле/хосте.

## Consequences

- Все runtime-цели runnable и наблюдаются единообразно; движок — регистратор.
- Home lab feasible: большинство сервисов — `lite`, горстка `vm` для hands-on.
- `cybercity-data` остаётся чисто декларативным (не знает `runtime_kind`).
- Массовка графа (прежние «simulated»/«mock») — это `lite`-стабы, а не выдуманные
  движком хосты; плотность без нового класса доверия.
- Код (загрузка manifest, образ `cc-lite`, диспетч provisioning по kind) — TODO
  (репозиторий к нему не дорос); фиксируется этим ADR как цель.

## Alternatives considered

- **`runtime_kind` в `cybercity-data`.** Нет: deployment-time concern, засоряет
  декларативную модель; data не должен знать, *как* исполняется сервис.
- **Оставить «simulated» (движок-эмулятор).** Нет: небегаемая выдуманная сущность вне
  доверительной границы; усложняет scoring отдельным классом engine-synth-событий.
  См. umbrella ADR-0004.
- **`lite` без реального сокета (fake-ответ в коде движка).** Нет: ломает единообразие
  наблюдения и возвращает движок к роли симулятора.

## Related

- [`cybercity/adr/0004-runtime-kind-vm-container-lite.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0004-runtime-kind-vm-container-lite.md) — umbrella: `runtime_kind {vm, container, lite}` + `honeypot` purpose; движок = регистратор; «decoy»/«simulated» упразднены.
- [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md) — доверительная граница; collector-signed = scoring.
- [`cybercity/adr/0003-collector-rust-out-of-band.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0003-collector-rust-out-of-band.md) — коллектор кроет все runtime-виды.
- [ADR-0001](0001-control-plane-over-real-iac.md) — manage — контрольная плоскость над IaC.
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — целевой стек, service-mapping manifest, reset per kind.
- [`cybercity-data/docs/adr/0019-service-honeypot-purpose.md`](https://github.com/TheCipherKeeper/cybercity-data/blob/main/docs/adr/0019-service-honeypot-purpose.md) — `honeypot` — топологическое свойство в data.