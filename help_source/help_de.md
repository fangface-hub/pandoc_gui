---
lang: de
---

# PandocGUI Hilfe

## Überblick

PandocGUI ist ein einfaches GUI-Tool zur Konvertierung von Markdown-Dateien in HTML und andere Formate mit Pandoc. Es kann automatisch Diagramme wie Mermaid und PlantUML mithilfe von Lua-Filtern generieren.

## Hauptfunktionen

- **Datei-/Ordnerkonvertierung**: Einzelne Dateien konvertieren oder mehrere Dateien in Ordnern stapelweise verarbeiten
- **Lua-Filter**: Filter wie diagram.lua anwenden, um Diagramme zu generieren
- **CSS-Stile**: Benutzerdefinierte Stylesheets anwenden (eingebettet/externer Link)
- **Profilverwaltung**: Häufig verwendete Einstellungen speichern und laden
- **Ausschlussmuster**: Bestimmte Dateien bei der Ordnerkonvertierung überspringen
- **Protokollanzeige**: Konvertierungsfortschritt und Fehler überwachen

## Grundlegende Verwendung

### 1. Eingabe auswählen

**Um eine Datei zu konvertieren:**

1. Klicken Sie auf die Schaltfläche "Dateiauswahl"
2. Wählen Sie die zu konvertierende Markdown-Datei (.md)

**Um einen Ordner stapelweise zu konvertieren:**

1. Klicken Sie auf die Schaltfläche "Ordnerauswahl"
2. Wählen Sie den Ordner mit Markdown-Dateien
3. Dateien in Unterordnern werden automatisch verarbeitet

### 2. Ausgabeziel festlegen

1. Klicken Sie auf die Schaltfläche "Ausgabeziel auswählen"
2. Wählen Sie den Ordner zum Speichern konvertierter Dateien

### 3. Filter konfigurieren

**Voreingestellte Filter hinzufügen:**

1. Wählen Sie aus dem Dropdown-Menü "Voreingestellte Filter"
2. Klicken Sie auf die Schaltfläche "Hinzufügen"

**Benutzerfilter hinzufügen:**

1. Klicken Sie auf die Schaltfläche "Durchsuchen", um eine `.lua`-Datei auszuwählen
2. Klicken Sie auf die Schaltfläche "Hinzufügen"

**Filterreihenfolge ändern:**

- Wählen Sie ein Element in der Filterliste
- Verwenden Sie die Schaltflächen "↑" "↓", um die Reihenfolge anzupassen

**Filter entfernen:**

- Wählen Sie ein Element in der Filterliste
- Klicken Sie auf die Schaltfläche "Löschen"

### 4. CSS-Stile konfigurieren

1. Klicken Sie auf die Schaltfläche "CSS-Stylesheet-Einstellungen"
2. Wählen Sie eine CSS-Datei
3. Wählen Sie die Anwendungsmethode:
   - **Einbetten**: CSS in die HTML-Datei einbetten
   - **Externer Link**: Als separate Datei ausgeben und von HTML verlinken

### 5. Ausschlussmuster konfigurieren (für Ordnerkonvertierung)

Um bestimmte Dateien bei der Ordnerkonvertierung zu überspringen:

1. Klicken Sie auf die Schaltfläche "Ausschlussmuster verwalten"
2. Das Ausschlussmusterfenster öffnet sich
3. Geben Sie Muster ein (eins pro Zeile)
4. Klicken Sie auf "OK"

**Musterbeispiele:**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. Konvertierung ausführen

1. Überprüfen Sie alle Einstellungen
2. Klicken Sie auf die Schaltfläche "Konvertierung ausführen"
3. Überprüfen Sie den Fortschritt im Protokollfenster

## Profilfunktion

Sie können häufig verwendete Einstellungskombinationen als Profile speichern.

### Profil speichern

1. Passen Sie die Einstellungen an
2. Klicken Sie auf die Schaltfläche "Profil speichern"
3. Geben Sie einen Profilnamen ein
4. Klicken Sie auf "OK"

### Profil laden

1. Klicken Sie auf die Schaltfläche "Profil laden"
2. Wählen Sie ein Profil aus der Liste
3. Klicken Sie auf "OK"

Gespeicherte Profile werden im Ordner `profiles/` im JSON-Format gespeichert.

## PlantUML / Java-Konfiguration

Bei der Verwendung von PlantUML-Diagrammen werden Pfade in der folgenden Prioritätsreihenfolge gesucht:

### PlantUML JAR-Datei

1. YAML-Metadaten `plantuml_jar` im Dokument
2. Umgebungsvariable `PLANTUML_JAR`
3. Standardwert `plantuml.jar`

### Java-Executable

1. YAML-Metadaten `java_path` im Dokument
2. Umgebungsvariable `JAVA_PATH`
3. Umgebungsvariable `JAVA_HOME\bin\java`
4. `java` aus PATH

