# Pandoc GUI

[English](README.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [Italiano](README.it.md) | [한국어](README.ko.md)

Une interface graphique simple pour Pandoc qui génère des diagrammes (Mermaid, PlantUML, etc.) à l'aide de filtres Lua. Conçu pour une utilisation sous Windows.

## Fonctionnalités

- Sélection de fichiers/dossiers et paramètres de destination de sortie
- Application de filtres Lua (préréglages + ajoutés par l'utilisateur) depuis le répertoire `filters/`
- Paramètres de style CSS (dans le répertoire `stylesheets/`), choix entre incorporation ou lien externe
- Sauvegarde/chargement de profils (`profiles/*.json`)
- Sortie de journal (GUI et `pandoc.log`)
- Exécution de Pandoc en arrière-plan, arrêt sécurisé des processus enfants à la fermeture de l'application

## Exigences

- Python 3.8+
- Pandoc (ajouté au PATH)
- Pour Mermaid : `mmdc` (mermaid-cli)
- Pour PlantUML : `plantuml.jar` et Java (jdk/jre)
- (Optionnel) Filtres Lua requis (`filters/*.lua`)

## Comment exécuter

1. Installer les outils requis (Pandoc, Node/mmdc, Java, etc.)
2. Exécuter depuis la racine du dépôt :

    ```powershell
    python main_window.py
    ```

## Spécifier les chemins PlantUML / Java

Spécifiez le JAR PlantUML et l'exécutable Java en utilisant ces méthodes (par ordre de priorité) :

- JAR PlantUML : Métadonnées YAML du document `plantuml_jar` → Variable d'environnement `PLANTUML_JAR` → `plantuml.jar`
- Exécutable Java : Métadonnées YAML du document `java_path` → Variable d'environnement `JAVA_PATH` → `JAVA_HOME\bin\java` → `java` (PATH)

Exemple de variable d'environnement Windows (Invite de commandes) :

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell :

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

Exemple de spécification YAML dans le document :

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## Comment utiliser (GUI)

1. Sélectionner l'entrée avec "Sélection de fichier" ou "Sélection de dossier"
2. Sélectionner le répertoire de sortie avec "Sélection de destination de sortie"
3. Ajouter des filtres prédéfinis/utilisateur (ajuster l'ordre avec les boutons haut/bas)
4. (Optionnel) Configurer les modèles d'exclusion pour ignorer des fichiers spécifiques pendant la conversion de dossier
5. Cliquer sur "Exécuter la conversion"

### Paramètres de modèle d'exclusion

Lors de la conversion par lots de dossiers, vous pouvez exclure des fichiers ou dossiers spécifiques :

- Cliquer sur "Gestion des modèles d'exclusion" pour ouvrir les paramètres
- Modèles génériques pris en charge (par ex. `*.tmp`, `__pycache__`, `.git`)
- Plusieurs modèles pris en charge (un par ligne)

Exemples de correspondance de modèles :

- `*.tmp` - Exclure tous les fichiers .tmp
- `__pycache__` - Exclure les dossiers __pycache__ et leur contenu
- `.git` - Exclure les dossiers .git
- `test_*` - Exclure les fichiers commençant par test_
- `*_backup` - Exclure les fichiers se terminant par _backup

## Journaux et profils

- L'interface graphique affiche les journaux, et le système enregistre les détails dans `pandoc.log`
- Le système enregistre les profils au format JSON dans le répertoire `profiles/`

## Création de packages de distribution

### Créer une distribution de dossier avec PyInstaller

1. Installer PyInstaller :

    ```powershell
    pip install pyinstaller
    ```

2. Créer l'exécutable :

    __Note__ : `PandocGUI.spec` est inclus dans le dépôt avec un traitement post-construction configuré pour placer `filters/` et `locales/` en dehors de `_internal/`.

    ```powershell
    python -m PyInstaller PandocGUI.spec
    ```

    Seulement si vous devez régénérer le fichier `.spec` (normalement pas nécessaire) :

    ```powershell
    pyinstaller --noconsole --onedir --name "PandocGUI" `
      --add-data "locales;locales" `
      --add-data "filters;filters" `
      --add-data "stylesheets;stylesheets" `
      main_window.py
    ```

    __Important__ : Vous devez ajouter manuellement le traitement post-construction au fichier `.spec` généré par la commande ci-dessus.

3. La sortie de construction se trouve dans `dist/PandocGUI/` :

    ```text
    dist/PandocGUI/
    ├── PandocGUI.exe        # Exécutable
    ├── filters/             # Filtres Lua
    ├── locales/             # Fichiers de traduction
    ├── stylesheets/         # Feuilles de style CSS
    ├── help/                # Fichiers d'aide (HTML)
    ├── profiles/            # Profils (créés à l'exécution)
    └── _internal/           # Dépendances Python
    ```

    Le traitement post-construction dans le fichier `.spec` place `filters/`, `locales/` et `stylesheets/` en dehors de `_internal/`

### Créer un installateur Windows avec MSIX Packaging Tool

1. Installer MSIX Packaging Tool :

   - Installer "MSIX Packaging Tool" depuis le Microsoft Store

2. Lancer MSIX Packaging Tool et sélectionner "Application package"

3. Sélectionner "Create package on this computer"

4. Entrer les informations du package :

    - Package name : `PandocGUI`
    - Publisher : `CN=YourName` (Modifier selon le certificat)
    - Version : `1.0.0.0`

5. Sélectionner l'installateur :

    - Cliquer sur "Browse" et sélectionner `dist/PandocGUI/PandocGUI.exe`
    - Installation location : `C:\Program Files\PandocGUI`

6. Exécuter l'installation et capturer :

   - Lancer l'application et vérifier le fonctionnement
   - Vérifier que tous les fichiers requis sont inclus
   - Cliquer sur "Done"

7. Enregistrer le package :

    - Enregistrer en tant que fichier .msix

8. Signature (optionnel) :

    - Créer un certificat de test ou utiliser un certificat existant

    ```powershell
    # Créer un certificat de test
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # Signer le fichier MSIX
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. Distribuer l'installateur :

   - Distribuer le fichier .msix
   - Les utilisateurs installent le certificat avant d'installer l'application

### Notes

- Vérifier que les fichiers de ressources comme `filters/` et `locales/` sont correctement inclus
- Les outils externes comme Pandoc, mmdc et Java doivent être installés séparément
- Les packages MSIX nécessitent une signature (les certificats de test peuvent être utilisés pendant le développement)

## Tests

Nous fournissons des tests unitaires. Exécutez-les avec les commandes suivantes :

### Exécuter tous les tests

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### Exécuter des fichiers de test individuels

```powershell
python -m unittest test_<name>.py
```

Exemple :

```powershell
python -m unittest test_main_window.py
```

### Sortie de test détaillée

```powershell
python -m unittest discover -v
```

Fichiers de test :

- `test_main_window.py` - Fenêtre principale et fonctionnalités de gestion des profils
- `test_css_window.py` - Fonctionnalités de paramètres CSS
- `test_filter_window.py` - Fonctionnalités de gestion des filtres
- `test_log_window.py` - Fonctionnalités d'affichage du journal

## Dépannage

- Si le système ne peut pas trouver PlantUML ou ne peut pas exécuter Java, un message apparaîtra dans stderr. Spécifiez le chemin en utilisant des variables d'environnement ou des métadonnées YAML.
- Le système affiche les erreurs Pandoc dans le journal GUI et `pandoc.log`.

## Notes de développement

- Nous plaçons les filtres Lua dans le répertoire `filters/` (par ex. `filters/diagram.lua`).
- Nous plaçons les fichiers CSS dans le répertoire `stylesheets/`. Vous pouvez les sélectionner depuis l'interface graphique et les appliquer en tant qu'incorporés ou liens externes.
- Le système effectue la conversion dans un thread en arrière-plan, et termine/tue les processus enfants à la fermeture de l'application.
