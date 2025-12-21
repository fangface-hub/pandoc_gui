# Pandoc GUI

シンプルな GUI フロントエンドで Pandoc を実行し、Lua フィルターで図（Mermaid / PlantUML 等）を生成するツールです。Windows での使用を想定しています。

## 主な機能

- ファイル/フォルダ選択、出力先設定
- Lua フィルター（filters/ 配下）の適用（プリセット + ユーザー追加）
- プロファイル保存/読み込み（profiles/*.json）
- ログ出力（GUI と `pandoc.log`）
- バックグラウンドで Pandoc を実行、アプリ終了時に子プロセスを安全に終了

## 必要なもの

- Python 3.8+
- Pandoc（PATH に通す）
- Mermaid 用: `mmdc`（mermaid-cli）
- PlantUML 用: `plantuml.jar` と Java（jdk/jre）
- （オプション）必要な Lua フィルター（filters/*.lua）

## 起動方法

1. 必要なツールをインストール（Pandoc, Node/mmdc, Java 等）
2. リポジトリのルートで実行:

```powershell
python pandoc_gui.py
```

## PlantUML / Java の指定方法

PlantUML の JAR と Java 実行ファイルは、以下の順で決定されます。

- PlantUML JAR: ドキュメントの YAML メタデータ `plantuml_jar` → 環境変数 `PLANTUML_JAR` → `plantuml.jar`
- Java 実行ファイル: ドキュメントの YAML メタデータ `java_path` → 環境変数 `JAVA_PATH` → `JAVA_HOME\bin\java` → `java`（PATH）

Windows の環境変数設定例（コマンドプロンプト）:

```bat
set PLANTUML_JAR=C:\path\to\plantuml.jar
set JAVA_PATH=C:\path\to\java.exe
```

PowerShell:

```powershell
$env:PLANTUML_JAR = 'C:\path\to\plantuml.jar'
$env:JAVA_PATH = 'C:\path\to\java.exe'
```

ドキュメントの YAML に指定する例:

```yaml
---
plantuml_jar: C:\path\to\plantuml.jar
java_path: C:\path\to\java.exe
---
```

## 使い方（GUI）

1. 「ファイル選択」または「フォルダ選択」で入力を決定
2. 「出力先フォルダ選択」で出力ディレクトリを選択
3. プリセット/ユーザーフィルターを追加（順序は上下で調整）
4. 「変換実行」をクリック

## ログ・プロファイル

- GUI 内にログが表示され、詳細は `pandoc.log` に記録されます。
- プロファイルは `profiles/` に JSON 形式で保存されます。

## トラブルシューティング

- PlantUML が見つからない / Java 実行できない場合は stderr にメッセージが出ます。環境変数または YAML メタデータでパスを指定してください。
- Pandoc のエラーは GUI ログと `pandoc.log` に表示されます。

## 開発メモ

- Lua フィルターは `filters/` 配下に置いています（例: `filters/diagram.lua`）。
- 変換はバックグラウンドスレッドで行われ、アプリ終了時に子プロセスを terminate/kill します。