### Beispiele für Umgebungsvariablenkonfiguration

**PowerShell:**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**Eingabeaufforderung:**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### Spezifikation in YAML-Metadaten

Fügen Sie am Anfang der Markdown-Datei hinzu:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

## Fehlerbehebung

### Konvertierung schlägt fehl

**Überprüfen:**

- Ist Pandoc installiert und zu PATH hinzugefügt?
- Ist die Eingabedatei im korrekten Markdown-Format?
- Haben Sie Schreibberechtigung für den Ausgabeordner?

**Protokolle überprüfen:**

- Überprüfen Sie Fehlermeldungen im GUI-Protokollfenster
- Überprüfen Sie Details in der `pandoc.log`-Datei

### Diagramme werden nicht generiert

**Für Mermaid-Diagramme:**

- Überprüfen Sie, ob `mmdc` (mermaid-cli) installiert ist
- Führen Sie `mmdc --version` in der Eingabeaufforderung zur Bestätigung aus

**Für PlantUML-Diagramme:**

- Überprüfen Sie, ob `plantuml.jar` existiert
- Überprüfen Sie, ob Java installiert ist
- Geben Sie den Pfad in Umgebungsvariablen oder YAML-Metadaten an

### Filter werden nicht angewendet

**Überprüfen:**

- Sind Filter korrekt hinzugefügt? (Überprüfen Sie die Filterliste)
- Existieren Lua-Dateien mit korrekten Pfaden?
- Ist die Filterreihenfolge angemessen? (diagram.lua kann eine bestimmte Reihenfolge erfordern)

### Ausschlussmuster funktionieren nicht

**Überprüfen:**

- Ist die Mustersyntax korrekt? (Verwenden Sie Platzhalter `*`)
- Stimmt das Muster mit Datei- oder Ordnernamen überein?
- Haben Sie durch Klicken auf "OK" im Ausschlussmusterfenster gespeichert?

## Häufig gestellte Fragen

### F: In welche Dateiformate kann ich konvertieren?

A: Sie können in alle von Pandoc unterstützten Formate konvertieren. Hauptformate sind:

- HTML
- PDF (erfordert LaTeX)
- DOCX (Word)
- EPUB
- Viele andere

Das Ausgabeformat kann mit Pandoc-Optionen angegeben werden (geplant für zukünftige Versionen).

### F: Kann ich mehrere CSS-Dateien verwenden?

A: Die aktuelle Version unterstützt nur eine CSS-Datei. Wenn Sie mehrere Stile benötigen, kombinieren Sie bitte CSS-Dateien.

### F: Wird die Dateistruktur bei der Ordnerkonvertierung beibehalten?

A: Ja, die Unterordnerstruktur des Eingabeordners wird im Ausgabeziel beibehalten.

### F: Kann ich die Konvertierung abbrechen?

A: Sie können den Konvertierungsprozess sicher beenden, indem Sie das Fenster schließen. Die Datei in Bearbeitung wird abgeschlossen, aber die verbleibenden Dateien werden abgebrochen.

## Protokolldatei

Details zur Konvertierung werden in den folgenden Protokolldateien aufgezeichnet:

- **Speicherort**: `pandoc.log` (im selben Ordner wie die ausführbare Datei)
- **Inhalt**: Pandoc-Ausgabe, Fehlermeldungen, Filterergebnisse

Wenn Probleme auftreten, überprüfen Sie bitte diese Protokolldatei.

## Anhang: Über Filter

### Voreingestellte Filter

Lua-Filter im Ordner `filters/` werden automatisch erkannt.

**diagram.lua:**

- Konvertiert Code-Blöcke wie Mermaid, PlantUML in Diagramme

**md2html.lua:**

- Führt zusätzliche Verarbeitung innerhalb von Markdown aus

**wikilink.lua:**

- Konvertiert Wiki-formatierte Links

### Hinzufügen benutzerdefinierter Filter

1. Erstellen Sie eine `.lua`-Datei an einem beliebigen Ort
2. Klicken Sie auf die Schaltfläche "Durchsuchen" im Abschnitt "Benutzerfilter"
3. Wählen Sie die erstellte Lua-Datei aus
4. Klicken Sie auf die Schaltfläche "Hinzufügen"

## Support-Informationen

Wenn Probleme nicht gelöst werden, melden Sie dies bitte mit den folgenden Informationen:

- PandocGUI-Version, die Sie verwenden
- Pandoc-Version (`pandoc --version`)
- Fehlermeldungen (aus Protokollfenster oder `pandoc.log`)
- Ausgeführte Schritte
- Beispieleingabedatei (falls möglich)

---

**PandocGUI** - Einfaches GUI-Frontend für Pandoc  
Version 1.0
