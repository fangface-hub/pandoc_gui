---
lang: fr
---

# Aide PandocGUI

## Aperçu

PandocGUI est un outil GUI simple pour convertir des fichiers Markdown en HTML et autres formats en utilisant Pandoc. Il peut générer automatiquement des diagrammes comme Mermaid et PlantUML en utilisant des filtres Lua.

## Fonctionnalités principales

- **Conversion fichier/dossier** : Convertir des fichiers individuels ou traiter par lot plusieurs fichiers dans des dossiers
- **Filtres Lua** : Appliquer des filtres comme diagram.lua pour générer des diagrammes
- **Styles CSS** : Appliquer des feuilles de style personnalisées (incorporées/lien externe)
- **Gestion des profils** : Sauvegarder et charger les paramètres fréquemment utilisés
- **Motifs d'exclusion** : Ignorer des fichiers spécifiques lors de la conversion de dossier
- **Affichage des journaux** : Surveiller la progression de la conversion et les erreurs

## Utilisation de base

### 1. Sélectionner l'entrée

**Pour convertir un fichier :**

1. Cliquez sur le bouton "Sélection de fichier"
2. Choisissez le fichier Markdown (.md) à convertir

**Pour convertir un dossier par lot :**

1. Cliquez sur le bouton "Sélection de dossier"
2. Choisissez le dossier contenant les fichiers Markdown
3. Les fichiers dans les sous-dossiers seront traités automatiquement

### 2. Définir la destination de sortie

1. Cliquez sur le bouton "Sélection de la destination de sortie"
2. Choisissez le dossier pour enregistrer les fichiers convertis

### 3. Configurer les filtres

**Ajouter des filtres prédéfinis :**

1. Sélectionnez dans le menu déroulant "Filtres prédéfinis"
2. Cliquez sur le bouton "Ajouter"

**Ajouter des filtres utilisateur :**

1. Cliquez sur le bouton "Parcourir" pour sélectionner un fichier `.lua`
2. Cliquez sur le bouton "Ajouter"

**Changer l'ordre des filtres :**

- Sélectionnez un élément dans la liste des filtres
- Utilisez les boutons "↑" "↓" pour ajuster l'ordre

**Supprimer des filtres :**

- Sélectionnez un élément dans la liste des filtres
- Cliquez sur le bouton "Supprimer"

### 4. Configurer les styles CSS

1. Cliquez sur le bouton "Paramètres de feuille de style CSS"
2. Sélectionnez un fichier CSS
3. Choisissez la méthode d'application :
   - **Incorporer** : Incorporer le CSS dans le fichier HTML
   - **Lien externe** : Sortie en tant que fichier séparé et lien depuis HTML

### 5. Configurer les motifs d'exclusion (pour la conversion de dossier)

Pour ignorer des fichiers spécifiques lors de la conversion de dossier :

1. Cliquez sur le bouton "Gestion des motifs d'exclusion"
2. La fenêtre des motifs d'exclusion s'ouvre
3. Entrez les motifs (un par ligne)
4. Cliquez sur "OK"

**Exemples de motifs :**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. Exécuter la conversion

1. Vérifiez tous les paramètres
2. Cliquez sur le bouton "Exécuter la conversion"
3. Vérifiez la progression dans la fenêtre de journal

## Fonction de profil

Vous pouvez enregistrer les combinaisons de paramètres fréquemment utilisées en tant que profils.

### Enregistrer un profil

1. Ajustez les paramètres
2. Cliquez sur le bouton "Enregistrer le profil"
3. Entrez le nom du profil
4. Cliquez sur "OK"

### Charger un profil

1. Cliquez sur le bouton "Charger le profil"
2. Sélectionnez un profil dans la liste
3. Cliquez sur "OK"

Les profils enregistrés sont stockés dans le dossier `profiles/` au format JSON.

## Configuration PlantUML / Java

Lors de l'utilisation de diagrammes PlantUML, les chemins sont recherchés dans l'ordre de priorité suivant :

### Fichier JAR PlantUML

1. Métadonnées YAML `plantuml_jar` dans le document
2. Variable d'environnement `PLANTUML_JAR`
3. Valeur par défaut `plantuml.jar`

### Exécutable Java

1. Métadonnées YAML `java_path` dans le document
2. Variable d'environnement `JAVA_PATH`
3. Variable d'environnement `JAVA_HOME\bin\java`
4. `java` depuis PATH

