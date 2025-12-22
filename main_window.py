# -*- coding: utf-8 -*-
"""Pandoc GUI Application."""
import json
import logging
import platform
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from css_window import CSSWindow
from filter_window import FilterWindow
from i18n import I18n
from log_window import LogWindow

try:
    from importlib.metadata import PackageNotFoundError, version
    __version__ = version("pandoc-gui")
except PackageNotFoundError:
    __version__ = "1.0.0"  # フォールバック

PROFILE_DIR = Path("profiles")
PROFILE_DIR.mkdir(exist_ok=True)

SCRIPT_DIR = Path(__file__).parent


def to_relative_path(path: Path) -> str:
    """パスをスクリプトディレクトリ基準の相対パスに変換.

    Convert path to relative path based on script directory.

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
        rel_path = path.relative_to(SCRIPT_DIR.resolve())
        return str(rel_path)
    except ValueError:
        # スクリプトディレクトリ以下でない場合は絶対パスで保存
        return str(path)


def from_relative_path(path_str: str) -> Path:
    """相対パスをスクリプトディレクトリ基準で解決.

    Resolve relative path based on script directory.

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
    return (SCRIPT_DIR / path).resolve()


def save_profile(name: str, data: dict):
    """プロファイル保存/読み込み.

    Save/load profile.

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
    """プロファイル保存/読み込み.

    Save/load profile.

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
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_default_profile():
    """デフォルトプロファイルを初期化する.

    Initialize default profile.
    """
    default_data = {
        "filters": [],
        "css_file": None,
        "embed_css": True,
        "output_format": "html",
        "language": None,  # None = auto-detect
        "java_path": None,
        "plantuml_jar": None,
    }
    path = PROFILE_DIR / "default.json"
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)


