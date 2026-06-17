# ADR-0001: Контрольная плоскость поверх реального IaC

## Status

Accepted

## Context

Репозиторий вырос из `cybercity-blueprints` — набора IaC-шаблонов
(Ansible/Terraform), описывающих развёртывание полигона. По мере того как
проект приобрёл контрольную плоскость (provisioning, reset/rollback,
изоляция, квоты, мульти-тенантность, размещение коллектора), «шаблоны»
перестали быть точным названием: нужна не декларация инфры один раз, а
runtime, который постоянно оркеструет гипервизор/фабрику в ответ на
команды и события.

Перед нами стоял выбор:

1. **Оставаться «шаблонами»** — чисто декларативный IaC (Terraform/Pulumi
   root module, Ansible playbooks), применяемый вручную. Просто, но reset
   за секунды, квоты, TTL, мульти-тенантность и живое размещение коллектора
   требуют интерактивной плоскости управления, а не разового `apply`.
2. **Написать свой provisioning заново** — дублировать то, что уже умеют
   Proxmox API, Terraform, Pulumi. Дорого, хрупко, мимо экосистемы.
3. **Контрольная плоскость поверх реального IaC** — тонкий Python-слой,
   который дёргает Proxmox API (`proxmoxer`) и Terraform/Pulumi как
   библиотеку (`python-terraform` / CDKTF), не переписывая их.

См. также «Историю переименований» в
[`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md):
`cybercity-blueprints` → `cybercity-manage`.

## Decision

`cybercity-manage` — **контрольная плоскость**, а не набор шаблонов и не
очередной provisioning-движок. Она оркеструет реальный IaC под собой:

- Proxmox API через `proxmoxer` (REST) — создание/удаление/старт/стоп
  гостей, snapshot/clone.
- Terraform/Pulumi как библиотека (`python-terraform` / CDKTF) для
  декларативных частей, где это уместно.
- Reset/rollback — через ZFS/CoW snapshot/clone за секунды, а не пересборка
  узла.
- Изоляция — VLAN/firewall на Proxmox + gVisor/Kata-containers для
  контейнерных целей в adversarial-режиме.
- Размещение доверенного `cybercity-collector` на каждом хосте + политика
  сбора + control-канал к нему.
- Квоты / TTL / мульти-тенантность — per-team бюджеты CPU/RAM/disk,
  автоуничтожение инстансов после TTL.

`cybercity-engine` не мутирует инфру напрямую: он только *слышит* об
изменениях как о смене сим-состояния. `manage` — единственный инфра-мутатор.

## Consequences

### Positive

- Не дублируем Proxmox/Terraform/Pulumi — используем зрелые движки.
- Reset за секунды через snapshot, а не минутные пересборки.
- Чёткая граница: `manage` владеет инфрой, `engine` — событиями и scoring.
- Естественная мульти-тенантность и квоты на уровне плоскости управления.

### Negative

- Дополнительный слой над IaC — ещё одна точка интеграции и отказа.
- Требует реального Proxmox/гипервизора для полноценной работы; без него
  плоскость бесполезна (mock-режим — TODO).
- Код пока отсутствует: документ фиксирует цель, к которой идём.

## Alternatives considered

- **Чистые IaC-шаблоны (`cybercity-blueprints`)**: отвергнуто — разовый
  `apply` не даёт интерактивного reset/квот/TTL/размещения коллектора.
- **Свой provisioning с нуля**: отвергнуто — дублирование Proxmox/Terraform,
  мимо экосистемы, дорого и хрупко.
- **Делегировать reset/изоляцию in-guest агенту**: отвергнуто — нарушает
  доверительную границу (см.
  [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md));
  действие над гостем — через `manage`/фабрику, не через in-guest.

## Related

- [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md) — «История переименований», «Кто чем владеет».
- [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md) — доверительная граница; `manage` в trusted-плоскости.
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — целевая архитектура manage.