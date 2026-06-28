# ComfyUI Batch Suite — Projekt-Kontext

## Ziel

Eine gemeinsame Batch-Infrastruktur für ComfyUI. Alle Batch-Nodes teilen
eine zentrale Engine — Queue, Fortschritt, Dateiname. Jede neue Node
implementiert nur ihre eigene Datenquelle.

Erste Implementierung: **Image Batch Loader** und **Prompt Batch Loader**.

## Kernprinzipien

- Ein Klick auf *Queue Prompt* startet den gesamten Batch.
- Einzelbildverarbeitung → konstanter VRAM.
- Keine doppelte Batch-Logik in Node-Dateien.
- Erweiterbar: neue Nodes = neuer Provider, fertig.

## Architektur

```
batch_suite/
├── core/
│   ├── batch_engine.py       # Koordiniert alle Jobs
│   ├── queue_manager.py      # Startet Queue automatisch neu
│   ├── batch_state.py        # Laufzustand eines Batch-Laufs
│   ├── filename_generator.py # {prefix}-{date}-{index}
│   ├── progress.py           # Fortschritts-Callbacks
│   ├── logger.py
│   ├── error_handler.py
│   ├── interfaces.py         # Abstrakte Provider-Schnittstelle
│   └── utils.py
├── providers/
│   ├── image_provider.py
│   └── prompt_provider.py
├── nodes/
│   ├── image_batch_loader.py
│   └── prompt_batch_loader.py
├── web/
│   ├── shared.js             # Fortschritt, Status, Drag & Drop, Picker
│   ├── image_batch_loader.js
│   └── prompt_batch_loader.js
└── __init__.py
```

## BatchJob

Jeder verarbeitete Eintrag trägt: `id`, `index`, `total`, `payload`,
`metadata`, `save_filename`.

## Dateinamengenerator

Format: `{prefix}-{date}-{index}` (Beispiel: `Output-20260628-001`).
Das Datum wird einmal beim Batch-Start erzeugt — bleibt über Mitternacht stabil.

Konfigurierbar: Prefix, Datumsformat, Startindex, Stellenanzahl.

## Node: Image Batch Loader

Universeller Ersatz für die Standard-*Load Image*-Node.

**Betriebsarten:** Einzelbild (UI), Multi-Select per Drag & Drop (UI),
API-Einzelbild, API-Bildliste.

**Unterstützte Formate:** png, jpg, jpeg, webp, bmp, tif, tiff.

**Outputs:** IMAGE, MASK, SAVE_FILENAME, CURRENT_INDEX, TOTAL_ITEMS,
ORIGINAL_FILENAME, ORIGINAL_FILENAME_NO_EXT, FILE_EXTENSION.

**Einstellungen:** Prefix, Digits, Start Index, Date Format, Stop on Error,
Skip Failed Images.

## Node: Prompt Batch Loader

Verarbeitet alle UTF-8-`.txt`-Dateien eines Ordners nacheinander.
Optional rekursiv.

**Outputs:** STRING, SAVE_FILENAME, CURRENT_INDEX, TOTAL_ITEMS,
PROMPT_FILENAME, PROMPT_FILENAME_NO_EXT, PROMPT_RELATIVE_PATH.

**Einstellungen:** Prefix, Digits, Start Index, Date Format, Recursive,
Skip Empty Files, Stop on Error.

## Frontend (JS)

Gemeinsame Basis `shared.js`: Fortschrittsanzeige, Statusanzeige,
Drag & Drop, File Picker, Folder Picker. Node-spezifische JS-Dateien
enthalten nur node-eigene Anpassungen.

## Implementierungsreihenfolge

1. Batch Engine
2. Queue Manager
3. Filename Generator
4. JS-Basis (`shared.js`)
5. Image Batch Loader (Adapter)
6. Prompt Batch Loader (Adapter)

## Qualitätsanforderungen

- Python >= 3.11
- Typannotationen auf allen Funktionen und Parametern
- Plattformunabhängig
- Keine doppelte Batch-Logik
