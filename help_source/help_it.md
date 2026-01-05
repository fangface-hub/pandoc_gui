---
lang: it
---

# Aiuto PandocGUI

## Panoramica

PandocGUI è un semplice strumento GUI per convertire file Markdown in HTML e altri formati utilizzando Pandoc. Può generare automaticamente diagrammi come Mermaid e PlantUML utilizzando filtri Lua.

## Funzionalità principali

- **Conversione file/cartella**: Converti singoli file o elabora in batch più file in cartelle
- **Filtri Lua**: Applica filtri come diagram.lua per generare diagrammi
- **Stili CSS**: Applica fogli di stile personalizzati (incorporati/collegamento esterno)
- **Gestione profili**: Salva e carica impostazioni utilizzate frequentemente
- **Pattern di esclusione**: Salta file specifici durante la conversione di cartelle
- **Visualizzazione log**: Monitora l'avanzamento della conversione e gli errori

## Utilizzo di base

### 1. Seleziona input

**Per convertire un file:**

1. Fai clic sul pulsante "Selezione file"
2. Scegli il file Markdown (.md) da convertire

**Per convertire una cartella in batch:**

1. Fai clic sul pulsante "Selezione cartella"
2. Scegli la cartella contenente i file Markdown
3. I file nelle sottocartelle verranno elaborati automaticamente

### 2. Imposta destinazione output

1. Fai clic sul pulsante "Selezione destinazione output"
2. Scegli la cartella per salvare i file convertiti

### 3. Configura filtri

**Aggiungi filtri predefiniti:**

1. Seleziona dal menu a discesa "Filtri predefiniti"
2. Fai clic sul pulsante "Aggiungi"

**Aggiungi filtri utente:**

1. Fai clic sul pulsante "Sfoglia" per selezionare un file `.lua`
2. Fai clic sul pulsante "Aggiungi"

**Cambia ordine filtri:**

- Seleziona un elemento nell'elenco filtri
- Usa i pulsanti "↑" "↓" per regolare l'ordine

**Rimuovi filtri:**

- Seleziona un elemento nell'elenco filtri
- Fai clic sul pulsante "Elimina"

### 4. Configura stili CSS

1. Fai clic sul pulsante "Impostazioni foglio di stile CSS"
2. Seleziona un file CSS
3. Scegli il metodo di applicazione:
   - **Incorpora**: Incorpora CSS nel file HTML
   - **Collegamento esterno**: Output come file separato e collegamento da HTML

### 5. Configura pattern di esclusione (per conversione cartelle)

Per saltare file specifici durante la conversione di cartelle:

1. Fai clic sul pulsante "Gestione pattern di esclusione"
2. Si apre la finestra dei pattern di esclusione
3. Inserisci i pattern (uno per riga)
4. Fai clic su "OK"

**Esempi di pattern:**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. Esegui conversione

1. Verifica tutte le impostazioni
2. Fai clic sul pulsante "Esegui conversione"
3. Controlla l'avanzamento nella finestra del log

## Funzione profilo

Puoi salvare combinazioni di impostazioni utilizzate frequentemente come profili.

### Crea profilo

1. Fai clic sul pulsante "Aggiungi"
2. Inserisci il nome del nuovo profilo
3. Fai clic su "OK"
4. Le impostazioni del profilo predefinito verranno copiate

### Seleziona profilo

1. Seleziona dal menu a discesa del profilo
2. Le impostazioni vengono caricate automaticamente

### Salva profilo

1. Regola le impostazioni
2. Seleziona il profilo di destinazione dal menu a discesa
3. Fai clic sul pulsante "Salva"
4. Le impostazioni correnti vengono salvate nel profilo

### Elimina profilo

1. Seleziona il profilo da eliminare dal menu a discesa
2. Fai clic sul pulsante "Elimina"
3. Fai clic su "Sì" nella finestra di dialogo di conferma

**Nota:** Il profilo predefinito non può essere eliminato.

### Aggiorna profilo

1. Fai clic sul pulsante "Carica"
2. Il profilo viene aggiornato con gli ultimi elementi di impostazione (retrocompatibilità)

I profili salvati sono memorizzati nella cartella `profiles/` in formato JSON.

## Configurazione PlantUML / Java

Quando si utilizzano diagrammi PlantUML, sono disponibili due metodi di esecuzione.

### Seleziona metodo di esecuzione PlantUML

**Metodo JAR (Esecuzione locale):**

1. Seleziona "File JAR" in "Metodo di esecuzione"
2. Specifica il percorso dell'eseguibile Java
3. Specifica il percorso del file JAR PlantUML

**Metodo server (Esecuzione online):**

1. Seleziona "Server" in "Metodo di esecuzione"
2. Specifica l'URL del server PlantUML (Predefinito: http://www.plantuml.com/plantuml)
3. Java/file JAR non richiesto

### Configurazione metodo JAR PlantUML

I percorsi vengono cercati nel seguente ordine di priorità:

#### File JAR PlantUML

1. Percorso impostazioni GUI
2. Metadati YAML `plantuml_jar` nel documento
3. Variabile d'ambiente `PLANTUML_JAR`
4. Valore predefinito `plantuml.jar`

#### Eseguibile Java

1. Percorso impostazioni GUI
2. Metadati YAML `java_path` nel documento
3. Variabile d'ambiente `JAVA_PATH`
4. Variabile d'ambiente `JAVA_HOME\bin\java`
5. `java` da PATH

