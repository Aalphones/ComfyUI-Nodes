# ComfyUI Batch Suite -- Architektur & Implementierungsspezifikation

> Ziel: Eine wiederverwendbare Batch-Infrastruktur für ComfyUI. Dieses
> Dokument beschreibt die gemeinsame technische Basis sowie die erste
> Implementierung der Nodes **Image Batch Loader** und **Prompt Batch
> Loader**.

------------------------------------------------------------------------

# Projektziele

-   Eine gemeinsame Batch Engine für alle zukünftigen Batch-Nodes.
-   Keine doppelte Implementierung von Queue-, Fortschritts- oder
    Dateinamenlogik.
-   Einzelbildverarbeitung (konstanter VRAM).
-   Ein Klick auf **Queue Prompt** startet den gesamten Batch.
-   Jede neue Batch-Node implementiert nur ihre Datenquelle.

------------------------------------------------------------------------

# Architektur

``` text
batch_suite/
├── core/
│   ├── batch_engine.py
│   ├── queue_manager.py
│   ├── batch_state.py
│   ├── filename_generator.py
│   ├── progress.py
│   ├── logger.py
│   ├── error_handler.py
│   ├── interfaces.py
│   └── utils.py
│
├── providers/
│   ├── image_provider.py
│   └── prompt_provider.py
│
├── nodes/
│   ├── image_batch_loader.py
│   └── prompt_batch_loader.py
│
├── web/
│   ├── shared.js
│   ├── image_batch_loader.js
│   └── prompt_batch_loader.js
│
└── __init__.py
```

------------------------------------------------------------------------

# Batch Engine

Verantwortlich für:

-   Batch starten
-   Jobs verwalten
-   nächsten Job bereitstellen
-   Queue automatisch erneut starten
-   Fortschritt
-   Logging
-   Fehlerbehandlung
-   Speicherbereinigung

Alle Nodes verwenden ausschließlich diese Engine.

------------------------------------------------------------------------

# BatchJob

Jeder Job besitzt:

``` python
BatchJob(
    id,
    index,
    total,
    payload,
    metadata,
    save_filename,
)
```

------------------------------------------------------------------------

# Dateinamengenerator

Gemeinsame Implementierung.

Konfiguration:

-   Prefix (frei wählbar)
-   Datumsformat
-   Startindex
-   Stellenanzahl

Format:

``` text
{prefix}-{date}-{index}
```

Beispiel:

``` text
Output-20260628-001
Output-20260628-002
Output-20260628-003
```

Das Datum wird genau einmal beim Start eines Batch-Laufs erzeugt.

------------------------------------------------------------------------

# Queue Manager

Der Benutzer klickt genau einmal auf **Queue Prompt**.

Danach übernimmt die Batch Engine sämtliche Wiederholungen bis alle Jobs
verarbeitet wurden.

------------------------------------------------------------------------

# Gemeinsame Outputs

Alle Loader liefern:

-   CURRENT_INDEX
-   TOTAL_ITEMS
-   SAVE_FILENAME

------------------------------------------------------------------------

# Node: Image Batch Loader

## Ziel

Universeller Ersatz für die Standard-Load-Image-Node.

Die Node muss sowohl Einzelbilder als auch Batch-Verarbeitung
unterstützen.

## Unterstützte Betriebsarten

### 1. Einzelbild (UI)

Ein Bild auswählen.

Die Node verhält sich identisch zur Standard-Load-Image-Node.

Kein Batch wird gestartet.

### 2. Multi-Select (UI)

Mehrere Bilder im Explorer markieren und per Drag & Drop auf die Node
ziehen.

Die Node erzeugt intern eine Jobliste und startet automatisch die Batch
Engine.

### 3. API (Einzelbild)

Der API-Aufruf übergibt genau einen Bildpfad.

Intern wird automatisch genau ein BatchJob erzeugt.

Das Verhalten entspricht der Standard-Load-Image-Node.

### 4. API (Mehrere Bilder)

