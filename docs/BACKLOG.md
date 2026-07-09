# Backlog

Строгая последовательная очередь задач. Выполнение строго сверху вниз.
Запрещено перепрыгивать через пункты или выполнять задачи параллельно.

Правила:
- Агент берёт самый первый невыполненный `[ ]` пункт.
- После реализации: поставить `[x]`, перенести в спек (TODO → «Что есть»).
- Человек меняет порядок, добавляет задачи.

Формат задачи (тег — имя модуля из `docs/specs/<module>.md`):

```
### N. [<модуль>] Краткое название
Зависит от: N (если есть)
Спек: docs/specs/<module>.md, раздел «Что TODO».

Что сделать (что, не как).

Тесты:
- …
```

> **Статус реализации:** кода контрольной плоскости пока нет (стартовая точка;
> см. `docs/ARCHITECTURE.md` → *Модули* — запланированные TBD). Задачи ниже —
> реальная работа по выводу manage из stub в контрольную плоскость.

---

### 1. [adapters] Proxmox API client
Зависит от: —
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Реализовать output port `HypervisorClient` (Go-интерфейс в `internal/ports`) и
адаптер на `bpg/proxmox-go-sdk` (REST): создание/удаление/старт/стоп гостей,
snapshot/clone, VLAN/firewall. Конфиг — из env (`PROXMOX_API_URL`,
`PROXMOX_TOKEN`). Реальный Proxmox — в интеграционных тестах за build-tag
`integration` (опц., требует гипервизор).

Тесты:
- Unit на fake-`HypervisorClient`: старт/стоп/guest lifecycle.
- Snapshot/clone: создание и откат.
- Ошибка на невалидном `PROXMOX_API_URL`/токене.
- Интеграционный (build-tag `integration`, опц.): реальный Proxmox round-trip.

### 2. [application] ZFS snapshot/clone provisioning (vm)
Зависит от: 1
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Юзкейс `provision` для `runtime_kind: vm`: golden image + ZFS linked clone для
воспроизводимых стартовых точек. Оркестрирует `HypervisorClient` (snapshot →
clone → start). Публикует `infra.provisioned` через `EventPublisher`.

Тесты:
- Unit: provision vm → `infra.provisioned` опубликован.
- Идемпотентность по `service_id`.
- Граничный: образ отсутствует — понятная ошибка.

### 3. [application] Pod restart provisioning (container / lite)
Зависит от: 1
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Юзкейс `provision` для `runtime_kind: container`/`lite`: пересоздание pod'а из
образа (stateless, секунды). `lite` — stub-образ `cc-lite` (параметризуется
дескриптором). Публикует `infra.provisioned`.

Тесты:
- Unit: provision container → `infra.provisioned`.
- provision lite → дескриптор применён (баннер/порты).
- Reset lite: мгновенный (stateless).

### 4. [application] Reset / rollback
Зависит от: 2, 3
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Юзкейс `reset`: откат к чистому состоянию. `vm` — ZFS snapshot/clone rollback;
`container`/`lite` — пересоздание pod'а. Публикует `control.reset`.

Тесты:
- Reset vm → rollback к snapshot, `control.reset` опубликован.
- Reset container → pod пересоздан, `control.reset`.
- Reset lite → мгновенный.

### 5. [application] Изоляция сегмента (Cilium / NetworkPolicy / VLAN)
Зависит от: 1
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Юзкейс `isolate`: VLAN/firewall на Proxmox для сегментов; Cilium /
NetworkPolicy + gVisor/Kata для контейнерных целей в adversarial-режиме.
Инвариант: нет маршрута из range в mgmt. Публикует `control.isolate`.

Тесты:
- Изоляция сегмента → `control.isolate`, маршрут range→mgmt запрещён.
- Снятие изоляции (обратная операция).
- Граничный: несуществующий сегмент — ошибка.

### 6. [application] Квоты / TTL / мульти-тенантность
Зависит от: 2, 3
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Юзкейс `set-quota`: per-team/per-tenant бюджеты CPU/RAM/disk; TTL на инстансы
(автоуничтожение после истечения срока); изоляция арендаторов через сегменты.

Тесты:
- Установка квоты → применяется.
- Превышение бюджета — отклонение.
- TTL истёк → автоуничтожение.

### 7. [adapters] Overlays-artifact generic consumer (Packer / Ansible)
Зависит от: 2, 3
Спек: docs/specs/overlays-consumer.md, раздел «Что TODO».

Реализовать output port `OverlayConsumer` и адаптер: по `service-mapping` +
`overlay-id` читать `overlays`-артефакт (out-of-band файл, контракт
data→manage), собирать образы (Packer/Ansible), деплоить. **Семантики vuln не
знает** — generic consumer.

Тесты:
- Чтение `overlays` по `overlay-id` → образ собран.
- Несуществующий `overlay-id` — понятная ошибка.
- Семантика vuln не инспектируется (проверка границы).

### 8. [application] Control API к engine (start / pause / reset / snapshot / reload)
Зависится от: 4, 5
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Реализовать HTTP/gRPC control-plane edge `manage → engine`: старт/пауза/сброс
сценария, запрос снапшота, reload топологии. Разрешённый control-plane edge
(документирован в `docs/ARCHITECTURE.md` → *Доверительная граница*). Stub
`cmd/cybercity-manage/main.go` уже поднимает HTTP-точку на `MANAGE_HTTP_ADDR`
(возвращает 501) — заменить на реальную реализацию.

Тесты:
- start/pause/reset сценария → engine вызван.
- snapshot-запрос → `control.snapshot` опубликован.
- reload топологии → обновлённый service-mapping применён.
- Несуществующий scenario_id — 404.

### 9. [adapters] Брокер infra/control-topic publisher (Redpanda)
Зависит от: 2
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Реализовать output port `EventPublisher` и Redpanda-адаптер: публикация
`infra.provisioned`, `control.snapshot`, `control.reset`, `control.isolate` в
формате `CONVENTIONS@v1` (envelope из хаба `CONVENTIONS.md`). Адрес —
`BROKER_ADDR`.

Тесты:
- Публикация `infra.provisioned` → envelope валиден (`CONVENTIONS@v1`).
- Публикация `control.reset`/`control.isolate`/`control.snapshot`.
- Брокер недоступен — retry + понятная ошибка.

### 10. [application] Опц. consume `city.build.completed` (TODO)
Зависит от: 9
Спек: docs/specs/control-plane.md, раздел «Что TODO».

Опциональный consumer `city.build.completed` (событие готовности сборки от
`data`): знать, что build готов перед провижнингом. Пока **не подключено** —
честно TODO; завести consumer-loop после ввода publisher'а.

Тесты:
- Получено `city.build.completed` → readiness-флаг установлен.
- Дубликаты события — идемпотентность.