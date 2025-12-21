---
lang: en
---

# PandocGUI Help

## Overview

PandocGUI is a simple GUI tool for converting Markdown files to HTML and other formats using Pandoc. It can automatically generate diagrams like Mermaid and PlantUML using Lua filters.

## Main Features

- **File/Folder Conversion**: Convert single files or batch process multiple files in folders
- **Lua Filters**: Apply filters like diagram.lua to generate diagrams
- **CSS Styles**: Apply custom stylesheets (embedded/external link)
- **Profile Management**: Save and load frequently used settings
- **Exclusion Patterns**: Skip specific files during folder conversion
- **Log Display**: Monitor conversion progress and errors

## Basic Usage

### 1. Select Input

**To convert a file:**

1. Click "File Selection" button
2. Choose the Markdown file (.md) to convert

**To batch convert a folder:**

1. Click "Folder Selection" button
2. Choose the folder containing Markdown files
3. Files in subfolders will be processed automatically

### 2. Set Output Destination

1. Click "Output Destination Selection" button
2. Choose the folder to save converted files

### 3. Configure Filters

**Add preset filters:**

1. Select from "Preset Filters" dropdown
2. Click "Add" button

**Add user filters:**

1. Click "Browse" button to select a `.lua` file
2. Click "Add" button

**Change filter order:**

- Select an item in the filter list
- Use "↑" "↓" buttons to adjust order

**Remove filters:**

- Select an item in the filter list
- Click "Delete" button

### 4. Configure CSS Styles

1. Click "CSS Stylesheet Settings" button
2. Select a CSS file
3. Choose application method:
   - **Embed**: Embed CSS within the HTML file
   - **External Link**: Output as a separate file and link from HTML

### 5. Configure Exclusion Patterns (For Folder Conversion)

To skip specific files during folder conversion:

1. Click "Exclusion Pattern Management" button
2. Exclusion pattern window opens
3. Enter patterns (one per line)
4. Click "OK"

**Pattern examples:**

```text
*.tmp
__pycache__
.git
test_*
*_backup
node_modules
```

### 6. Execute Conversion

1. Verify all settings
2. Click "Run Conversion" button
3. Check progress in the log window

## Profile Feature

You can save frequently used setting combinations as profiles.

### Save Profile

1. Adjust settings
2. Click "Save Profile" button
3. Enter profile name
4. Click "OK"

### Load Profile

1. Click "Load Profile" button
2. Select a profile from the list
3. Click "OK"

Saved profiles are stored in the `profiles/` folder in JSON format.

## PlantUML / Java Configuration

When using PlantUML diagrams, paths are searched in the following priority order:

### PlantUML JAR File

1. YAML metadata `plantuml_jar` in document
2. Environment variable `PLANTUML_JAR`
3. Default value `plantuml.jar`

### Java Executable

1. YAML metadata `java_path` in document
2. Environment variable `JAVA_PATH`
3. Environment variable `JAVA_HOME\bin\java`
4. `java` from PATH

### Environment Variable Configuration Examples

**PowerShell:**

```powershell
$env:PLANTUML_JAR = 'C:\tools\plantuml.jar'
$env:JAVA_PATH = 'C:\Program Files\Java\jdk-17\bin\java.exe'
```

**Command Prompt:**

```bat
set PLANTUML_JAR=C:\tools\plantuml.jar
set JAVA_PATH=C:\Program Files\Java\jdk-17\bin\java.exe
```

### Specification in YAML Metadata

Add to the beginning of the Markdown file:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

## Troubleshooting

### Conversion Fails

**Check:**

- Is Pandoc installed and added to PATH?
- Is the input file in correct Markdown format?
- Do you have write permission to the output folder?

**Check logs:**

- Check error messages in the GUI log window
- Check details in `pandoc.log` file

### Diagrams Not Generated

**For Mermaid diagrams:**

- Verify `mmdc` (mermaid-cli) is installed
- Run `mmdc --version` in command prompt to confirm

**For PlantUML diagrams:**

- Verify `plantuml.jar` exists
- Verify Java is installed
- Specify path in environment variables or YAML metadata

### Filters Not Applied

**Check:**

- Are filters correctly added? (Check filter list)
- Do Lua files exist with correct paths?
- Is filter order appropriate? (diagram.lua may require specific order)

### Exclusion Patterns Not Working

**Check:**

- Is pattern syntax correct? (Use wildcard `*`)
- Does pattern match file or folder names?
- Did you save by clicking "OK" in the exclusion pattern window?

## Frequently Asked Questions

### Q: What file formats can I convert to?

A: You can convert to all formats supported by Pandoc. Main ones include:

- HTML
- PDF (requires LaTeX)
- DOCX (Word)
- EPUB
- Many others

Output format can be specified with Pandoc options (planned for future versions).

### Q: Can I use multiple CSS files?

A: The current version supports only one CSS file. If you need multiple styles, please combine CSS files.

### Q: Is file structure preserved during folder conversion?

A: Yes, subfolder structure of the input folder is preserved in the output destination.

### Q: Can I cancel conversion?

A: Closing the window safely terminates the conversion process. Files being processed will complete, but remaining files will be canceled.

## Log Files

Conversion details are recorded in the following log file:

- **Location**: `pandoc.log` (same folder as executable)
- **Contents**: Pandoc output, error messages, filter execution results

Check this log file if problems occur.

## Appendix: About Filters

### Preset Filters

Lua filters placed in the `filters/` folder are automatically detected.

**diagram.lua:**

- Converts code blocks like Mermaid, PlantUML to diagrams

**md2html.lua:**

- Performs additional processing within Markdown

**wikilink.lua:**

- Converts Wiki-style links

### Adding Custom Filters

1. Create a `.lua` file anywhere
2. Click "Browse" button in "User Filters" section
3. Select the created Lua file
4. Click "Add" button

## Support Information

If problems persist, please report with the following information:

- PandocGUI version you're using
- Pandoc version (`pandoc --version`)
- Error messages (from log window or `pandoc.log`)
- Steps you performed
- Sample input file (if possible)

---

**PandocGUI** - Simple GUI frontend for Pandoc  
Version 1.0
