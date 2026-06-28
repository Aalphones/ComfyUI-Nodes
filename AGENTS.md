# ComfyUI Batch Suite

Wiederverwendbare Batch-Infrastruktur für ComfyUI als Custom-Node-Paket.

## Stack

- Python 3.11+, ComfyUI Custom Nodes API
- Plain JavaScript (kein Framework) für das Frontend
- Kein Test-Framework (noch)

## Kontext & Ziele

Siehe [docs/PROJECT.md](docs/PROJECT.md)

## Verzeichnisstruktur (Ziel)

```
batch_suite/
├── core/          # Batch Engine, Queue Manager, Filename Generator, …
├── providers/     # Datenquellen (Image, Prompt, …)
├── nodes/         # ComfyUI-Node-Adapter
└── web/           # JS-Frontend (Fortschritt, Drag & Drop, …)
```

ComfyUI-Nodes liegen in `batch_suite/nodes/`. Der Root enthält nur noch den
Paket-Einstieg für ComfyUI und Projektdokumentation.

## Konventionen

- [docs/conventions/python.md](docs/conventions/python.md)

## Aktiver Plan

Siehe [STATE.md](STATE.md)
