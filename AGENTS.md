# AGENTS.md — правила для AI-агентов и контрибьюторов CyberCity Manage

## Иерархия документов (от старшего к младшему)

**Над репозиторием** — хаб `cybercity` держит системные документы:

- [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md) — канон состава, контрактов, доверительной границы.
- [`cybercity/CONVENTIONS.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/CONVENTIONS.md) — кросс-репо конвенции (язык, скелет репо, ADR-формат, event envelope).
- [`cybercity/adr/`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/) — сквозные ADR (почему 6 репо, доверительная граница, Rust-коллектор).

**Внутри репозитория:**

1. `docs/adr/` — действующие архитектурные решения. ADR со статусом
   `superseded` не имеют силы.
2. `AGENTS.md` (этот файл) — операционные правила работы в репозитории.
3. `README.md` — краткое описание и quick start.
4. `docs/` — внутренняя документация (ARCHITECTURE, DEVELOPMENT, DATA_FLOW).
5. Код, тесты, конфиги — реализация принятых решений (**кода пока нет**).

Если документы противоречат друг другу, побеждает старший. Любое расхождение —
повод создать новый ADR.

## Ключевые принципы

- **Manage — единственный инфра-мутатор.** Только `manage` дёргает
  гипервизор/фабрику (provisioning, reset, изоляция). `cybercity-engine`
  только *слышит* об изменениях как о смене сим-состояния и не мутирует
  инфру.
- **Контрольная плоскость поверх реального IaC.** Оркестрируем Proxmox API
  (`proxmoxer`) + Terraform/Pulumi как библиотеку, не переписываем
  provisioning заново (см.
  [ADR-0001](docs/adr/0001-control-plane-over-real-iac.md)).
- **Reset/rollback через ZFS/CoW snapshot.** Откат к чистому состоянию за
  секунды через snapshot/clone, не пересборка узла. Золотые образы + linked
  clones.
- **Изоляция через gVisor/Kata** для контейнерных целей в adversarial-режиме;
  VLAN/firewall на Proxmox для сегментов. Нет маршрута из range в mgmt.
- **Размещение доверенного коллектора.** `manage` деплоит
  `cybercity-collector` на каждый хост, задаёт политику сбора и передаёт
  control-канал. Действие над гостем — через `manage`/фабрику, не через
  in-guest агента.
- **Доверенная плоскость.** `manage` живёт в mgmt-сегменте вместе с
  `collector` и Kafka; mTLS + ACL; гости до брокера не достукиваются (см.
  [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md)).
- **LLM — помощник, не хозяин.** LLM пишет код/YAML/документы; валидаторы,
  тесты и линтеры решают.

## Правила для AI-агентов

### Что агенту МОЖНО

- Писать планы, ADR, документацию в `docs/`.
- Описывать целевую архитектуру и целевой стек (честно помечая как цель/TODO).
- Создавать новые ADR, если меняется архитектурное решение.
- Готовить заготовки кода/тестов/`pyproject.toml` (когда начнётся
  реализация) по образцу `cybercity-data`.
- Обновлять `README.md`, `AGENTS.md` при изменении структуры.

### Чего агенту НЕЛЬЗЯ

- Фабриковать «реализованное» поведение — кода пока нет; всё целевое
  помечать как цель/TODO.
- Редактировать ADR без явного указания или создания нового ADR.
- Делать коммиты, пуши, PR — это делает человек.
- Описывать in-guest действие как способ reset/изоляции (нарушает
  доверительную границу).

## Структура репозитория

> **Кода пока нет.** Ниже — целевой макет (TODO), не текущее состояние.

```text
cybercity-manage/
├── README.md                     # краткая сводка + бейджи + quick start
├── AGENTS.md                     # этот файл
├── CONTRIBUTING.md               # указатель → docs/DEVELOPMENT.md
├── LICENSE                       # MIT
├── LICENSE-DOCS                  # CC BY 4.0
├── pyproject.toml                # TODO: зависимости и инструментарий (по образцу data)
├── src/cybercity_manage/         # TODO: код
│   ├── domain/                   # чистая логика: desired-state, quota, policy
│   ├── ports/                    # интерфейсы: HypervisorPort, IaCPort, SnapshotPort
│   ├── adapters/                 # proxmoxer, CDKTF, ZFS, gVisor/Kata, collector-placement
│   ├── application/              # оркестрация: provision, reset, isolate, place-collector
│   └── api/                      # CLI/HTTP
├── tests/                        # TODO: pytest + hypothesis
└── docs/
    ├── ARCHITECTURE.md           # целевая архитектура
    ├── DEVELOPMENT.md            # целевой стек и тестирование
    ├── DATA_FLOW.md              # потоки manage ↔ гипервизор / engine / collector
    └── adr/
        ├── README.md             # индекс ADR
        └── 0001-control-plane-over-real-iac.md
```

## Рабочий цикл (целевой)

1. Прочитать соответствующий ADR и `docs/ARCHITECTURE.md`.
2. Написать/обновить план или документацию (кода пока нет).
3. Когда появится код: `ruff check .`, `mypy .`, `pytest` (по образцу
   `cybercity-data`).
4. Показать результат пользователю. Не коммитить.

## Язык документации

Вся документация и ADR ведутся на русском языке. README может содержать
английские бейджи и ссылки, но основной текст — русский. Английский
допустим только для бейджей, идентификаторов кода, имён библиотек и
значений поля `Status:` (Accepted / Superseded / Amended).