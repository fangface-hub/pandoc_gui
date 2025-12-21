# Pandoc GUI

シンプルな GUI フロントエンドで Pandoc を実行し、Lua フィルターで図（Mermaid / PlantUML 等）を生成するツールです。Windows での使用を想定しています。

A simple GUI frontend for Pandoc that generates diagrams (Mermaid, PlantUML, etc.) using Lua filters. We designed it for use on Windows.

## 主な機能 / Features

- ファイル/フォルダ選択、出力先設定 / File/folder selection and output destination settings
- Lua フィルター（filters/ 配下）の適用（プリセット + ユーザー追加）/ Apply Lua filters (preset + user-added) from the `filters/` directory
- プロファイル保存/読み込み（profiles/*.json）/ Save/load profiles (`profiles/*.json`)
- ログ出力（GUI と `pandoc.log`）/ Log output (GUI and `pandoc.log`)
- バックグラウンドで Pandoc を実行、アプリ終了時に子プロセスを安全に終了 / Run Pandoc in background, safely terminate child processes on app exit

## 必要なもの / Requirements

- Python 3.8+
- Pandoc（PATH に通す / add to PATH）
- Mermaid 用 / For Mermaid: `mmdc`（mermaid-cli）
- PlantUML 用 / For PlantUML: `plantuml.jar` と / and Java（jdk/jre）
- （オプション / Optional）必要な Lua フィルター / Required Lua filters（filters/*.lua）

## 起動方法 / How to Run

1. 必要なツールをインストール（Pandoc, Node/mmdc, Java 等）/ Install required tools (Pandoc, Node/mmdc, Java, etc.)
2. リポジトリのルートで実行 / Run from the repository root:

```powershell
python main_window.py
```

## PlantUML / Java の指定方法 / Specifying PlantUML / Java Paths

以下の方法で PlantUML の JAR と Java 実行ファイルを指定できます（優先順位順）：

Specify the PlantUML JAR and Java executable using these methods (in priority order):

- PlantUML JAR: ドキュメントの YAML メタデータ `plantuml_jar` → 環境変数 `PLANTUML_JAR` → `plantuml.jar`
  - Document YAML metadata `plantuml_jar` → Environment variable `PLANTUML_JAR` → `plantuml.jar`
- Java 実行ファイル / Java executable: ドキュメントの YAML メタデータ `java_path` → 環境変数 `JAVA_PATH` → `JAVA_HOME\bin\java` → `java`（PATH）
  - Document YAML metadata `java_path` → Environment variable `JAVA_PATH` → `JAVA_HOME\bin\java` → `java` (PATH)

Windows の環境変数設定例（コマンドプロンプト）/ Windows environment variable example (Command Prompt):

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell:

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

ドキュメントの YAML に指定する例 / Example YAML specification in document:

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## 使い方（GUI）/ How to Use (GUI)

1. 「ファイル選択」または「フォルダ選択」で入力を決定 / Select input with "File Selection" or "Folder Selection"
2. 「出力先フォルダ選択」で出力ディレクトリを選択 / Select output directory with "Output Destination Selection"
3. プリセット/ユーザーフィルターを追加（順序は上下で調整）/ Add preset/user filters (adjust order with up/down buttons)
4. 「変換実行」をクリック / Click "Run Conversion"

## ログ・プロファイル / Logs & Profiles

- GUI 内にログが表示され、詳細は `pandoc.log` に記録されます。/ The GUI displays logs, and the system records details in `pandoc.log`
- プロファイルは `profiles/` に JSON 形式で保存されます。/ The system saves profiles as JSON in the `profiles/` directory

## テスト / Testing

ユニットテストが用意されています。以下のコマンドで実行できます：

We provide unit tests. Run them with the following commands:

### すべてのテストを実行 / Run All Tests

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### 個別のテストファイルを実行 / Run Individual Test Files

```powershell
# メインウィンドウのテスト / Main window tests
python -m unittest test_main_window.py

# CSS設定ウィンドウのテスト / CSS settings window tests
python -m unittest test_css_window.py

# フィルター管理ウィンドウのテスト / Filter management window tests
python -m unittest test_filter_window.py

# ログウィンドウのテスト / Log window tests
python -m unittest test_log_window.py
```

### テストの詳細出力 / Verbose Test Output

```powershell
python -m unittest discover -v
```

テストファイル / Test Files：

- `test_main_window.py` - メインウィンドウとプロファイル管理機能 / Main window and profile management features
- `test_css_window.py` - CSS設定機能 / CSS settings features
- `test_filter_window.py` - フィルター管理機能 / Filter management features
- `test_log_window.py` - ログ表示機能 / Log display features

## トラブルシューティング / Troubleshooting

- PlantUML が見つからない / Java 実行できない場合は stderr にメッセージが出ます。環境変数または YAML メタデータでパスを指定してください。
  - If the system cannot find PlantUML or cannot execute Java, a message will appear in stderr. Specify the path using environment variables or YAML metadata.
- Pandoc のエラーは GUI ログと `pandoc.log` に表示されます。
  - The system displays Pandoc errors in the GUI log and `pandoc.log`.

## 開発メモ / Development Notes

- Lua フィルターは `filters/` 配下に置いています（例: `filters/diagram.lua`）。
  - We locate Lua filters in the `filters/` directory (e.g., `filters/diagram.lua`).
- 変換はバックグラウンドスレッドで行われ、アプリ終了時に子プロセスを terminate/kill します。
  - The system performs conversion in a background thread, and terminates/kills child processes on app exit.
