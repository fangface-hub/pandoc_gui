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

- Python 3.8+
- Pandoc (aggiunto a PATH)
- Per Mermaid: `mmdc` (mermaid-cli)
- Per PlantUML: `plantuml.jar` e Java (jdk/jre)
- (Opzionale) Filtri Lua richiesti (`filters/*.lua`)

## Come eseguire

1. Installare gli strumenti richiesti (Pandoc, Node/mmdc, Java, ecc.)
2. Eseguire dalla radice del repository:

    ```powershell
    python main_window.py
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

### Creare una distribuzione di cartelle con PyInstaller

1. Installare PyInstaller:

    ```powershell
    pip install pyinstaller
    ```

2. Creare l'eseguibile:

    __Nota__: `PandocGUI.spec` è incluso nel repository con l'elaborazione post-build configurata per posizionare `filters/` e `locales/` all'esterno di `_internal/`.

    ```powershell
    python -m PyInstaller PandocGUI.spec
    ```

    Solo se è necessario rigenerare il file `.spec` (normalmente non richiesto):

    ```powershell
    pyinstaller --noconsole --onedir --name "PandocGUI" `
      --add-data "locales;locales" `
      --add-data "filters;filters" `
      --add-data "stylesheets;stylesheets" `
      main_window.py
    ```

    __Importante__: È necessario aggiungere manualmente l'elaborazione post-build al file `.spec` generato dal comando sopra.

3. L'output della build si trova in `dist/PandocGUI/`:

    ```text
    dist/PandocGUI/
    ├── PandocGUI.exe        # Eseguibile
    ├── filters/             # Filtri Lua
    ├── locales/             # File di traduzione
    ├── stylesheets/         # Fogli di stile CSS
    ├── help/                # File di aiuto (HTML)
    ├── profiles/            # Profili (creati in fase di esecuzione)
    └── _internal/           # Dipendenze Python
    ```

    L'elaborazione post-build nel file `.spec` posiziona `filters/`, `locales/` e `stylesheets/` all'esterno di `_internal/`

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

    - Fare clic su "Browse" e selezionare `dist/PandocGUI/PandocGUI.exe`
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
