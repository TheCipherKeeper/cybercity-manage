# CyberCity — Blueprints

[![Part of CyberCity](https://img.shields.io/badge/CyberCity-composition-blueviolet)](#)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)

IaC для развёртывания узлов полигона на **Proxmox VE**: плейбуки Ansible,
модули Terraform, шаблоны VM, сетевые мосты. Полигон может жить и в K8s
(см. [`cybercity-core`](https://github.com/TheCipherKeeper/cybercity)),
но базовые узлы — обычные VM на Proxmox.

## Что внутри

```
provisioning/
  ansible/
    roles/
      common/        базовая настройка ОС, firewall, NTP
      k8s-node/      kubeadm join, CNI prerequisites
      ot-sim/        эмулятор SCADA-узла
      corp-workstation/  типичная рабочая станция + decoy-сервисы
  terraform/
    proxmox/         модули для VM, бриджей, storage
  pve-templates/     cloud-init шаблоны (Debian, Ubuntu, Windows)
  network/           чертежи VLAN/сегментов полигона
```

## Сегменты

| Сегмент | VLAN | Назначение |
|---|---|---|
| `mgmt` | 10 | MSP, мониторинг, бэкапы |
| `corp` | 20 | рабочие станции, серверы организаций |
| `ot` | 30 | SCADA, контроллеры, эмуляторы АСУ ТП |
| `public` | 40 | DMZ, публичные порталы (Ingress) |
| `red-team` | 50 | изолированная сеть атакующего |

Изоляция сегментов = `NetworkPolicy` в K8s (ADR-0007) и **VLAN + firewall rules**
на уровне Proxmox.

## Композиция CyberCity

| Слой | Репозиторий |
|---|---|
| Профиль / витрина | [TheCipherKeeper](https://github.com/TheCipherKeeper/TheCipherKeeper) |
| Сайт | [thecipherkeeper.github.io](https://github.com/TheCipherKeeper/thecipherkeeper.github.io) |
| Core | [cybercity](https://github.com/TheCipherKeeper/cybercity) |
| Данные | [cybercity-data](https://github.com/TheCipherKeeper/cybercity-data) |
| Сценарии | [cybercity-scenarios](https://github.com/TheCipherKeeper/cybercity-scenarios) |
| UI | [cybercity-ui](https://github.com/TheCipherKeeper/cybercity-ui) |
| Агенты | [cybercity-agents](https://github.com/TheCipherKeeper/cybercity-agents) |
| **Blueprints (этот репо)** | **cybercity-blueprints** |

## Лицензия

- Код / IaC: [MIT](LICENSE)
- Документация: [CC BY 4.0](LICENSE-DOCS)
