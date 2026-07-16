# CyberCity Manage

`cybercity-manage` — Go-сервис контрольной плоскости CyberCity. Фактическое
назначение, границы и контракты описаны в `docs/ARCHITECTURE.md`, поведение
модуля — в `docs/specs/control_plane.md`, системный состав и задачи — в хабе
[`TheCipherKeeper/cybercity`](https://github.com/TheCipherKeeper/cybercity).

## Локальная проверка

```bash
gofmt -l .
go vet ./...
go test ./...
go build -o bin/cybercity-manage ./cmd/cybercity_manage
```

Локальный запуск контейнеров: `docker compose up --build`. Рабочий цикл задан
в `<methodology-repo>/docs/WORKFLOW.md`, эксплуатация — в
`<methodology-repo>/docs/OPERATIONS.md`.

## Лицензия

MIT.