### Esempi di configurazione variabili d'ambiente

**PowerShell:**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**Prompt dei comandi:**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### Specifica dei metadati YAML

Aggiungi all'inizio del file Markdown:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

**Quando si utilizza il metodo server:**

```yaml
---
plantuml_server: true
plantuml_server_url: http://www.plantuml.com/plantuml
---
```

## Funzione di aggiornamento automatico

Quando aggiorni l'applicazione, i seguenti file vengono aggiornati automaticamente:

### File di filtro

- Filtri integrati nella cartella `filters/` (diaglam.lua, md2html.lua, wikilink.lua)
- Aggiornati automaticamente all'ultima versione durante l'aggiornamento
- I filtri personalizzati sono protetti

### Impostazioni profilo

- Le nuove impostazioni aggiunte nelle nuove versioni vengono completate automaticamente
- Le impostazioni esistenti vengono preservate
- I valori predefiniti vengono recuperati da `profiles/default.json`

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### Specifica nei metadati YAML

Aggiungi all'inizio del file Markdown:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

## Risoluzione dei problemi

### Pandoc non trovato

**Sintomi:**

- Dialogo di avviso visualizzato all'avvio
- Impossibile eseguire la conversione

**Soluzione:**

1. Installa Pandoc: https://pandoc.org/installing.html
2. Dopo l'installazione, verifica che sia aggiunto a PATH
3. Esegui `pandoc --version` nel prompt dei comandi per confermare

### La conversione fallisce

**Verifica:**

- Pandoc è installato e aggiunto a PATH?
- Il file di input è in formato Markdown corretto?
- Hai il permesso di scrittura nella cartella di output?

**Controlla i log:**

- Controlla i messaggi di errore nella finestra del log GUI
- Controlla i dettagli nel file `pandoc.log`

### I diagrammi non vengono generati

**Per diagrammi Mermaid:**

- Verifica che `mmdc` (mermaid-cli) sia installato
- Esegui `mmdc --version` nel prompt dei comandi per confermare

**Per diagrammi PlantUML:**

**Metodo JAR:**
- Verifica che `plantuml.jar` esista
- Verifica che Java sia installato
- Specifica il percorso nelle impostazioni GUI, variabili d'ambiente o metadati YAML

**Metodo server:**
- Verifica la connessione Internet
- Verifica che l'URL del server sia corretto (Predefinito: http://www.plantuml.com/plantuml)
- Controlla le impostazioni del firewall

### I filtri non vengono applicati

**Verifica:**

- I filtri sono stati aggiunti correttamente? (Controlla l'elenco filtri)
- I file Lua esistono con i percorsi corretti?
- L'ordine dei filtri è appropriato? (diagram.lua potrebbe richiedere un ordine specifico)

### I pattern di esclusione non funzionano

**Verifica:**

- La sintassi del pattern è corretta? (Usa il carattere jolly `*`)
- Il pattern corrisponde ai nomi di file o cartelle?
- Hai salvato facendo clic su "OK" nella finestra dei pattern di esclusione?

## Domande frequenti

### D: In quali formati di file posso convertire?

R: Puoi convertire in tutti i formati supportati da Pandoc. I principali sono:

- HTML
- PDF (richiede LaTeX)
- DOCX (Word)
- EPUB
- Molti altri

Il formato di output può essere specificato con le opzioni Pandoc (previsto per versioni future).

### D: Posso usare più file CSS?

R: La versione attuale supporta solo un file CSS. Se hai bisogno di più stili, combina i file CSS.

### D: La struttura dei file viene preservata durante la conversione di cartelle?

R: Sì, la struttura delle sottocartelle della cartella di input viene preservata nella destinazione di output.

### D: Posso annullare la conversione?

R: Puoi terminare il processo di conversione in modo sicuro chiudendo la finestra. Il file in elaborazione sarà completato, ma i file rimanenti saranno annullati.

## File di log

I dettagli della conversione sono registrati nei seguenti file di log:

- **Posizione**: `pandoc.log` (nella stessa cartella dell'eseguibile)
- **Contenuto**: Output Pandoc, messaggi di errore, risultati dei filtri

Se si verificano problemi, controlla questo file di log.

## Appendice: Informazioni sui filtri

### Filtri predefiniti

I filtri Lua posizionati nella cartella `filters/` vengono rilevati automaticamente.

**diagram.lua:**

- Converte blocchi di codice come Mermaid, PlantUML in diagrammi

**md2html.lua:**

- Esegue elaborazioni aggiuntive in Markdown

**wikilink.lua:**

- Converte collegamenti in formato Wiki

### Aggiunta di filtri personalizzati

1. Crea un file `.lua` in qualsiasi posizione
2. Fai clic sul pulsante "Sfoglia" nella sezione "Filtri utente"
3. Seleziona il file Lua creato
4. Fai clic sul pulsante "Aggiungi"

## Informazioni di supporto

Se i problemi non vengono risolti, segnala con le seguenti informazioni:

- Versione di PandocGUI che stai utilizzando
- Versione di Pandoc (`pandoc --version`)
- Messaggi di errore (dalla finestra del log o `pandoc.log`)
- Passaggi eseguiti
- File di input di esempio (se possibile)

---

**PandocGUI** - Frontend GUI semplice per Pandoc
