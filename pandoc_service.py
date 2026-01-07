# -*- coding: utf-8 -*-
"""Pandoc変換サービス."""
import http.server
import json
import logging
import os
import platform
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from fnmatch import fnmatch
from pathlib import Path

# Windowsでのプロセス管理用フラグ
if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_PROCESS_GROUP = 0x00000200
else:
    CREATE_NO_WINDOW = 0
    CREATE_NEW_PROCESS_GROUP = 0


def check_pandoc_installed():
    """pandocがインストールされているかチェックする.

    Check if pandoc is installed.

    Returns
    -------
    bool
        pandocが利用可能な場合True (True if pandoc is available)
    """
    try:
        result = subprocess.run(["pandoc", "--version"],
                                capture_output=True,
                                text=True,
                                timeout=5,
                                check=False)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        return False


def get_app_dir() -> Path:
    """アプリケーションのルートディレクトリを取得.

    Get application root directory.

    PyInstallerでビルドされた場合は実行ファイルのディレクトリ、
    開発環境ではスクリプトのディレクトリを返します。

    Returns
    -------
    Path
        アプリケーションのルートディレクトリ
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた場合
        return Path(sys.executable).parent
    else:
        # 通常のPythonスクリプトとして実行される場合
        return Path(__file__).parent


def get_data_dir() -> Path:
    """データディレクトリを取得 / Get data directory.

    プラットフォームごとに適切な場所を返します。
    Returns appropriate location for each platform:
    - Windows: %LOCALAPPDATA%\\PandocGUI
    - macOS: ~/Library/Application Support/PandocGUI
    - Linux: ~/.local/share/PandocGUI (XDG Base Directory)

    Returns
    -------
    Path
        データディレクトリ / Data directory path
    """
    if platform.system() == "Windows":
        return Path(os.getenv("LOCALAPPDATA",
                              os.path.expanduser("~"))) / "PandocGUI"

    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Application Support" / "PandocGUI"

    # Linux and other Unix-like systems
    return Path(os.getenv("XDG_DATA_HOME",
                          Path.home() / ".local" / "share")) / "PandocGUI"


# PyInstallerビルド時のパス解決
SCRIPT_DIR = get_app_dir()

# データディレクトリ（プラットフォームごとに適切な場所を使用）
DATA_DIR = get_data_dir()

# プロファイルディレクトリ（DATA_DIR配下）
PROFILE_DIR = DATA_DIR / "profiles"


def to_relative_path(path: Path) -> str:
    """パスをデータディレクトリ基準の相対パスに変換.

    Convert path to relative path based on data directory.

    Parameters
    ----------
    path : Path
        変換するパス (Path to convert)
    Returns
    -------
    str
        相対パスまたは絶対パス (Relative path or absolute path)
    """
    if not path:
        return None
    path = Path(path).resolve()
    try:
        rel_path = path.relative_to(DATA_DIR.resolve())
        return str(rel_path)
    except ValueError:
        # データディレクトリ以下でない場合は絶対パスで保存
        return str(path)


def from_relative_path(path_str: str) -> Path:
    """相対パスをデータディレクトリ基準で解決.

    Resolve relative path based on data directory.

    Parameters
    ----------
    path_str : str
        パス文字列 (Path string)
    Returns
    -------
    Path
        解決されたパス (Resolved path)
    """
    if not path_str:
        return None
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (DATA_DIR / path).resolve()


def save_profile(name: str, data: dict):
    """プロファイル保存.

    Save profile.

    Parameters
    ----------
    name : str
        名称 (Name)
    data : dict
        辞書データ (Dictionary data)
    """
    path = PROFILE_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_profile(name: str) -> dict:
    """プロファイル読み込み.

    Load profile.

    バージョンアップ後に新しいキーが追加された場合、
    SCRIPT_DIR/profiles/default.jsonから不足しているキーを補完します。
    If new keys are added after version update,
    missing keys are complemented from SCRIPT_DIR/profiles/default.json.

    Parameters
    ----------
    name : str
        名称 (Name)
    Returns
    -------
    dict or None
        プロファイルデータ、またはファイルが存在しない場合はNone
        (Profile data, or None if file does not exist)
    """
    path = PROFILE_DIR / f"{name}.json"
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8-sig") as f:
        user_data = json.load(f)

    # SCRIPT_DIRのデフォルトプロファイルからマスターキーを取得
    # Get master keys from SCRIPT_DIR default profile
    master_default_path = SCRIPT_DIR / "profiles" / "default.json"
    if master_default_path.exists():
        try:
            with open(master_default_path, "r", encoding="utf-8-sig") as f:
                master_default = json.load(f)

            # 不足しているキーをマスターデフォルトから補完
            # Complement missing keys from master default
            updated = False
            for key, value in master_default.items():
                if key not in user_data:
                    user_data[key] = value
                    updated = True

            # キーが補完された場合はファイルを保存
            # Save file if keys were complemented
            if updated:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(user_data, f, indent=2, ensure_ascii=False)

        except (OSError, ValueError, json.JSONDecodeError):
            # マスターデフォルトが読めない場合はユーザーデータをそのまま使用
            # Use user data as-is if master default cannot be read
            pass

    return user_data


def init_default_profile():
    """デフォルトプロファイルを初期化する.

    Initialize default profile.
    """
    default_data = {
        "filters": [],
        "exclude_patterns": [],
        "css_file": None,
        "embed_css": True,
        "output_format": "html",
        "language": None,  # None = auto-detect
        "java_path": None,
        "plantuml_jar": None,
        "plantuml_use_server": False,
        "plantuml_server_url": "http://www.plantuml.com/plantuml",
        "mermaid_mode": "mmdc",  # mmdc or browser
    }
    path = PROFILE_DIR / "default.json"
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)


class PandocService:
    """Pandoc変換サービスクラス.

    Business logic for Pandoc conversion.
    """

    def __init__(self, logger: logging.Logger):
        """初期化.

        Initialize.

        Parameters
        ----------
        logger : logging.Logger
            ロガーインスタンス
        """
        self.logger = logger
        self.enabled_filters = []
        self.exclude_patterns = []
        self.css_file = None
        self.embed_css = True
        self.output_format = "html"
        self.java_path = None
        self.plantuml_jar = None
        self.plantuml_use_server = False
        self.plantuml_server_url = "http://www.plantuml.com/plantuml"
        self.mermaid_mode = "browser"  # mmdc or browser
        self.local_server = None
        self.server_port = None
        self.server_thread = None
        self.output_dir = None

    def start_local_server(self, directory: Path) -> int:
        """ローカルHTTPサーバを起動する（Mermaid SVG保存用）.

        Start local HTTP server for Mermaid SVG saving.

        Parameters
        ----------
        directory : Path
            サーバのルートディレクトリ

        Returns
        -------
        int
            割り当てられたポート番号、失敗時はNone
        """
        if self.local_server:
            self.logger.info("Stopping existing local server...")
            self.stop_local_server()

        try:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)

            self.output_dir = directory.resolve()
            logger = self.logger

            class MermaidHTTPRequestHandler(http.server.SimpleHTTPRequestHandler
                                            ):
                """Mermaid SVG保存用カスタムHTTPハンドラ."""

                def __init__(self, *args, **kwargs):
                    super().__init__(*args,
                                     directory=str(directory.resolve()),
                                     **kwargs)

                def do_POST(self) -> None:  # pylint: disable=C0103
                    """Handle POST requests to save SVG data / SVGデータを受け取って保存.
                    This method processes POST requests to the '/save-svg'
                    endpoint. It receives JSON data containing SVG content and
                    filename, saves the SVG file to disk, and returns a JSON
                    response indicating success or failure.
                    The method name 'do_POST' follows the naming convention
                    required by http.server.BaseHTTPRequestHandler and cannot
                    be changed to snake_case.
                    Returns:
                        None
                    Raises:
                        json.JSONDecodeError: If the POST data cannot be
                            parsed as JSON.
                        IOError: If the SVG file cannot be written to disk.
                    Response Codes:
                        200: SVG file saved successfully
                        500: Error occurred while processing or saving the SVG
                        404: Request path does not match '/save-svg'
                    """
                    if self.path.startswith('/save-svg'):
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)

                        # JSONとして解析
                        try:
                            data = json.loads(post_data.decode('utf-8'))
                            svg_content = data.get('svg', '')
                            filename = data.get('filename', 'diagram.svg')

                            # SVGファイルを保存
                            svg_path = directory / filename
                            with open(svg_path, 'w', encoding='utf-8') as f:
                                f.write(svg_content)

                            logger.info("Saved SVG: %s", svg_path)

                            # 成功レスポンス
                            self.send_response(200)
                            self.send_header('Content-type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            response = json.dumps({'status': 'success'})
                            self.wfile.write(response.encode('utf-8'))

                        except (json.JSONDecodeError, IOError) as e:
                            logger.error("Failed to save SVG: %s", e)
                            self.send_response(500)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def log_message(self, fmt, *args):  # pylint: disable=W0221
                    """ログ出力を抑制."""

            self.local_server = socketserver.TCPServer(
                ("127.0.0.1", 0), MermaidHTTPRequestHandler)
            self.server_port = self.local_server.server_address[1]

            self.server_thread = threading.Thread(
                target=self.local_server.serve_forever, daemon=True)
            self.server_thread.start()

            self.logger.info("Local HTTP server started on http://127.0.0.1:%d",
                             self.server_port)
            return self.server_port

        except (OSError, IOError) as e:
            self.logger.error("Failed to start local server: %s", e)
            self.local_server = None
            self.server_port = None
            return None

    def stop_local_server(self):
        """ローカルHTTPサーバを停止する.

        Stop local HTTP server.
        """
        if self.local_server:
            try:
                self.local_server.shutdown()
                self.local_server.server_close()
                self.logger.info("Local HTTP server stopped")
            except (OSError, IOError) as e:
                self.logger.error("Failed to stop local server: %s", e)
            finally:
                self.local_server = None
                self.server_port = None
                self.server_thread = None
                self.output_dir = None

    def should_exclude(self, relative_path: Path) -> bool:
        """ファイルパスが除外パターンに一致するかチェックする.

        Check if file path matches exclude patterns.

        Parameters
        ----------
        relative_path : Path
            チェックするファイルパス (File path to check)

        Returns
        -------
        bool
            除外する場合True (True if should be excluded)
        """
        path_str = str(relative_path)
        parts = relative_path.parts

        for pattern in self.exclude_patterns:
            # ファイル名またはフォルダ名でマッチング
            if fnmatch(relative_path.name, pattern):
                return True
            # パス全体でマッチング
            if fnmatch(path_str, pattern):
                return True
            # パスの各部分でマッチング（フォルダ名での除外用）
            for part in parts:
                if fnmatch(part, pattern):
                    return True

        return False

    def create_metadata_file(self,
                             input_file: Path,
                             java_path_override: str = None,
                             plantuml_jar_override: str = None) -> Path:
        """Java/PlantUML設定用の一時メタデータファイルを作成する.

        Create temporary metadata file for Java/PlantUML settings.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス (Input file path)
        java_path_override : str, optional
            GUI設定のJavaパス（オーバーライド用）
        plantuml_jar_override : str, optional
            GUI設定のPlantUML JARパス（オーバーライド用）

        Returns
        -------
        Path or None
            一時メタデータファイルのパス、設定が不要な場合はNone
            (Path to temporary metadata file, or None if not needed)
        """
        # GUI設定を優先
        final_java_path = java_path_override or (str(self.java_path)
                                                 if self.java_path else "")
        final_plantuml_jar = plantuml_jar_override or (str(
            self.plantuml_jar) if self.plantuml_jar else "")

        # 環境変数も確認
        if not final_java_path:
            final_java_path = os.getenv("JAVA_PATH") or ""
        if not final_plantuml_jar:
            final_plantuml_jar = os.getenv("PLANTUML_JAR") or ""

        # PlantUMLサーバ設定
        use_server = self.plantuml_use_server
        server_url = self.plantuml_server_url if use_server else ""

        # Mermaidモード設定
        mermaid_mode = self.mermaid_mode

        # 全ての設定がない場合は何もしない
        no_settings = (not final_java_path and not final_plantuml_jar
                       and not use_server and mermaid_mode == "mmdc")
        if no_settings:
            return None

        # 一時ファイルを作成
        temp_fd, temp_path = tempfile.mkstemp(suffix='.md', text=True)
        temp_file = Path(temp_path)

        try:
            yaml_lines = []
            yaml_lines.append("---\n")

            # Mermaidモード設定
            if mermaid_mode:
                yaml_lines.append(f"mermaid_mode: {mermaid_mode}\n")

            if use_server:
                # PlantUMLサーバを使用
                yaml_lines.append("plantuml_server: true\n")
                if server_url:
                    yaml_lines.append(f"plantuml_server_url: {server_url}\n")
            else:
                # JAR方式を使用
                if final_java_path:
                    # Windowsパスをフォワードスラッシュに変換（YAMLで安全）
                    forward_slash_path = final_java_path.replace('\\', '/')
                    yaml_lines.append(f"java_path: {forward_slash_path}\n")
                if final_plantuml_jar:
                    # Windowsパスをフォワードスラッシュに変換（YAMLで安全）
                    forward_slash_path = final_plantuml_jar.replace('\\', '/')
                    yaml_lines.append(f"plantuml_jar: {forward_slash_path}\n")
            yaml_lines.append("---\n\n")

            with open(temp_fd, 'w', encoding='utf-8') as f:
                # YAMLメタデータを書き込む
                f.writelines(yaml_lines)

                # 元のファイル内容を追記
                with open(input_file, 'r', encoding='utf-8') as input_f:
                    content = input_f.read()
                    # 元のファイルに既にYAMLメタデータがある場合は削除
                    if content.startswith('---\n'):
                        parts = content.split('---\n', 2)
                        if len(parts) >= 3:
                            content = parts[2]
                    f.write(content)

            return temp_file

        except (OSError, IOError) as e:
            self.logger.error(f"Failed to create temp metadata file: {e}")
            try:
                temp_file.unlink()
            except (OSError, IOError):
                pass
            return None

    def build_pandoc_command(self,
                             input_file: Path,
                             output_file: Path,
                             temp_metadata_file: Path = None) -> list:
        """Pandocコマンドを構築する.

        Build Pandoc command.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス
        output_file : Path
            出力ファイルパス
        temp_metadata_file : Path, optional
            一時メタデータファイル

        Returns
        -------
        list
            コマンドリスト
        """
        actual_input = temp_metadata_file if temp_metadata_file else input_file
        cmd = ["pandoc", str(actual_input), "-o", str(output_file)]

        for f in self.enabled_filters:
            cmd.extend(["--lua-filter", str(f)])

        # 入力形式を判定
        input_format = input_file.suffix.lower().lstrip('.')

        # --extract-media オプションを追加する条件
        extract_media_conditions = [
            (input_format == "docx" and self.output_format == "markdown"),
            (input_format == "docx" and self.output_format == "html"),
            (input_format == "html" and self.output_format == "markdown"),
        ]

        if any(extract_media_conditions):
            # 出力ファイルと同じディレクトリにmediaフォルダを作成
            media_dir = output_file.parent / "media"
            cmd.extend(["--extract-media", str(media_dir)])

        # CSSを適用（DOCX以外）
        if (self.output_format != "docx" and self.css_file
                and self.css_file.exists()):
            cmd.extend(["--css", str(self.css_file)])

        # PDF変換時は日本語対応のPDFエンジンを使用
        if self.output_format == "pdf":
            cmd.extend(["--pdf-engine=lualatex"])
            # 日本語対応のLaTeXテンプレート変数を設定
            cmd.extend(["-V", "documentclass=ltjsarticle"])

        # スタンドアロン形式（HTML, PDF, EPUB）
        if self.output_format in ["html", "pdf", "epub"]:
            cmd.append("--standalone")

            # HTML出力時は数式レンダリングにMathJaxを使用
            if self.output_format == "html":
                cmd.append("--mathjax")

            # 埋め込みモードの場合はリソースも埋め込む
            if self.css_file and self.css_file.exists() and self.embed_css:
                cmd.append("--embed-resources")

        return cmd

    def execute_pandoc(self,
                       cmd: list,
                       output_file: Path,
                       temp_metadata_file: Path = None) -> tuple:
        """Pandocコマンドを実行する.

        Execute Pandoc command.

        Parameters
        ----------
        cmd : list
            実行するコマンド
        output_file : Path
            出力ファイルパス
        temp_metadata_file : Path, optional
            一時メタデータファイル

        Returns
        -------
        tuple
            (success: bool, stdout: str, stderr: str, returncode: int)
        """
        try:
            # Windowsではプロセスグループを作成し、コンソールウィンドウを
            # 表示しない
            creationflags = 0
            if platform.system() == "Windows":
                creationflags = CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP

            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    encoding="utf-8",
                                    errors="replace",
                                    creationflags=creationflags)

            stdout_text, stderr_text = proc.communicate()

            success = proc.returncode == 0
            if success:
                self.logger.info(f"Conversion success: {output_file}")
                if stdout_text.strip():
                    self.logger.info(f"STDOUT:\n{stdout_text}")
                if stderr_text.strip():
                    self.logger.info(f"STDERR:\n{stderr_text}")
            else:
                self.logger.error(
                    f"Conversion failed (code={proc.returncode}): "
                    f"{stderr_text.strip() or 'Unknown error'}")
                if stderr_text.strip():
                    self.logger.error(f"STDERR:\n{stderr_text}")

            return (success, stdout_text, stderr_text, proc.returncode)

        except (OSError, ValueError, subprocess.SubprocessError) as e:
            self.logger.exception(f"Pandoc execution error: {e}")
            return (False, "", str(e), -1)

        finally:
            # 一時メタデータファイルを削除
            if temp_metadata_file and temp_metadata_file.exists():
                try:
                    temp_metadata_file.unlink()
                    self.logger.info(
                        f"Temp metadata deleted: {temp_metadata_file}")
                except (OSError, IOError) as e:
                    self.logger.warning(f"Failed to delete temp metadata: "
                                        f"{temp_metadata_file}, {e}")

    def convert_file(self,
                     input_file: Path,
                     output_file: Path,
                     java_path_override: str = None,
                     plantuml_jar_override: str = None) -> tuple:
        """単一ファイルの変換を実行する.

        Execute conversion for a single file.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス
        output_file : Path
            出力ファイルパス
        java_path_override : str, optional
            GUI設定のJavaパス
        plantuml_jar_override : str, optional
            GUI設定のPlantUML JARパス

        Returns
        -------
        tuple
            (success: bool, stdout: str, stderr: str, returncode: int)
        """
        temp_metadata_file = self.create_metadata_file(input_file,
                                                       java_path_override,
                                                       plantuml_jar_override)

        cmd = self.build_pandoc_command(input_file, output_file,
                                        temp_metadata_file)

        self.logger.info(f"Command execution: {' '.join(cmd)}")

        return self.execute_pandoc(cmd, output_file, temp_metadata_file)

    def convert_folder(self,
                       input_folder: Path,
                       output_folder: Path,
                       ext: str,
                       java_path_override: str = None,
                       plantuml_jar_override: str = None,
                       progress_callback=None) -> tuple:
        """フォルダ内のファイルを一括変換する.

        Convert all files in a folder.

        Parameters
        ----------
        input_folder : Path
            入力フォルダパス
        output_folder : Path
            出力フォルダパス
        ext : str
            出力ファイルの拡張子
        java_path_override : str, optional
            GUI設定のJavaパス
        plantuml_jar_override : str, optional
            GUI設定のPlantUML JARパス
        progress_callback : callable, optional
            進捗コールバック関数 (current, total, relative_path)

        Returns
        -------
        tuple
            (成功数, 失敗数, エラーリスト)
        """
        # 変換対象の拡張子
        convertible_extensions = {
            ".md", ".markdown", ".html", ".htm", ".tex", ".rst", ".org",
            ".textile", ".xml", ".epub", ".docx"
        }

        # 出力フォルダが存在しない場合は作成
        output_folder.mkdir(parents=True, exist_ok=True)

        # 変換対象ファイルのリストを作成
        files_to_convert = []
        files_to_copy = []

        for input_file in input_folder.rglob("*"):
            if input_file.is_file():
                relative_path = input_file.relative_to(input_folder)

                # 除外パターンチェック
                if self.should_exclude(relative_path):
                    continue

                if input_file.suffix.lower() in convertible_extensions:
                    output_file = output_folder / relative_path.parent / (
                        input_file.stem + ext)
                    files_to_convert.append(
                        (input_file, output_file, relative_path))
                else:
                    output_file = output_folder / relative_path
                    files_to_copy.append(
                        (input_file, output_file, relative_path))

        total_files = len(files_to_convert)
        success_count = 0
        fail_count = 0
        errors = []

        # 変換ファイルを順次処理
        for idx, (input_file, output_file,
                  relative_path) in enumerate(files_to_convert, 1):
            output_file.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Converting file: {relative_path} -> "
                             f"{output_file.relative_to(output_folder)}")

            # 進捗コールバック
            if progress_callback:
                progress_callback(idx, total_files, relative_path)

            # 変換を実行
            success, _stdout, _stderr, _returncode = self.convert_file(
                input_file, output_file, java_path_override,
                plantuml_jar_override)

            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append((relative_path, _stderr or "Unknown error"))

        # コピーファイルを処理
        for input_file, output_file, relative_path in files_to_copy:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(input_file, output_file)
                self.logger.info(f"Copied file: {relative_path}")
            except (OSError, IOError) as e:
                self.logger.error(f"Copy failed: {relative_path}, {e}")

        self.logger.info("Folder conversion complete")

        return (success_count, fail_count, errors)

    def save_profile_data(self, name: str):
        """現在の設定をプロファイルに保存する.

        Save current settings to profile.

        Parameters
        ----------
        name : str
            プロファイル名
        """
        data = {
            "filters": [to_relative_path(f) for f in self.enabled_filters],
            "exclude_patterns": self.exclude_patterns,
            "css_file": to_relative_path(self.css_file),
            "embed_css": self.embed_css,
            "output_format": self.output_format,
            "java_path": to_relative_path(self.java_path),
            "plantuml_jar": to_relative_path(self.plantuml_jar),
            "plantuml_use_server": self.plantuml_use_server,
            "plantuml_server_url": self.plantuml_server_url,
            "mermaid_mode": self.mermaid_mode,
        }
        save_profile(name, data)
        self.logger.info(f"Profile saved: {name}")

    def load_profile_data(self, name: str) -> bool:
        """プロファイルから設定を読み込む.

        Load settings from profile.

        Parameters
        ----------
        name : str
            プロファイル名

        Returns
        -------
        bool
            読み込みに成功した場合True
        """
        data = load_profile(name)
        if not data:
            self.logger.warning(f"Profile not found: {name}")
            return False

        self.enabled_filters = [
            from_relative_path(p) for p in data.get("filters", []) if p
        ]
        self.exclude_patterns = data.get("exclude_patterns", [])
        self.css_file = from_relative_path(data.get("css_file"))
        self.embed_css = data.get("embed_css", True)
        self.output_format = data.get("output_format", "html")
        self.java_path = from_relative_path(data.get("java_path"))
        self.plantuml_jar = from_relative_path(data.get("plantuml_jar"))
        self.plantuml_use_server = data.get("plantuml_use_server", False)
        self.plantuml_server_url = data.get("plantuml_server_url",
                                            "http://www.plantuml.com/plantuml")
        self.mermaid_mode = data.get("mermaid_mode", "mmdc")

        self.logger.info(f"Profile loaded: {name}")
        return True
