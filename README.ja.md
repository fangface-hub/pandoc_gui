# Pandoc GUI

[English](README.md) | [Deutsch](README.de.md) | [中文](README.zh.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [한국어](README.ko.md)

シンプルな GUI フロントエンドで Pandoc を実行し、Lua フィルターで図（Mermaid / PlantUML 等）を生成するツールです。Windows での使用を想定しています。

## 主な機能

- ファイル/フォルダ選択、出力先設定
- Lua フィルター（filters/ 配下）の適用（プリセット + ユーザー追加）
- CSS スタイル設定（stylesheets/ 配下）、埋め込み/外部リンクの選択
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
    python main_window.py
    ```

## PlantUML / Java の指定方法

以下の方法で PlantUML の JAR と Java 実行ファイルを指定できます（優先順位順）：

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
4. （オプション）除外パターンを設定してフォルダ変換時に特定のファイルをスキップ
5. 「変換実行」をクリック

### 除外パターンの設定

フォルダを一括変換する際、特定のファイルやフォルダを除外できます：

- 「除外パターン管理」ボタンをクリックして設定ウィンドウを開く
- ワイルドカードパターンを使用可能（例: `*.tmp`, `__pycache__`, `.git`）
- 複数のパターンを追加可能（各行に1つずつ）

パターンのマッチング例:

- `*.tmp` - すべての .tmp ファイルを除外
- `__pycache__` - __pycache__ フォルダとその内容を除外
- `.git` - .git フォルダを除外
- `test_*` - test_ で始まるファイルを除外
- `*_backup` - _backup で終わるファイルを除外

## ログ・プロファイル

- GUI 内にログが表示され、詳細は `pandoc.log` に記録されます
- プロファイルは `profiles/` に JSON 形式で保存されます

## 配布用パッケージの作成

### PyInstallerでフォルダ形式の実行ファイルを作成

1. PyInstallerをインストール:

    ```powershell
    pip install pyinstaller
    ```

2. 実行ファイルを作成:

    __注意__: `PandocGUI.spec`はリポジトリに含まれており、ビルド後処理（`filters/`と`locales/`を`_internal/`の外に配置）が設定済みです。

    ```powershell
    python -m PyInstaller PandocGUI.spec
    ```

    `.spec`ファイルを再生成したい場合のみ、以下のコマンドを実行してください（通常は不要）:

    ```powershell
    pyinstaller --noconsole --onedir --name "PandocGUI" `
      --add-data "locales;locales" `
      --add-data "filters;filters" `
      --add-data "stylesheets;stylesheets" `
      main_window.py
    ```

    __重要__: 上記コマンドで生成した`.spec`ファイルには、手動でビルド後処理を追加する必要があります。

3. ビルド結果は`dist/PandocGUI/`に出力されます:

    ```text
    dist/PandocGUI/
    ├── PandocGUI.exe        # 実行ファイル
    ├── filters/             # Luaフィルター
    ├── locales/             # 翻訳ファイル
    ├── stylesheets/         # CSSスタイルシート
    ├── help/                # ヘルプファイル（HTML）
    ├── profiles/            # プロファイル（実行時作成）
    └── _internal/           # Python依存関係
    ```

    `.spec`ファイルのビルド後処理により、`filters/`、`locales/`、`stylesheets/`が`_internal/`の外に配置されます。

### MSIX Packaging ToolでWindowsインストーラを作成

1. MSIX Packaging Toolをインストール:

   - Microsoft Storeから「MSIX Packaging Tool」をインストール

2. MSIX Packaging Toolを起動し、「Application package」を選択

3. 「Create package on this computer」を選択

4. パッケージ情報を入力:

    - Package name: `PandocGUI`
    - Publisher: `CN=YourName` （証明書に合わせて変更）
    - Version: `1.0.0.0`

5. インストーラの選択:

    - 「Browse」をクリックし、`dist/PandocGUI/PandocGUI.exe`を選択
    - Installation location: `C:\Program Files\PandocGUI`

6. インストールの実行とキャプチャ:

   - アプリを起動して動作を確認
   - 必要なファイルがすべて含まれていることを確認
   - 「Done」をクリック

7. パッケージの保存:

    - .msixファイルとして保存

8. 署名（オプション）:

    - テスト用の証明書を作成するか、既存の証明書を使用

    ```powershell
    # テスト用証明書の作成
    New-SelfSignedCertificate -Type Custom -Subject "CN=YourName" `
      -KeyUsage DigitalSignature -FriendlyName "PandocGUI Test Certificate" `
      -CertStoreLocation "Cert:\CurrentUser\My" `
      -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
    
    # MSIXファイルに署名
    SignTool sign /fd SHA256 /a /f certificate.pfx /p password PandocGUI.msix
    ```

9. インストーラの配布:

   - .msixファイルを配布
   - ユーザーは証明書をインストールしてからアプリをインストール

### 注意事項

- `filters/`や`locales/`などのリソースファイルが正しく含まれているか確認してください
- Pandoc、mmdc、Java等の外部ツールは別途インストールが必要です
- MSIXパッケージは署名が必要です（開発時はテスト証明書を使用可能）

## テスト

ユニットテストが用意されています。以下のコマンドで実行できます：

### すべてのテストを実行

```powershell
python -m unittest discover -s . -p "test_*.py"
```

### 個別のテストファイルを実行

```powershell
python -m unittest test_<name>.py
```

例：

```powershell
python -m unittest test_main_window.py
```

### テストの詳細出力

```powershell
python -m unittest discover -v
```

テストファイル:

- `test_main_window.py` - メインウィンドウとプロファイル管理機能
- `test_css_window.py` - CSS設定機能
- `test_filter_window.py` - フィルター管理機能
- `test_log_window.py` - ログ表示機能

## トラブルシューティング

- PlantUML が見つからない / Java 実行できない場合は stderr にメッセージが出ます。環境変数または YAML メタデータでパスを指定してください。
- Pandoc のエラーは GUI ログと `pandoc.log` に表示されます。

## 開発メモ

- Lua フィルターは `filters/` 配下に置いています（例: `filters/diagram.lua`）。
- CSS ファイルは `stylesheets/` 配下に置いています。GUI から選択して埋め込みまたは外部リンクとして適用できます。
- 変換はバックグラウンドスレッドで行われ、アプリ終了時に子プロセスを terminate/kill します。
