# Pandoc GUI

[English](README.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [Français](README.fr.md) | [한국어](README.ko.md)

Una semplice interfaccia grafica per Pandoc che genera diagrammi (Mermaid, PlantUML, ecc.) utilizzando filtri Lua. Progettato per l'uso su Windows.

## Funzionalità

- Selezione di file/cartelle e impostazioni di destinazione dell'output
- Applicazione di filtri Lua (predefiniti + aggiunti dall'utente) dalla directory `filters/`
- Impostazioni di stile CSS (nella directory `stylesheets/`), scelta tra incorporamento o collegamento esterno
- Salvataggio/caricamento profili (`profiles/*.json`)
- Output del registro (GUI e `pandoc.log`)
- Esecuzione di Pandoc in background, terminazione sicura dei processi figlio all'uscita dell'app

## Requisiti

- Python 3.14+
- Pandoc (aggiunto a PATH)
- Per Mermaid: `mmdc` (mermaid-cli)
- Per PlantUML: `plantuml.jar` e Java (jdk/jre)
- (Opzionale) Filtri Lua richiesti (`filters/*.lua`)

## Come eseguire

### Sviluppo locale con uv

1. Installare uv (se non e installato):

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. Sincronizzare le dipendenze:

    ```powershell
    uv sync --group build
    ```

3. Avviare l'applicazione:

    ```powershell
    uv run python main_window.py
    ```

4. Eseguire i test:

    ```powershell
    uv run python -m unittest discover -v
    ```

5. Installare gli strumenti richiesti (Pandoc, Node/mmdc, Java, ecc.)
6. Eseguire dalla radice del repository:

    ```powershell
    uv run python main_window.py
    ```

## Specificare i percorsi PlantUML / Java

Specificare il JAR PlantUML e l'eseguibile Java utilizzando questi metodi (in ordine di priorità):

- JAR PlantUML: Metadati YAML del documento `plantuml_jar` → Variabile d'ambiente `PLANTUML_JAR` → `plantuml.jar`
- Eseguibile Java: Metadati YAML del documento `java_path` → Variabile d'ambiente `JAVA_PATH` → `JAVA_HOME\bin\java` → `java` (PATH)

Esempio di variabile d'ambiente Windows (Prompt dei comandi):

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell:

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

Esempio di specifica YAML nel documento:

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## Come utilizzare (GUI)

1. Selezionare l'input con "Selezione file" o "Selezione cartella"
2. Selezionare la directory di output con "Selezione destinazione output"
3. Aggiungere filtri predefiniti/utente (regolare l'ordine con i pulsanti su/giù)
4. (Opzionale) Configurare i modelli di esclusione per saltare file specifici durante la conversione della cartella
5. Fare clic su "Esegui conversione"

### Impostazioni modello di esclusione

Durante la conversione batch delle cartelle, è possibile escludere file o cartelle specifici:

- Fare clic su "Gestione modelli di esclusione" per aprire le impostazioni
- Modelli con caratteri jolly supportati (ad es. `*.tmp`, `__pycache__`, `.git`)
- Più modelli supportati (uno per riga)

Esempi di corrispondenza modelli:

- `*.tmp` - Escludere tutti i file .tmp
- `__pycache__` - Escludere le cartelle __pycache__ e i contenuti
- `.git` - Escludere le cartelle .git
- `test_*` - Escludere i file che iniziano con test_
- `*_backup` - Escludere i file che terminano con _backup

## Registri e profili

- La GUI visualizza i registri e il sistema registra i dettagli in `pandoc.log`
- Il sistema salva i profili come JSON nella directory `profiles/`

## Creazione di pacchetti di distribuzione

### Creare una distribuzione di cartelle con Nuitka

1. Installare Nuitka:

    ```powershell
    uv tool install nuitka
    ```

2. Creare l'eseguibile:

    __Nota__: `main_window.py` è incluso nel repository con l'elaborazione post-build configurata per posizionare `filters/` e `locales/` all'esterno di `main_window.dist/`.

    ```powershell
    uv run python -m nuitka --standalone --output-dir=dist --output-filename=PandocGUI --include-data-dir=filters=filters --include-data-dir=locales=locales --include-data-dir=stylesheets=stylesheets --include-data-dir=help=help --include-data-dir=profiles=profiles --include-data-dir=mermaid=mermaid --include-data-dir=LICENSES=LICENSES main_window.py
    ```

    Solo se è necessario rigenerare il file `Nuitka` (normalmente non richiesto):

    ```powershell
    uv run python -m nuitka --standalone --clang --msvc=latest --windows-console-mode=disable --output-dir=dist --output-filename=PandocGUI.exe --include-data-dir=filters=filters --include-data-dir=locales=locales --include-data-dir=stylesheets=stylesheets --include-data-dir=help=help --include-data-dir=profiles=profiles --include-data-dir=mermaid=mermaid --include-data-dir=LICENSES=LICENSES main_window.py
    ```

    __Importante__: È necessario aggiungere manualmente l'elaborazione post-build al file `Nuitka` generato dal comando sopra.

3. L'output della build si trova in `dist/main_window.dist/`:

    ```text
    dist/main_window.dist/
    ├── PandocGUI.exe        # Eseguibile
    ├── filters/             # Filtri Lua
    ├── locales/             # File di traduzione
    ├── stylesheets/         # Fogli di stile CSS
    ├── help/                # File di aiuto (HTML)
    ├── profiles/            # Profili (creati in fase di esecuzione)
    └── *.dll / *.pyd ...  # Runtime dependencies
    ```

    L'elaborazione post-build nel file `Nuitka` posiziona `filters/`, `locales/` e `stylesheets/` all'esterno di `main_window.dist/`

### Aggiornare il numero di versione

Usare questi script nella root del repository:

- `./bump_patch.ps1`: `X.Y.Z` -> `X.Y.(Z+1)`
- `./bump_minor.ps1`: `X.Y.Z` -> `X.(Y+1).0`
- `./bump_major.ps1`: `X.Y.Z` -> `(X+1).0.0`

Quando si incrementa una versione superiore, le versioni inferiori vengono azzerate.
Tutti gli script aggiornano contemporaneamente questi file:

- `pyproject.toml`
- `__version__.py`
- `AppxManifest.xml`

### Creare un programma di installazione Windows con MSIX Packaging Tool

1. Installare MSIX Packaging Tool:

   - Installare "MSIX Packaging Tool" dal Microsoft Store

2. Avviare MSIX Packaging Tool e selezionare "Application package"

3. Selezionare "Create package on this computer"

4. Inserire le informazioni del pacchetto:

    - Package name: `PandocGUI`
    - Publisher: `CN=YourName` (Modificare in base al certificato)
    - Version: `1.0.0.0`

5. Selezionare il programma di installazione:

    - Fare clic su "Browse" e selezionare `dist/main_window.dist/PandocGUI.exe`
    - Installation location: `C:\Program Files\PandocGUI`

6. Eseguire l'installazione e acquisire:

   - Avviare l'app e verificare il funzionamento
   - Verificare che tutti i file richiesti siano inclusi
   - Fare clic su "Done"

7. Salvare il pacchetto:

    - Salvare come file .msix

8. Firma (opzionale):

    - Creare un certificato di test o utilizzare un certificato esistente

    ```powershell
    # Creare un certificato di test
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # Firmare il file MSIX
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. Distribuire il programma di installazione:

   - Distribuire il file .msix
   - Gli utenti installano il certificato prima di installare l'app

### Note

- Verificare che i file di risorse come `filters/` e `locales/` siano correttamente inclusi
- Strumenti esterni come Pandoc, mmdc e Java devono essere installati separatamente
- I pacchetti MSIX richiedono la firma (i certificati di test possono essere utilizzati durante lo sviluppo)

## Test

Forniamo test unitari. Eseguirli con i seguenti comandi:

### Eseguire tutti i test

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### Eseguire singoli file di test

```powershell
python -m unittest test_<name>.py
```

Esempio:

```powershell
python -m unittest test_main_window.py
```

### Output di test dettagliato

```powershell
python -m unittest discover -v
```

File di test:

- `test_main_window.py` - Finestra principale e funzionalità di gestione del profilo
- `test_css_window.py` - Funzionalità delle impostazioni CSS
- `test_filter_window.py` - Funzionalità di gestione dei filtri
- `test_log_window.py` - Funzionalità di visualizzazione del registro

## Risoluzione dei problemi

- Se il sistema non riesce a trovare PlantUML o non può eseguire Java, verrà visualizzato un messaggio in stderr. Specificare il percorso utilizzando variabili d'ambiente o metadati YAML.
- Il sistema visualizza gli errori di Pandoc nel registro GUI e in `pandoc.log`.

## Note di sviluppo

- Posizioniamo i filtri Lua nella directory `filters/` (ad es. `filters/diagram.lua`).
- Posizioniamo i file CSS nella directory `stylesheets/`. È possibile selezionarli dalla GUI e applicarli come incorporati o collegamenti esterni.
- Il sistema esegue la conversione in un thread in background e termina/uccide i processi figlio all'uscita dell'app.

[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Sostieni%20il%20progetto-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/fangface-hub)
