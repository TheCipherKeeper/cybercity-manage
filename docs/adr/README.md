# ADR — cybercity-manage

Локальные архитектурные решения контрольной плоскости. Сквозные решения
(затрагивающие несколько репозиториев) — в
[`cybercity/adr/`](https://github.com/TheCipherKeeper/cybercity/blob/main/adr/).

| № | Решение | Статус |
|---|---------|--------|
| [0001](0001-control-plane-over-real-iac.md) | Контрольная плоскость поверх реального IaC, а не переописание provisioning | Accepted |
| [0002](0002-runtime-kind-manifest.md) | Service-mapping manifest; `runtime_kind {vm, container, lite}`; образ `cc-lite` | Accepted |

Формат ADR — в
[`cybercity/CONVENTIONS.md`](https://github.com/TheCipherKeeper/cybercity/blob/main/CONVENTIONS.md).