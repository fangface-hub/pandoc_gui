# Pandoc GUI

[English](README.md) | [日本語](README.ja.md) | [中文](README.zh.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [한국어](README.ko.md)

Ein einfaches GUI-Frontend für Pandoc, das Diagramme (Mermaid, PlantUML usw.) mithilfe von Lua-Filtern generiert. Entwickelt für die Verwendung unter Windows.

## Funktionen

- Datei-/Ordnerauswahl und Ausgabezieleinstellungen
- Anwendung von Lua-Filtern (Voreinstellung + Benutzer hinzugefügt) aus dem Verzeichnis `filters/`
- CSS-Stileinstellungen (im Verzeichnis `stylesheets/`), Auswahl zwischen Einbettung oder externem Link
- Profile speichern/laden (`profiles/*.json`)
- Protokollausgabe (GUI und `pandoc.log`)
- Pandoc im Hintergrund ausführen, untergeordnete Prozesse beim Beenden der App sicher beenden

## Anforderungen

- Python 3.14+
- Pandoc (zu PATH hinzufügen)
- Für Mermaid: `mmdc` (mermaid-cli)
- Für PlantUML: `plantuml.jar` und Java (jdk/jre)
- (Optional) Erforderliche Lua-Filter (`filters/*.lua`)

## Ausführen

### Lokale Entwicklung mit uv

1. uv installieren (falls noch nicht installiert):

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. Abhängigkeiten synchronisieren:

    ```powershell
    uv sync --group build
    ```

3. Anwendung starten:

    ```powershell
    uv run python main_window.py
    ```

4. Tests ausführen:

    ```powershell
    uv run python -m unittest discover -v
    ```

5. Erforderliche Tools installieren (Pandoc, Node/mmdc, Java usw.)
6. Vom Repository-Root ausführen:

    ```powershell
    uv run python main_window.py
    ```

## PlantUML / Java-Pfade angeben

Geben Sie die PlantUML JAR und die Java-Ausführungsdatei mit diesen Methoden an (in Prioritätsreihenfolge):

- PlantUML JAR: Dokument-YAML-Metadaten `plantuml_jar` → Umgebungsvariable `PLANTUML_JAR` → `plantuml.jar`
- Java-Ausführungsdatei: Dokument-YAML-Metadaten `java_path` → Umgebungsvariable `JAVA_PATH` → `JAVA_HOME\bin\java` → `java` (PATH)

Beispiel für Windows-Umgebungsvariable (Eingabeaufforderung):

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell:

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

Beispiel für YAML-Spezifikation im Dokument:

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## Verwendung (GUI)

1. Eingabe mit "Dateiauswahl" oder "Ordnerauswahl" auswählen
2. Ausgabeverzeichnis mit "Ausgabezielauswahl" auswählen
3. Voreingestellte/Benutzerfilter hinzufügen (Reihenfolge mit Auf-/Ab-Tasten anpassen)
4. (Optional) Ausschlussmuster konfigurieren, um bestimmte Dateien während der Ordnerkonvertierung zu überspringen
5. Auf "Konvertierung ausführen" klicken

### Ausschlussmuster-Einstellungen

Beim Stapelkonvertieren von Ordnern können Sie bestimmte Dateien oder Ordner ausschließen:

- Klicken Sie auf "Ausschlussmusterverwaltung", um die Einstellungen zu öffnen
- Wildcard-Muster werden unterstützt (z.B. `*.tmp`, `__pycache__`, `.git`)
- Mehrere Muster werden unterstützt (eines pro Zeile)

Beispiele für Musterabgleich:

- `*.tmp` - Alle .tmp-Dateien ausschließen
- `__pycache__` - __pycache__-Ordner und Inhalte ausschließen
- `.git` - .git-Ordner ausschließen
- `test_*` - Dateien ausschließen, die mit test_ beginnen
- `*_backup` - Dateien ausschließen, die mit _backup enden

## Protokolle & Profile

- Die GUI zeigt Protokolle an, und das System zeichnet Details in `pandoc.log` auf
- Das System speichert Profile als JSON im Verzeichnis `profiles/`

## Verteilungspakete erstellen

### Ordnerverteilung mit Nuitka erstellen

1. Nuitka installieren:

    ```powershell
    uv tool install nuitka
    ```

2. Ausführbare Datei erstellen:

    __Hinweis__: `main_window.py` ist im Repository enthalten und die Nachbearbeitung ist so konfiguriert, dass `filters/` und `locales/` außerhalb von `main_window.dist/` platziert werden.

    ```powershell
    uv run python -m nuitka --standalone --output-dir=dist --output-filename=PandocGUI --include-data-dir=filters=filters --include-data-dir=locales=locales --include-data-dir=stylesheets=stylesheets --include-data-dir=help=help --include-data-dir=profiles=profiles --include-data-dir=mermaid=mermaid --include-data-dir=LICENSES=LICENSES main_window.py
    ```

    Nur wenn Sie die `Nuitka`-Datei neu generieren müssen (normalerweise nicht erforderlich):

    ```powershell
    uv run python -m nuitka --standalone --clang --msvc=latest --windows-console-mode=disable --output-dir=dist --output-filename=PandocGUI.exe --include-data-dir=filters=filters --include-data-dir=locales=locales --include-data-dir=stylesheets=stylesheets --include-data-dir=help=help --include-data-dir=profiles=profiles --include-data-dir=mermaid=mermaid --include-data-dir=LICENSES=LICENSES main_window.py
    ```

    __Wichtig__: Sie müssen die Nachbearbeitung manuell zur `Nuitka`-Datei hinzufügen, die mit dem obigen Befehl generiert wurde.

3. Build-Ausgabe ist in `dist/main_window.dist/`:

    ```text
    dist/main_window.dist/
    ├── PandocGUI.exe        # Ausführbare Datei
    ├── filters/             # Lua-Filter
    ├── locales/             # Übersetzungsdateien
    ├── stylesheets/         # CSS-Stylesheets
    ├── help/                # Hilfedateien (HTML)
    ├── profiles/            # Profile (zur Laufzeit erstellt)
    └── *.dll / *.pyd ...  # Runtime dependencies
    ```

    Die Nachbearbeitung in der `Nuitka`-Datei platziert `filters/`, `locales/` und `stylesheets/` außerhalb von `main_window.dist/`

### Versionsnummer erhöhen

Verwenden Sie diese Skripte im Repository-Stammverzeichnis:

- `./bump_patch.ps1`: `X.Y.Z` -> `X.Y.(Z+1)`
- `./bump_minor.ps1`: `X.Y.Z` -> `X.(Y+1).0`
- `./bump_major.ps1`: `X.Y.Z` -> `(X+1).0.0`

Wenn eine höhere Version erhöht wird, werden die niedrigeren Versionen auf 0 zurückgesetzt.
Alle Skripte aktualisieren diese Dateien gleichzeitig:

- `pyproject.toml`
- `__version__.py`
- `AppxManifest.xml`

### Windows-Installer mit MSIX Packaging Tool erstellen

1. MSIX Packaging Tool installieren:

   - "MSIX Packaging Tool" aus dem Microsoft Store installieren

2. MSIX Packaging Tool starten und "Application package" auswählen

3. "Create package on this computer" auswählen

4. Paketinformationen eingeben:

    - Package name: `PandocGUI`
    - Publisher: `CN=YourName` (Entsprechend dem Zertifikat ändern)
    - Version: `1.0.0.0`

5. Installer auswählen:

    - Auf "Browse" klicken und `dist/main_window.dist/PandocGUI.exe` auswählen
    - Installation location: `C:\Program Files\PandocGUI`

6. Installation ausführen und erfassen:

   - App starten und Betrieb überprüfen
   - Überprüfen, ob alle erforderlichen Dateien enthalten sind
   - Auf "Done" klicken

7. Paket speichern:

    - Als .msix-Datei speichern

8. Signierung (optional):

    - Testzertifikat erstellen oder vorhandenes Zertifikat verwenden

    ```powershell
    # Testzertifikat erstellen
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # MSIX-Datei signieren
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. Installer verteilen:

   - .msix-Datei verteilen
   - Benutzer installieren das Zertifikat, bevor sie die App installieren

### Hinweise

- Überprüfen Sie, ob Ressourcendateien wie `filters/` und `locales/` ordnungsgemäß enthalten sind
- Externe Tools wie Pandoc, mmdc und Java müssen separat installiert werden
- MSIX-Pakete erfordern eine Signierung (Testzertifikate können während der Entwicklung verwendet werden)

## Testen

Wir stellen Unit-Tests bereit. Führen Sie sie mit den folgenden Befehlen aus:

### Alle Tests ausführen

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### Einzelne Testdateien ausführen

```powershell
python -m unittest test_<name>.py
```

Beispiel:

```powershell
python -m unittest test_main_window.py
```

### Ausführliche Testausgabe

```powershell
python -m unittest discover -v
```

Testdateien:

- `test_main_window.py` - Hauptfenster- und Profilverwaltungsfunktionen
- `test_css_window.py` - CSS-Einstellungsfunktionen
- `test_filter_window.py` - Filterverwaltungsfunktionen
- `test_log_window.py` - Protokollanzeigefunktionen

## Fehlerbehebung

- Wenn das System PlantUML nicht finden oder Java nicht ausführen kann, wird eine Meldung in stderr angezeigt. Geben Sie den Pfad mit Umgebungsvariablen oder YAML-Metadaten an.
- Das System zeigt Pandoc-Fehler im GUI-Protokoll und in `pandoc.log` an.

## Entwicklungshinweise

- Wir platzieren Lua-Filter im Verzeichnis `filters/` (z.B. `filters/diagram.lua`).
- Wir platzieren CSS-Dateien im Verzeichnis `stylesheets/`. Sie können sie über die GUI auswählen und als eingebettet oder als externe Links anwenden.
- Das System führt die Konvertierung in einem Hintergrund-Thread aus und beendet/killt untergeordnete Prozesse beim Beenden der App.

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Projekt%20unterst%C3%BCtzen-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/fangface-hub)