Der API-Aufruf übergibt eine Liste von Bildpfaden.

Für jedes Bild wird ein BatchJob erzeugt.

Die Batch Engine verarbeitet alle Jobs nacheinander.

## Unterstützte Eingabequellen

-   Drag & Drop
-   File Picker
-   API (ein Bild)
-   API (Liste von Bildern)

Alle vier Wege verwenden dieselbe interne Provider-Logik.

## Unterstützte Formate

-   png
-   jpg
-   jpeg
-   webp
-   bmp
-   tif
-   tiff

## Outputs

-   IMAGE
-   MASK
-   SAVE_FILENAME
-   CURRENT_INDEX
-   TOTAL_ITEMS
-   ORIGINAL_FILENAME
-   ORIGINAL_FILENAME_NO_EXT
-   FILE_EXTENSION

## Einstellungen

-   Prefix
-   Digits
-   Start Index
-   Date Format
-   Stop on Error
-   Skip Failed Images

------------------------------------------------------------------------

# Node: Prompt Batch Loader

## Ziel

Alle Prompt-Dateien eines Ordners nacheinander verarbeiten.

## Eingabe

-   Ordner auswählen
-   Optional rekursiv durchsuchen

Nur UTF-8 `.txt`-Dateien.

## Verhalten

Jede Datei repräsentiert genau einen Prompt.

Alle übrigen Workflowparameter bleiben unverändert.

## Outputs

-   STRING
-   SAVE_FILENAME
-   CURRENT_INDEX
-   TOTAL_ITEMS
-   PROMPT_FILENAME
-   PROMPT_FILENAME_NO_EXT
-   PROMPT_RELATIVE_PATH

## Einstellungen

-   Prefix
-   Digits
-   Start Index
-   Date Format
-   Recursive
-   Skip Empty Files
-   Stop on Error

------------------------------------------------------------------------

# Frontend

Gemeinsame JavaScript-Basis:

-   Fortschrittsanzeige
-   Statusanzeige
-   Drag & Drop
-   File Picker
-   Folder Picker

------------------------------------------------------------------------

# Backend

Node-Dateien enthalten ausschließlich:

-   UI
-   Provider
-   Output-Mapping

Keine Batchlogik.

Keine Queueverwaltung.

Keine Dateinamenlogik.

------------------------------------------------------------------------

# Akzeptanztests

## Image Batch Loader

-   Einzelbild verhält sich identisch zur Standard-Node.
-   API mit einem Bild funktioniert identisch.
-   API mit Bildliste startet Batch.
-   Multi-Drag-&-Drop funktioniert.
-   1000 Bilder werden vollständig verarbeitet.
-   VRAM bleibt konstant.

## Prompt Batch Loader

-   1000 Prompt-Dateien funktionieren.
-   Rekursion funktioniert.
-   UTF-8 bleibt unverändert.
-   Leere Dateien können übersprungen werden.

## Gemeinsam

-   Ein Klick auf Queue Prompt genügt.
-   SAVE_FILENAME wird korrekt erzeugt.
-   Batch über Mitternacht behält denselben Datumsstempel.
-   Speicher wird vollständig freigegeben.
-   Batch kann sauber beendet werden.

------------------------------------------------------------------------

# Qualitätsanforderungen

-   Python \>= 3.11
-   Typannotationen
-   Dokumentierter Code
-   Plattformunabhängig
-   Keine doppelte Batchlogik
-   Erweiterbar für weitere Provider

------------------------------------------------------------------------

# Implementierungsstrategie

1.  Batch Engine implementieren.
2.  Queue Manager implementieren.
3.  Filename Generator implementieren.
4.  Gemeinsame JavaScript-Basis implementieren.
5.  Image Batch Loader als Adapter implementieren.
6.  Prompt Batch Loader als Adapter implementieren.

Alle zukünftigen Batch-Nodes sollen ausschließlich neue Provider
bereitstellen und die bestehende Infrastruktur wiederverwenden.
