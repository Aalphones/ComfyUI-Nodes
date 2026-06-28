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

Lose `.py`-Dateien im Root (`random_line.py`, `safe_border_crop.py` usw.) sind
eigenständige Hilfsskripte — kein Teil der Batch Suite.

## Konventionen

- [docs/conventions/python.md](docs/conventions/python.md)

## Aktiver Plan

Siehe [STATE.md](STATE.md)