### Exemples de configuration de variables d'environnement

**PowerShell :**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**Invite de commandes :**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### Spécification dans les métadonnées YAML

Ajoutez au début du fichier Markdown :

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

## Dépannage

### La conversion échoue

**Vérifier :**

- Pandoc est-il installé et ajouté à PATH ?
- Le fichier d'entrée est-il au format Markdown correct ?
- Avez-vous la permission d'écriture dans le dossier de sortie ?

**Vérifier les journaux :**

- Vérifiez les messages d'erreur dans la fenêtre de journal GUI
- Vérifiez les détails dans le fichier `pandoc.log`

### Les diagrammes ne sont pas générés

**Pour les diagrammes Mermaid :**

- Vérifiez que `mmdc` (mermaid-cli) est installé
- Exécutez `mmdc --version` dans l'invite de commandes pour confirmer

**Pour les diagrammes PlantUML :**

- Vérifiez que `plantuml.jar` existe
- Vérifiez que Java est installé
- Spécifiez le chemin dans les variables d'environnement ou les métadonnées YAML

### Les filtres ne sont pas appliqués

**Vérifier :**

- Les filtres sont-ils correctement ajoutés ? (Vérifiez la liste des filtres)
- Les fichiers Lua existent-ils avec les chemins corrects ?
- L'ordre des filtres est-il approprié ? (diagram.lua peut nécessiter un ordre spécifique)

### Les motifs d'exclusion ne fonctionnent pas

**Vérifier :**

- La syntaxe du motif est-elle correcte ? (Utilisez le caractère générique `*`)
- Le motif correspond-il aux noms de fichiers ou de dossiers ?
- Avez-vous enregistré en cliquant sur "OK" dans la fenêtre des motifs d'exclusion ?

## Questions fréquemment posées

### Q : Dans quels formats de fichier puis-je convertir ?

R : Vous pouvez convertir dans tous les formats pris en charge par Pandoc. Les principaux sont :

- HTML
- PDF (nécessite LaTeX)
- DOCX (Word)
- EPUB
- Beaucoup d'autres

Le format de sortie peut être spécifié avec les options Pandoc (prévu pour les versions futures).

### Q : Puis-je utiliser plusieurs fichiers CSS ?

R : La version actuelle ne prend en charge qu'un seul fichier CSS. Si vous avez besoin de plusieurs styles, veuillez combiner les fichiers CSS.

### Q : La structure des fichiers est-elle conservée lors de la conversion de dossier ?

R : Oui, la structure des sous-dossiers du dossier d'entrée est conservée dans la destination de sortie.

### Q : Puis-je annuler la conversion ?

R : Vous pouvez terminer le processus de conversion en toute sécurité en fermant la fenêtre. Le fichier en cours de traitement sera terminé, mais les fichiers restants seront annulés.

## Fichier journal

Les détails de conversion sont enregistrés dans les fichiers journaux suivants :

- **Emplacement** : `pandoc.log` (dans le même dossier que l'exécutable)
- **Contenu** : Sortie Pandoc, messages d'erreur, résultats de filtre

Si des problèmes surviennent, veuillez vérifier ce fichier journal.

## Annexe : À propos des filtres

### Filtres prédéfinis

Les filtres Lua placés dans le dossier `filters/` sont automatiquement détectés.

**diagram.lua :**

- Convertit les blocs de code comme Mermaid, PlantUML en diagrammes

**md2html.lua :**

- Exécute un traitement supplémentaire dans Markdown

**wikilink.lua :**

- Convertit les liens au format Wiki

### Ajout de filtres personnalisés

1. Créez un fichier `.lua` à n'importe quel emplacement
2. Cliquez sur le bouton "Parcourir" dans la section "Filtres utilisateur"
3. Sélectionnez le fichier Lua créé
4. Cliquez sur le bouton "Ajouter"

## Informations d'assistance

Si les problèmes ne sont pas résolus, veuillez signaler avec les informations suivantes :

- Version de PandocGUI que vous utilisez
- Version de Pandoc (`pandoc --version`)
- Messages d'erreur (depuis la fenêtre de journal ou `pandoc.log`)
- Étapes exécutées
- Exemple de fichier d'entrée (si possible)

---

**PandocGUI** - Interface graphique simple pour Pandoc
