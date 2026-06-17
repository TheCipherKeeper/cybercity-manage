# CyberCity Manage — Поток данных

> **Целевой поток.** Кода пока нет; документ описывает, как manage
> взаимодействует с гипервизором, движком и коллектором по задумке.

## Роль в потоке

`cybercity-manage` — единственный инфра-мутатор. Он не производит события
для scoring сам; он меняет инфру, и `cybercity-engine` слышит об этом как
о смене сим-состояния. Поток scoring живёт на доверенной плоскости
(`manage` + `collector` + Kafka), см.
[`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md).

## Целевые потоки

```text
1. Команда оператора/engine → manage
      provision / reset / isolate / place-collector / set-quota

2. manage → гипервизор/фабрика (Proxmox API, Terraform/Pulumi)
      создание/удаление гостей, snapshot/clone, VLAN/firewall, gVisor/Kata

3. manage → cybercity-collector (control-канал, mgmt-сегмент)
      «наблюдать X», «снапшот сейчас», «обновить политику сбора»
      placement: деплой коллектора на хост + политика

4. manage → cybercity-engine (уведомление о смене инфры)
      «узел bank-web reset к t0», «сегмент ot изолирован»
      engine слышит это как смену сим-состояния, не мутирует инфру сам

5. cybercity-collector → Kafka (mgmt) → cybercity-engine
      подписанные (Ed25519) события наблюдения; на них считается scoring
      (этот поток — между collector и engine, не через manage)

6. Опционально: engine → manage (командный запрос)
      «сделай snapshot сейчас», «изолируй скомпрометированный сегмент»
      engine просит действие, manage исполняет на гипервизоре
```

## Что manage НЕ делает

- **Не считает scoring.** Scoring — на потоке `collector → engine`.
- **Не наблюдает гостей.** Наблюдение — задача `cybercity-collector`.
- **Не пишет события в событийный граф.** `engine` — единственный мутатор
  состояния; manage только меняет инфру и уведомляет.

## Граница доверия

- Control-канал `manage → collector` и уведомления `manage → engine` идут
  по mgmt-плоскости (mTLS), без маршрута из range.
- Действие над гостем (reset/изоляция) — всегда через `manage`/фабрику,
  не через in-guest агента.

## Связанные документы

- [`cybercity/COMPOSITION.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/COMPOSITION.md) — «Поток данных и контракты» (канон).
- [`cybercity/adr/0002-trust-boundary.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/0002-trust-boundary.md) — доверительная граница.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — целевая архитектура manage.
- [`cybercity-engine/docs/DATA_FLOW.md`](https://github.com/TheCipherKeeper/cybercity-engine/blob/main/docs/DATA_FLOW.md) — поток событий в движке.