| Layer | Choice |
|---|---|
| Framework | ComfyUI Custom Nodes API |
| Lang | Python 3.11+, strict type annotations |
| Styling | — |
| State | In-memory via `batch_state.py` |
| Tests | — (kein Framework) |

# Python-Konventionen

## Typen

- Explizite Typannotationen auf **allen** Parametern und Rückgabewerten.
- `unknown` / `Any` nur wenn unvermeidbar — kommentieren warum.
- Keine `Optional[X]`-Aliase wenn `X | None` kürzer und klarer ist (Python 3.10+).

## Benennung

- Variablen und Parameter: beschreibende Substantive, nie `i`, `j`, `x`, `tmp`.
- Funktionen: Verben (`load_image`, `generate_filename`).
- Booleans: `is_` / `has_` / `can_` / `should_`-Präfix.
- Klassen: PascalCase. Module und Dateien: snake_case.

## Kontrollfluss

- Early Returns statt tief geschachtelter `if/else`-Blöcke.
- Keine leeren `__init__`-Methoden mit nur `pass`.
- Keine Doppelnegation (`not not value`) — direkt prüfen oder `bool(value)`.

## Kommentare

- Kommentare erklären das *Warum*, nicht das *Was*.
- Kein auskommentierter Code — dafür gibt es Git.
- Komplexe ComfyUI-API-Interaktionen bekommen einen erklärenden Kommentar.

## Logging

- Über `logger.py` aus `core/`, nie direkt `print()`.
- Levels: `error` für Abbruch-würdiges, `warning` für übersprungene Items,
  `info` für Batch-Start/-Ende, `debug` für Job-Details.
- Keine Tokens, Pfade mit PII oder Binärdaten ins Log.

## ComfyUI-spezifisch

- Node-Dateien enthalten nur: UI-Definition, Provider-Aufruf, Output-Mapping.
- Keine Batch-Logik, Queue-Logik oder Dateinamen-Logik in Node-Dateien.
- Provider-Klassen implementieren das Interface aus `core/interfaces.py`.
- `INPUT_TYPES` immer als `classmethod` mit vollständigen Typangaben.
