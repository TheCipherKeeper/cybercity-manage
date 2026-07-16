# overlays-consumer

> Спека модуля generic consumption `overlays`-артефакта (`internal/adapters`
> часть + output port `OverlayConsumer`). Канон структуры —
> [TheCipherKeeper/addm](https://github.com/TheCipherKeeper/addm)/docs/ARCHITECTURE.md;
> **внутренняя архитектура — `…/docs/ARCHITECTURE.md`**; процедура —
> `…/docs/ARCHITECTURE.md`.
>
> **Статус: stub / placeholder.** Реализации нет; «Что TODO» — полный план.

Модуль generic consumer'а `overlays`-артефакта: по `service-mapping` +
`overlay-id` читает `overlays` (out-of-band файл — контракт data→manage,
[ADR-0006](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0006-vulnerability-declarative-overlay-realism.md)),
собирает образы (Packer/Ansible) и деплоит. **Семантики vuln не знает** —
generic потребитель; vuln — first-class сущность в `cybercity-data`.

## Интерфейсы

- `ConsumeOverlay.execute(in: OverlayRequest) -> Result<BuiltImage, ManageError>`
  — прочитать `overlays` по `overlay-id`, собрать образ (Packer/Ansible),
  вернуть артефакт для провижнинга. Потребляет output ports: `OverlayReader`
  (файловый), `ImageBuilder` (Packer/Ansible exec).

## Типы

```go
type OverlayRequest struct {
    ServiceID string
    OverlayID string
    Mapping   ServiceMapping // из domain
}

type BuiltImage struct {
    ImageRef string // ссылка на собранный образ (Proxmox template / OCI image)
    Kind     RuntimeKind
}
```

## Что есть

- (пусто — кода нет; stub)

## Что TODO

- `ConsumeOverlay`: чтение `overlays` по `overlay-id` (out-of-band файл) →
  сборка образа через Packer/Ansible → возврат `BuiltImage` (BACKLOG #7).
- Интеграция с `Provision` (`control-plane.md`) — образ подставляется в
  провижнинг по `runtime_kind`.
- Обработка отсутствующего `overlay-id` — понятная ошибка.
- Граница: семантика vuln **не** инспектируется (manage — generic consumer).

## Ограничения

- `overlays` — **out-of-band файловый** контракт (не брокер); в таблицу топиков
  `docs/ARCHITECTURE.md` не входит.
- manage **не** владеет контентом уязвимости (`cve_id` живёт в vuln-сущности
  data, не в дескрипторе сервиса).
- Сборка образа — через реальный IaC (Packer/Ansible), не велосипед.

## Зависимости

- Output ports: `internal/ports.OverlayReader` (файловый), `ImageBuilder`
  (Packer/Ansible exec).
- Внутренние: `internal/domain.ServiceMapping`, `control-plane.Provision`.
- Внешние: Packer, Ansible (через exec); `overlays`-артефакт от `cybercity-data`
  (файл).