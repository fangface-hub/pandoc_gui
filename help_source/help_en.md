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

### GUI Mode Usage

#### 1. Select Input

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

## Command-Line Mode

PandocGUI can also be run directly from the command line without using the GUI. This is useful for batch processing and automated execution from scripts.

### Command-Line Basic Usage

**Convert a single file:**

```bash
PandocGUI.exe -i input.md -o output.html
```

**Batch convert a folder:**

```bash
PandocGUI.exe -i input_folder -o output_folder -f pdf
```

### Command-Line Arguments

- `-i, --input`: Input file or folder path (required)
- `-o, --output`: Output file or folder path (required)
- `-f, --format`: Specify output format (default: html)
  - Choices: `html`, `pdf`, `docx`, `epub`, `markdown`
- `-p, --profile`: Profile name to use (default: default)

### Usage Examples

**Convert to HTML format (default):**

```bash
PandocGUI.exe -i document.md -o document.html
```

**Convert to PDF format:**

```bash
PandocGUI.exe -i document.md -o document.pdf -f pdf
```

**Use a custom profile:**

```bash
PandocGUI.exe -i document.md -o output.html -p myprofile
```

**Convert entire folder to Markdown format:**

```bash
PandocGUI.exe -i html_folder -o markdown_folder -f markdown
```

### Notes

- In command-line mode, settings from the specified profile (filters, CSS, exclusion patterns, etc.) will be applied
- Error messages will be displayed if the input path doesn't exist or Pandoc is not installed
- Exit codes: 0 (success), 1 (failure)

## Profile Feature

You can save frequently used setting combinations as profiles.

### Create Profile

1. Click "Add" button
2. Enter new profile name
3. Click "OK"
4. Default profile settings will be copied

### Select Profile

1. Select from profile dropdown
2. Settings are automatically loaded

### Save Profile

1. Adjust settings
2. Select target profile from dropdown
3. Click "Save" button
4. Current settings are saved to the profile

### Delete Profile

1. Select profile to delete from dropdown
2. Click "Delete" button
3. Click "Yes" in confirmation dialog

**Note:** Default profile cannot be deleted.

### Update Profile

1. Click "Load" button
2. Profile is updated with latest settings (backward compatibility)

Saved profiles are stored in the `profiles/` folder in JSON format.

## PlantUML / Java Configuration

When using PlantUML diagrams, there are two execution methods available.

### Select PlantUML Execution Method

**JAR Method (Local Execution):**

1. Select "JAR File" in "Execution Method"
2. Specify Java executable path
3. Specify PlantUML JAR file path

**Server Method (Online Execution):**

1. Select "Server" in "Execution Method"
2. Specify PlantUML server URL (Default: <http://www.plantuml.com/plantuml>)
3. Java/JAR file not required

### PlantUML JAR Method Configuration

Paths are searched in the following priority order:

#### PlantUML JAR File

1. GUI settings path
2. YAML metadata `plantuml_jar` in document
3. Environment variable `PLANTUML_JAR`
4. Default value `plantuml.jar`

#### Java Executable

1. GUI settings path
2. YAML metadata `java_path` in document
3. Environment variable `JAVA_PATH`
4. Environment variable `JAVA_HOME\bin\java`
5. `java` from PATH

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

### YAML Metadata Specification

Add to the beginning of Markdown file:

```yaml
---
plantuml_jar: C:\tools\plantuml.jar
java_path: C:\Program Files\Java\jdk-17\bin\java.exe
---
```

**When using server method:**

```yaml
---
plantuml_server: true
plantuml_server_url: http://www.plantuml.com/plantuml
---
```

### Mermaid Configuration

There are two methods for generating Mermaid diagrams:

#### Browser Mode (Default, Recommended)

**Features:**

- No command-line tool installation required
- Automatically generates diagrams using browser and mermaid.js
- Automatically saves SVG files using local HTTP server

**How to Use:**

- Select "Browser" as Mermaid method in GUI settings (default)
- Browser opens automatically during conversion and diagrams are generated
- SVG files are automatically saved to output folder

**Benefits:**

- No setup required
- Access to latest Mermaid.js features
- Environment-independent

#### mmdc Mode (Command-Line Tool)

**Features:**

- Uses mermaid-cli (`mmdc`)
- Generates diagrams headlessly

**How to Use:**

- Select "mmdc" as Mermaid method in GUI settings
- Verify `mmdc` is installed
- Run `mmdc --version` in command prompt to confirm

**Installation:**

```bash
npm install -g @mermaid-js/mermaid-cli
```

### Specifying Mermaid Mode in YAML Metadata

Add to the beginning of Markdown file:

```yaml
---
mermaid_mode: browser  # or mmdc
---
```

## Auto-Update Feature

When you update the application, the following files are automatically updated:

### Filter Files

- Built-in filters in `filters/` folder (diaglam.lua, md2html.lua, wikilink.lua)
- Automatically updated to latest version on update
- Custom filters added by users are protected

### Profile Settings

- New settings added in new versions are automatically complemented
- Existing settings are preserved
- Default values are retrieved from `profiles/default.json`

## Troubleshooting

### Pandoc Not Found

**Symptoms:**

- Warning dialog displayed on startup
- Cannot execute conversion

**Solution:**

1. Install Pandoc: <https://pandoc.org/installing.html>
2. After installation, verify it's added to PATH
3. Run `pandoc --version` in command prompt to confirm

### Conversion Fails

**Check:**

- Is Pandoc installed and added to PATH?
- Is the input file in correct Markdown format?
- Do you have write permission to the output folder?

**Check logs:**

- Check error messages in the GUI log window
- Check details in `pandoc.log` file

### Diagrams Not Generated

**For Mermaid diagrams (mmdc mode):**

- Verify `mmdc` (mermaid-cli) is installed
- Run `mmdc --version` in command prompt to confirm

**For Mermaid diagrams (browser mode):**

- Browser mode should work without additional setup
- Check if the browser opens automatically
- Verify SVG files are saved to the output folder

**For PlantUML diagrams:**

**JAR Method:**

- Verify `plantuml.jar` exists
- Verify Java is installed
- Specify path in GUI settings, environment variables, or YAML metadata

**Server Method:**

- Verify internet connection
- Verify server URL is correct (Default: <http://www.plantuml.com/plantuml>)
- Check firewall settings

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

**PandocGUI** - Simple GUI Frontend for Pandoc
