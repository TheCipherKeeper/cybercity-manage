# control-plane

> Спека главного планируемого модуля manage — оркестрации контрольной
> плоскости (`internal/application` + `internal/ports` + `internal/adapters`).
> Канон структуры —
> [TheCipherKeeper/ai-project-template](https://github.com/TheCipherKeeper/ai-project-template)/docs/refs/SPEC.md;
> **внутренняя архитектура (usecases/ports/domain/adapters) —
> `…/docs/refs/MODULE.md`**; процедура заведения — `…/docs/guide/20-define-module.md`.
>
> **Статус: stub / placeholder.** Кода контрольной плоскости пока нет (стартовая
> точка). Секция «Что есть» — честно пуста (только stub-HTTP в
> `cmd/cybercity-manage/main.go`, возвращающий 501, к этому модулю не относится);
> «Что TODO» — полный план. Не выдавать stub за реализацию.

Модуль `control-plane` (условно объединяет `internal/application` + зависимые
`ports`/`adapters`/`domain` в один логический контракт; при реализации может
быть разбит на несколько спек по одному на Go-пакет) — оркестрация
инфра-мутаций: provisioning, reset/rollback, изоляция, квоты, control API к
engine, публикация infra/control-событий в брокер. Граница: manage —
единственный инфра-мутатор; engine слышит об изменениях, не мутирует инфру.

## Интерфейсы

> Юзкейсы. На каждый — input port (`execute(In) -> Out`/ошибки) + потребляемые
> output ports (`internal/ports`).

- `Provision.execute(in: ProvisionInput) -> Result<ProvisionResult, ManageError>`
  — провижнинг runtime-цели по `service_id` + service-mapping. Потребляет:
  `HypervisorClient`, `EventPublisher` (публикация `infra.provisioned`).
- `Reset.execute(in: ResetInput) -> Result<ResetResult, ManageError>` —
  rollback к чистому состоянию. Потребляет: `HypervisorClient`,
  `EventPublisher` (`control.reset`).
- `Isolate.execute(in: IsolateInput) -> Result<IsolateResult, ManageError>` —
  сетевая изоляция сегмента. Потребляет: `HypervisorClient` (VLAN/firewall),
  сетевой адаптер (Cilium/NetworkPolicy), `EventPublisher` (`control.isolate`).
- `SetQuota.execute(in: QuotaInput) -> Result<QuotaResult, ManageError>` —
  установка per-team/per-tenant бюджетов CPU/RAM/disk + TTL. Потребляет:
  `HypervisorClient`/IaC, (опц.) `EventPublisher`.
- `ControlSnapshot.execute(in: SnapshotRequest) -> Result<SnapshotRef, ManageError>`
  — запрос снапшота от engine (control API). Потребляет: `HypervisorClient`,
  `EventPublisher` (`control.snapshot`).
- `ReloadTopology.execute(in: ReloadInput) -> Result<ReloadResult, ManageError>`
  — reload топологии/service-mapping (control API от engine/оператора).
- `PlaceCollector.execute(in: PlacementInput) -> Result<PlacementResult, ManageError>`
  — размещение `cybercity-collector` на хосте + политика сбора (control-канал
  к collector'у). Потребляет: коллектор-адаптер.

## Типы

> Go-типы (целевые). Приведены как канон; детали — при реализации.

```go
// internal/domain
type RuntimeKind string // "vm" | "container" | "lite"

type ServiceMapping struct {
    ServiceID   string
    RuntimeKind RuntimeKind
    Template    string // golden image / образ / cc-lite дескриптор
    Honeypot    bool
}

type SegmentID string // "mgmt" | "corp" | "ot" | "public" | "red-team"

// internal/ports
type HypervisorClient interface { /* Proxmox: create/delete/start/stop/snapshot/clone/vlan */ }
type IacRunner interface        { /* Terraform/Pulumi apply */ }
type OverlayConsumer interface   { /* read overlays by overlay-id, build image */ }
type EventPublisher interface    { /* publish infra.provisioned / control.* to Redpanda */ }
type ControlAPI interface        { /* HTTP/gRPC control-plane edge to engine */ }

// per-usecase DTO
type ProvisionInput struct {
    ServiceID string
    Mapping   ServiceMapping
}
type ProvisionResult struct {
    NodeID     string
    RuntimeKind RuntimeKind
    Ready       bool
}

type ManageError struct {
    Kind    ManageErrorKind // InvalidInput | HypervisorError | NotAllowed | NotFound | BrokerError
    Message string
    Cause   error
}
```

## Что есть

> Честно: реализованного поведения контрольной плоскости **нет**. Код
> отсутствует (стартовая точка). Stub `cmd/cybercity-manage/main.go` поднимает
> HTTP-точку на `MANAGE_HTTP_ADDR`, логирует «manage stub — not implemented» и
> возвращает 501 на все маршруты — это **placeholder** для собираемости образа,
> не реализация юзкейсов; к контрактам выше отношения не имеет.

- (пусто — кода нет)

## Что TODO

> Полный план; переезжает в «Что есть» по мере реализации (см. `BACKLOG.md`).

- `Provision` для `vm`: ZFS snapshot/clone golden image → start → publish
  `infra.provisioned` (BACKLOG #2).
- `Provision` для `container`/`lite`: пересоздание pod'а; `lite` параметризуется
  дескриптором (баннер/порты) (BACKLOG #3).
- `Reset`: ZFS rollback (`vm`) / pod пересоздание (`container`/`lite`) →
  publish `control.reset` (BACKLOG #4).
- `Isolate`: VLAN/firewall (Proxmox) + Cilium/NetworkPolicy + gVisor/Kata →
  publish `control.isolate`; инвариант «нет маршрута range→mgmt» (BACKLOG #5).
- `SetQuota`: per-team/per-tenant бюджеты + TTL автоуничтожение (BACKLOG #6).
- `ControlSnapshot`: запрос снапшота от engine → publish `control.snapshot`
  (BACKLOG #8).
- `ReloadTopology`: reload service-mapping/topology (BACKLOG #8).
- `PlaceCollector`: деплой collector на хост + политика сбора.
- `EventPublisher` (Redpanda): публикация `infra.provisioned`,
  `control.snapshot`/`control.reset`/`control.isolate` в формате
  `CONVENTIONS@v1` (BACKLOG #9).
- Опц. consume `city.build.completed` — readiness перед провижнингом (BACKLOG
  #10, пока не подключено).
- Заменить stub-HTTP в `cmd/cybercity-manage/main.go` на реальный control API
  (BACKLOG #8).

## Ограничения

- Только через output ports: `application` (usecases) **никогда** не импортирует
  `adapters` напрямую (инвариант #14, `…/docs/refs/VERIFICATION.md`).
- `domain` ни от чего внутри модуля не зависит (без I/O, без ports).
- Действие над гостем — только через `HypervisorClient` (гипервизор/фабрика),
  **не** через in-guest агента (доверительная граница).
- manage **не** переписывает provisioning — оркестрирует реальный IaC
  (Terraform/Pulumi) под собой.
- manage **не** знает семантики vuln — generic consumer `overlays` (см.
  `docs/specs/overlays-consumer.md`).
- manage **не** мутирует world-state engine и **не** ходит в PostgreSQL
  (engine — единственный читатель/писатель БД).
- Шины общения: broker — для infra/control-событий; control API manage→engine —
  разрешённый control-plane edge (документирован в `docs/ARCHITECTURE.md`).

## Зависимости

> Output ports + внутренние модули + внешние библиотеки Go.

- Output ports: `internal/ports` — `HypervisorClient`, `IacRunner`,
  `OverlayConsumer`, `EventPublisher`, `ControlAPI`.
- Внутренние: `internal/domain` (доменные типы), `cmd/cybercity-manage`
  (composition root).
- Внешние (Go): `bpg/proxmox-go-sdk` (Proxmox REST),
  `hashicorp/terraform-exec` / Pulumi Go SDK (IaC), Redpanda Go client
  (`github.com/redpanda-data/redpanda-client-go` или `segmentio/kafka-go`),
  Packer/Ansible (через exec — сборка образа). Обоснование —
  [ADR-0009](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0009-manage-implementation-language-go.md).