class MainWindow(tk.Tk):
    """Pandoc GUIアプリケーションのメインクラス.

    Main class for Pandoc GUI application.
    """

    def __init__(self):
        """初期化.

        Initialize.
        """
        super().__init__()

        # デフォルトプロファイルを初期化
        init_default_profile()

        # 言語設定を読み込む
        profile_data = load_profile("default")
        lang = profile_data.get("language") if profile_data else None
        self.i18n = I18n(lang)

        self.title(self.i18n.t("app_title"))

        self.input_path = None
        self.output_path = None

        # ダイアログ用の前回選択パス
        self.last_input_dir = Path(__file__).parent
        self.last_output_dir = Path(__file__).parent
        self.last_filter_dir = Path(__file__).parent

        # Java/PlantUML設定
        self.java_path = None
        self.plantuml_jar = None

        # -------------------------
        # ログ設定
        # -------------------------
        self.logger = logging.getLogger("pandoc_gui")
        self.logger.setLevel(logging.INFO)

        # ローテーション付きファイルログ
        file_handler = RotatingFileHandler("pandoc_gui.log",
                                           maxBytes=1024 * 1024,
                                           backupCount=5,
                                           encoding="utf-8")
        # ロガーにハンドラーを追加
        self.logger.addHandler(file_handler)

        # ログウィンドウ（フローティング）
        self.log_window = LogWindow(self)

        # フィルター管理ウィンドウ用の内部保持
        self.enabled_filters = []
        self.css_file = None
        self.embed_css = True
        self.output_format = "html"

        # 言語選択メニュー
        self._create_menu()

        # ログウィンドウトグルボタン
        log_toggle_frame = tk.Frame(self, padx=5, pady=5)
        log_toggle_frame.pack(fill=tk.X, padx=5, pady=5)
        self.log_button = tk.Button(log_toggle_frame,
                                    text=self.i18n.t("log_window_show"),
                                    command=self.toggle_log_window)
        self.log_button.pack(fill=tk.X)

        # フィルター管理ボタン
        filter_button_frame = tk.Frame(self, padx=5, pady=5)
        filter_button_frame.pack(fill=tk.X, padx=5, pady=5)
        self.filter_button = tk.Button(filter_button_frame,
                                       text=self.i18n.t("filter_management"),
                                       command=self.open_filter_window)
        self.filter_button.pack(fill=tk.X)

        # CSS設定ボタン
        css_button_frame = tk.Frame(self, padx=5, pady=5)
        css_button_frame.pack(fill=tk.X, padx=5, pady=5)
        self.css_button = tk.Button(css_button_frame,
                                    text=self.i18n.t("css_settings"),
                                    command=self.open_css_window)
        self.css_button.pack(fill=tk.X)

        # CSS設定表示ラベル
        self.css_info_label = tk.Label(self,
                                       text=self.i18n.t("css_info_not_set"),
                                       fg="gray",
                                       font=("Arial", 9))
        self.css_info_label.pack(fill=tk.X, padx=5, pady=2)

        # -------------------------
        # Java/PlantUML設定
        # -------------------------
        plantuml_frame = tk.LabelFrame(self,
                                       text=self.i18n.t("plantuml_settings"),
                                       padx=5,
                                       pady=5)
        plantuml_frame.pack(fill=tk.X, padx=5, pady=5)

        # Java Path
        java_frame = tk.Frame(plantuml_frame)
        java_frame.pack(fill=tk.X, pady=2)
        tk.Label(java_frame,
                 text=self.i18n.t("java_path"),
                 width=12,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.java_path_var = tk.StringVar()
        tk.Entry(java_frame, textvariable=self.java_path_var,
                 width=40).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        tk.Button(java_frame,
                  text="...",
                  command=self.select_java_path,
                  width=3).pack(side=tk.LEFT, padx=2)

        # PlantUML JAR
        jar_frame = tk.Frame(plantuml_frame)
        jar_frame.pack(fill=tk.X, pady=2)
        tk.Label(jar_frame,
                 text=self.i18n.t("plantuml_jar"),
                 width=12,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.plantuml_jar_var = tk.StringVar()
        tk.Entry(jar_frame, textvariable=self.plantuml_jar_var,
                 width=40).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        tk.Button(jar_frame,
                  text="...",
                  command=self.select_plantuml_jar,
                  width=3).pack(side=tk.LEFT, padx=2)

        # -------------------------
        # 入出力
        # -------------------------
        io_frame = tk.LabelFrame(self,
                                 text=self.i18n.t("input_output"),
                                 padx=5,
                                 pady=5)
        io_frame.pack(fill=tk.X, padx=5, pady=5)

        self.input_type_var = tk.StringVar(value="file")
        tk.Radiobutton(io_frame,
                       text=self.i18n.t("file"),
                       variable=self.input_type_var,
                       value="file").pack(anchor=tk.W)
        tk.Radiobutton(io_frame,
                       text=self.i18n.t("folder"),
                       variable=self.input_type_var,
                       value="folder").pack(anchor=tk.W)
        tk.Button(io_frame,
                  text=self.i18n.t("select_input"),
                  command=self.select_input).pack(fill=tk.X, pady=2)
        tk.Button(io_frame,
                  text=self.i18n.t("select_output"),
                  command=self.select_output).pack(fill=tk.X, pady=2)

        # 出力形式
        format_sub_frame = tk.Frame(io_frame)
        format_sub_frame.pack(fill=tk.X, pady=5)
        tk.Label(format_sub_frame,
                 text=self.i18n.t("output_format")).pack(side=tk.LEFT, padx=5)

        self.format_var = tk.StringVar(value="html")
        format_options = ["html", "pdf", "docx", "epub"]
        self.format_combo = ttk.Combobox(format_sub_frame,
                                         textvariable=self.format_var,
                                         values=format_options,
                                         state="readonly",
                                         width=10)
        self.format_combo.pack(side=tk.LEFT, padx=5)
        self.format_combo.bind("<<ComboboxSelected>>",
                               lambda e: self._on_format_changed())

        # -------------------------
        # プロファイル
        # -------------------------
        profile_frame = tk.LabelFrame(self,
                                      text=self.i18n.t("profile"),
                                      padx=5,
                                      pady=5)
        profile_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(profile_frame,
                 text=self.i18n.t("profile_name")).pack(side=tk.LEFT, padx=5)
        self.profile_var = tk.StringVar(value="default")
        tk.Entry(profile_frame, textvariable=self.profile_var,
                 width=15).pack(side=tk.LEFT, padx=5)

        tk.Button(profile_frame,
                  text=self.i18n.t("save"),
                  command=self.save_profile).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_frame,
                  text=self.i18n.t("load"),
                  command=self.load_profile).pack(side=tk.LEFT, padx=2)

        # -------------------------
        # 実行
        # -------------------------
        exec_frame = tk.Frame(self, padx=5, pady=5)
        exec_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(exec_frame,
                  text=self.i18n.t("run_conversion"),
                  command=self.run_pandoc,
                  bg="#4CAF50",
                  fg="white",
                  font=("Arial", 10, "bold")).pack(fill=tk.X)

        # プロセス管理
        self.current_proc = None
        self.proc_lock = threading.Lock()

        # ウィンドウクローズで子プロセスを終了させる
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_java_path(self):
        """Javaの実行ファイルを選択する.

        Select Java executable file.
        """
        file = filedialog.askopenfilename(title=self.i18n.t("select_java_path"),
                                          filetypes=[("Executable files",
                                                      "*.exe"),
                                                     ("All files", "*.*")],
                                          initialdir=str(self.last_input_dir))
        if file:
            self.java_path_var.set(file)
            self.java_path = Path(file)
            self.logger.info(self.i18n.t("java_path_selected", path=file))

    def select_plantuml_jar(self):
        """PlantUML JARファイルを選択する.

        Select PlantUML JAR file.
        """
        file = filedialog.askopenfilename(
            title=self.i18n.t("select_plantuml_jar"),
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")],
            initialdir=str(self.last_input_dir))
        if file:
            self.plantuml_jar_var.set(file)
            self.plantuml_jar = Path(file)
            self.logger.info(self.i18n.t("plantuml_jar_selected", path=file))

    def _create_menu(self):
        """メニューバーを作成する.

        Create menu bar.
        """
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # 言語メニュー
        language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("language"), menu=language_menu)

        available_languages = self.i18n.get_available_languages()
        for lang in available_languages:
            language_menu.add_command(label=lang["name"],
                                      command=lambda lang_code=lang["code"]:
                                      (self.change_language(lang_code)))

        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.i18n.t("help"), menu=help_menu)
        help_menu.add_command(label=self.i18n.t("about"),
                              command=self.show_about)

    def change_language(self, lang_code):
        """言語を変更してプロファイルに保存.

        Change language and save to profile.

        Parameters
        ----------
        lang_code : str
            言語コード (Language code)
        """
        # プロファイルに保存
        profile_data = load_profile("default") or {}
        profile_data["language"] = lang_code
        save_profile("default", profile_data)

        # 再起動が必要であることを通知
        messagebox.showinfo(self.i18n.t("language_settings"),
                            self.i18n.t("restart_required"))

    def show_about(self):
        """バージョン情報を表示する.

        Show version information.
        """
        about_text = "\n".join([
            "Pandoc GUI", f"Version: {__version__}", "",
            self.i18n.t("about_description"), "", "© 2025"
        ])
        messagebox.showinfo(self.i18n.t("about"), about_text)

    def toggle_log_window(self):
        """ログウィンドウの表示・非表示を切り替える.

        Toggle log window visibility.
        """
        if self.log_window and self.log_window.winfo_viewable():
            self.log_window.withdraw()
            self.log_button.config(text=self.i18n.t("log_window_show"))
            return
        self.log_window.deiconify()
        self.log_button.config(text=self.i18n.t("log_window_hide"))

    def select_input(self):
        """入力を選択する(ファイルまたはフォルダ).

        Select input (file or folder).
        """
        if self.input_type_var.get() == "file":
            file = filedialog.askopenfilename(
                filetypes=[(self.i18n.t("markdown_files"), "*.md"),
                           (self.i18n.t("html_files"), "*.html;*.htm"),
                           (self.i18n.t("latex_files"), "*.tex"),
                           (self.i18n.t("rst_files"), "*.rst"),
                           (self.i18n.t("org_files"), "*.org"),
                           (self.i18n.t("textile_files"), "*.textile"),
                           (self.i18n.t("docbook_files"), "*.xml"),
                           (self.i18n.t("epub_files"), "*.epub"),
                           (self.i18n.t("word_files"), "*.docx"),
                           (self.i18n.t("all_files"), "*.*")],
                initialdir=str(self.last_input_dir))
            if not file:
                return
            self.input_path = Path(file)
            self.last_input_dir = self.input_path.parent
            self.logger.info(self.i18n.t("input_file", path=self.input_path))
            return

        folder = filedialog.askdirectory(initialdir=str(self.last_input_dir))
        if not folder:
            return
        self.input_path = Path(folder)
        self.last_input_dir = self.input_path
        self.logger.info(self.i18n.t("input_folder", path=self.input_path))

    def select_output_dir(self):
        """出力先フォルダを選択する.

        Select output folder.
        """
        folder = filedialog.askdirectory(initialdir=str(self.last_output_dir))
        if not folder:
            return
        self.output_path = Path(folder)
        self.last_output_dir = self.output_path
        self.logger.info(self.i18n.t("output_folder", path=self.output_path))

    def select_output(self):
        """出力先を選択する（入力形式に応じて動的に変更）.

        Select output destination (dynamically changes according to input type).
        """
        if self.input_type_var.get() == "file":
            # 入力がファイルの場合は出力ファイルを選択
            file = filedialog.asksaveasfilename(
                initialdir=str(self.last_output_dir),
                defaultextension=f".{self.output_format}",
                filetypes=[(f"{self.output_format.upper()}ファイル",
                            f"*.{self.output_format}"), ("すべてのファイル", "*.*")])
            if not file:
                return
            self.output_path = Path(file)
            self.last_output_dir = self.output_path.parent
            self.logger.info(self.i18n.t("output_file", path=self.output_path))
        else:
            # 入力がフォルダの場合は出力フォルダを選択
            folder = filedialog.askdirectory(
                initialdir=str(self.last_output_dir))
            if not folder:
                return
            self.output_path = Path(folder)
            self.last_output_dir = self.output_path
            self.logger.info(self.i18n.t("output_folder",
                                         path=self.output_path))

    def toggle_filter_window(self):
        """フィルター管理ウィンドウを開く.

        Open filter management window.
        """
        self.open_filter_window()

    def open_filter_window(self):
        """フィルター管理ウィンドウをモーダルで開いて結果を取得する.

        Open filter management window as modal and get results.
        """
        filter_window = FilterWindow(self)
        filter_window.set_filters(self.enabled_filters)
        result = filter_window.show_modal()

        if result is not None:
            self.enabled_filters = result
            self.logger.info(self.i18n.t("filter_settings_updated"))

    def open_css_window(self):
        """CSS設定ウィンドウをモーダルで開いて結果を取得する.

        Open CSS settings window as modal and get results.
        """
        css_window = CSSWindow(self)
        css_window.set_css_config(self.css_file, self.embed_css)
        result = css_window.show_modal()

        if result is not None:
            self.css_file = result["css_file"]
            self.embed_css = result["embed_mode"]
            self._update_css_info_label()
            self.logger.info(self.i18n.t("css_settings_updated"))

    def _update_css_info_label(self):
        """CSS設定情報ラベルを更新する.

        Update CSS settings information label.
        """
        if not self.css_file:
            self.css_info_label.config(text=self.i18n.t("css_info_not_set"),
                                       fg="gray")
            return

        mode_text = self.i18n.t(
            "css_mode_embed") if self.embed_css else self.i18n.t(
                "css_mode_external")
        self.css_info_label.config(text=self.i18n.t("css_info_set",
                                                    filename=self.css_file.name,
                                                    mode=mode_text),
                                   fg="black")

    def _on_format_changed(self):
        """出力形式が変更されたときの処理.

        Process when output format is changed.
        """
        self.output_format = self.format_var.get()
        # DOCXはCSS非対応なので、CSS設定ボタンを非活性にする
        if self.output_format == "docx":
            self.css_button.config(state=tk.DISABLED)
            self.css_info_label.config(fg="gray")
        else:
            self.css_button.config(state=tk.NORMAL)
            if self.css_file:
                self.css_info_label.config(fg="black")

    def show_filter_window(self):
        """フィルター管理ウィンドウを表示する.

        Show filter management window.
        """
        self.open_filter_window()

    def save_profile(self):
        """プロファイルを保存する.

        Save profile.
        """
        data = {
            "filters": [to_relative_path(f) for f in self.enabled_filters],
            "css_file": to_relative_path(self.css_file),
            "embed_css": self.embed_css,
            "output_format": self.output_format,
            "java_path": to_relative_path(self.java_path),
            "plantuml_jar": to_relative_path(self.plantuml_jar),
        }
        save_profile(self.profile_var.get(), data)
        self.logger.info(
            self.i18n.t("profile_saved", name=self.profile_var.get()))

    def load_profile(self):
        """プロファイルを読み込む.

        Load profile.
        """
        data = load_profile(self.profile_var.get())
        if not data:
            self.logger.warning(self.i18n.t("profile_not_found"))
            return

        self.enabled_filters = [
            from_relative_path(p) for p in data.get("filters", []) if p
        ]
        self.css_file = from_relative_path(data.get("css_file"))
        self.embed_css = data.get("embed_css", True)
        self.output_format = data.get("output_format", "html")
        self.format_var.set(self.output_format)

        # Java/PlantUML設定を読み込む
        self.java_path = from_relative_path(data.get("java_path"))
        self.plantuml_jar = from_relative_path(data.get("plantuml_jar"))
        if self.java_path:
            self.java_path_var.set(str(self.java_path))
        else:
            self.java_path_var.set("")
        if self.plantuml_jar:
            self.plantuml_jar_var.set(str(self.plantuml_jar))
        else:
            self.plantuml_jar_var.set("")

        self._update_css_info_label()
        self._on_format_changed()

        self.logger.info(
            self.i18n.t("profile_loaded", name=self.profile_var.get()))

    def _create_metadata_file(self, input_file):
        """Java/PlantUML設定用の一時メタデータファイルを作成する.

        Create temporary metadata file for Java/PlantUML settings.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス (Input file path)

        Returns
        -------
        Path or None
            一時メタデータファイルのパス、設定が不要な場合はNone
            (Path to temporary metadata file, or None if not needed)
        """
        # Java/PlantUML設定が両方未設定の場合は何もしない
        java_path_str = self.java_path_var.get().strip()
        plantuml_jar_str = self.plantuml_jar_var.get().strip()

        if not java_path_str and not plantuml_jar_str:
            return None

        # 一時ファイルを作成
        temp_fd, temp_path = tempfile.mkstemp(suffix='.md', text=True)
        temp_file = Path(temp_path)

        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                # YAMLメタデータを書き込む
                f.write("---\n")
                if java_path_str:
                    # Windowsパスのバックスラッシュをエスケープ
                    escaped_path = java_path_str.replace('\\', '\\\\')
                    f.write(f"java_path: \"{escaped_path}\"\n")
                if plantuml_jar_str:
                    escaped_path = plantuml_jar_str.replace('\\', '\\\\')
                    f.write(f"plantuml_jar: \"{escaped_path}\"\n")
                f.write("---\n\n")

                # 元のファイル内容を追記
                with open(input_file, 'r', encoding='utf-8') as input_f:
                    content = input_f.read()
                    # 元のファイルに既にYAMLメタデータがある場合は削除
                    if content.startswith('---\n'):
                        parts = content.split('---\n', 2)
                        if len(parts) >= 3:
                            content = parts[2]
                    f.write(content)

            self.logger.info(
                self.i18n.t("temp_metadata_created", path=temp_file))
            return temp_file

        except (OSError, IOError) as e:
            self.logger.error(self.i18n.t("temp_metadata_failed", error=str(e)))
            try:
                temp_file.unlink()
            except (OSError, IOError):
                pass
            return None

    def run_pandoc(self):
        """Pandocを実行する.

        Execute Pandoc.
        """
        if not self.input_path or not self.output_path:
            self.logger.error(self.i18n.t("error_no_input_output"))
            return

        # 出力形式に応じた拡張子マップ
        format_ext_map = {
            "html": ".html",
            "pdf": ".pdf",
            "docx": ".docx",
            "epub": ".epub",
        }
        ext = format_ext_map.get(self.output_format, ".html")

        if self.input_path.is_file():
            # 入力がファイルの場合、output_pathがファイルかフォルダかで処理を分ける
            if self.output_path.suffix:  # 拡張子がある=ファイルとして指定された
                output_file = self.output_path
            else:  # フォルダとして指定された
                output_file = self.output_path / (self.input_path.stem + ext)
            self._run_single_file_conversion(self.input_path, output_file)
        else:
            # フォルダ選択の場合
            self._run_folder_conversion(self.input_path, self.output_path, ext)

    def _run_single_file_conversion(self, input_file, output_file):
        """単一ファイルの変換を実行する.

        Execute conversion for a single file.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス (Input file path)
        output_file : Path
            出力ファイルパス (Output file path)
        """
        # Java/PlantUML設定がある場合は一時メタデータファイルを作成
        temp_metadata_file = self._create_metadata_file(input_file)
        actual_input = temp_metadata_file if temp_metadata_file else input_file

        cmd = ["pandoc", str(actual_input), "-o", str(output_file)]

        for f in self.enabled_filters:
            cmd.extend(["--lua-filter", str(f)])

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

        self.logger.info(self.i18n.t("command_execution", cmd=" ".join(cmd)))

        # 長時間処理でもUIをブロックしないようスレッドで実行
        threading.Thread(target=self._run_pandoc_thread,
                         args=(cmd, output_file, temp_metadata_file),
                         daemon=True).start()

    def _run_folder_conversion(self, input_folder, output_folder, ext):
        """フォルダ内のファイルを一括変換する.

        Convert all files in a folder.

        Parameters
        ----------
        input_folder : Path
            入力フォルダパス (Input folder path)
        output_folder : Path
            出力フォルダパス (Output folder path)
        ext : str
            出力ファイルの拡張子 (Output file extension)
        """
        # 変換対象の拡張子
        convertible_extensions = {
            ".md", ".markdown", ".html", ".htm", ".tex", ".rst", ".org",
            ".textile", ".xml", ".epub", ".docx"
        }

        # 出力フォルダが存在しない場合は作成
        output_folder.mkdir(parents=True, exist_ok=True)

        # 入力フォルダ内の全ファイルを走査
        for input_file in input_folder.rglob("*"):
            if input_file.is_file():
                # 入力フォルダからの相対パスを取得
                relative_path = input_file.relative_to(input_folder)

                if input_file.suffix.lower() in convertible_extensions:
                    # 変換対象ファイル
                    output_file = output_folder / relative_path.parent / (
                        input_file.stem + ext)
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    self.logger.info(
                        self.i18n.t(
                            "converting_file",
                            input=str(relative_path),
                            output=str(output_file.relative_to(output_folder))))
                    self._run_single_file_conversion(input_file, output_file)
                else:
                    # 変換対象外ファイル（画像など）はコピー
                    output_file = output_folder / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    try:
                        shutil.copy2(input_file, output_file)
                        self.logger.info(
                            self.i18n.t("copied_file", path=str(relative_path)))
                    except (OSError, IOError) as e:
                        self.logger.error(
                            self.i18n.t("copy_failed",
                                        path=str(relative_path),
                                        error=str(e)))

        self.logger.info(self.i18n.t("folder_conversion_complete"))

    def _run_pandoc_thread(self, cmd, output_file, temp_metadata_file=None):
        """バックグラウンドで pandoc を実行し、ログ出力を行う.

        Execute pandoc in background and output logs.

        Parameters
        ----------
        cmd : list
            実行するコマンド (Command to execute)
        output_file : Path
            出力ファイルパス (Output file path)
        temp_metadata_file : Path, optional
            一時メタデータファイルのパス (Path to temporary metadata file)
        """
        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    encoding="utf-8",
                                    errors="replace")

            with self.proc_lock:
                self.current_proc = proc

            stdout_text, stderr_text = proc.communicate()

            with self.proc_lock:
                self.current_proc = None

            if proc.returncode == 0:
                self.logger.info(
                    self.i18n.t("conversion_success", path=output_file))
                if stdout_text.strip():
                    self.logger.info("STDOUT:\n%s", stdout_text)
            else:
                self.logger.error(
                    self.i18n.t("conversion_failed", code=proc.returncode))
                if stderr_text.strip():
                    self.logger.error("STDERR:\n%s", stderr_text)
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            self.logger.exception(self.i18n.t("pandoc_execution_error",
                                              error=e))
        finally:
            # 一時メタデータファイルを削除
            if temp_metadata_file and temp_metadata_file.exists():
                try:
                    temp_metadata_file.unlink()
                    self.logger.info(
                        self.i18n.t("temp_metadata_deleted",
                                    path=temp_metadata_file))
                except (OSError, IOError) as e:
                    self.logger.warning(
                        self.i18n.t("temp_metadata_delete_failed",
                                    path=temp_metadata_file,
                                    error=str(e)))

    def on_close(self):
        """アプリ終了時に実行中プロセスを終了させてからウィンドウを破棄する.

        Terminate running processes and destroy window when closing the
        application.
        """
        self.logger.info(self.i18n.t("app_closing"))
        proc = None
        with self.proc_lock:
            proc = self.current_proc

        if not proc or proc.poll() is not None:
            # プロセスがないか、すでに終了している
            self._cleanup_and_close()
            return

        self.logger.info("子プロセスを終了します (pid=%s)", proc.pid)
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.logger.warning("子プロセスが終了しないため強制終了します")
                try:
                    proc.kill()
                except (ProcessLookupError, PermissionError, OSError) as e:
                    self.logger.exception("proc.kill に失敗: %s", e)
                # Windows ではプロセスツリーを強制終了(フォールバック)
                if platform.system() == "Windows":
                    try:
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID",
                             str(proc.pid)],
                            capture_output=True,
                            text=True,
                            check=False  # taskkill の失敗を無視
                        )
                    except (FileNotFoundError, OSError) as e:
                        self.logger.exception("taskkill に失敗しました: %s", e)
        except (OSError, ValueError, AttributeError) as e:
            self.logger.exception("子プロセスの終了中にエラーが発生しました: %s", e)

        self._cleanup_and_close()

    def _cleanup_and_close(self):
        """ウィンドウをクリーンアップして閉じる.

        Clean up and close window.
        """
        # ログウィンドウを閉じる
        if self.log_window:
            try:
                self.log_window.destroy()
            except (tk.TclError, AttributeError) as e:
                self.logger.warning("ログウィンドウの破棄に失敗しました: %s", e)

        # メインウィンドウを閉じる
        self.destroy()


# -------------------------
# 起動
# -------------------------
if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
