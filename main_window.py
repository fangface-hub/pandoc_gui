# -*- coding: utf-8 -*-
"""Pandoc GUI Application."""
import argparse
import json
import logging
import os
import platform
import shutil
import sys
import threading
import tkinter as tk
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from __version__ import __version__
from css_window import CSSWindow
from exclude_window import ExcludeWindow
from filter_window import FilterWindow
from i18n import I18n
from log_window import LogWindow
from pandoc_service import (PandocService, check_pandoc_installed, get_app_dir,
                            get_data_dir, init_default_profile, load_profile,
                            save_profile)
from subprocessex import terminate_process

# Windowsでのプロセス管理用フラグ
if platform.system() == "Windows":
    CREATE_NO_WINDOW = 0x08000000
    CREATE_NEW_PROCESS_GROUP = 0x00000200
else:
    CREATE_NO_WINDOW = 0
    CREATE_NEW_PROCESS_GROUP = 0

# PyInstallerビルド時のパス解決
SCRIPT_DIR = get_app_dir()

# データディレクトリ（プラットフォームごとに適切な場所を使用）
DATA_DIR = get_data_dir()


def _init_data_folders():
    """初回起動時にDATA_DIRにフォルダを複製する.

    Copy folders to DATA_DIR on first launch.

    フィルタはアップデート時に上書き、それ以外は初回のみコピー。
    Filters are overwritten on updates, others are copied only on first launch.
    """
    # profiles, stylesheets は初回のみコピー（ユーザーカスタマイズを保護）
    folders_to_copy_once = ["profiles", "stylesheets"]

    for folder_name in folders_to_copy_once:
        src_folder = SCRIPT_DIR / folder_name
        dest_folder = DATA_DIR / folder_name

        # フォルダが存在しない場合のみコピー
        if src_folder.exists() and not dest_folder.exists():
            shutil.copytree(src_folder, dest_folder)

    # filters は常に上書き（アップデート時に最新版に更新）
    filters_src = SCRIPT_DIR / "filters"
    filters_dest = DATA_DIR / "filters"

    if not filters_src.exists():
        return
    # DATA_DIR/filters が存在しない場合は丸ごとコピー
    if not filters_dest.exists():
        shutil.copytree(filters_src, filters_dest)
        return
    # DATA_DIR/filters が存在する場合は、SCRIPT_DIRにある同名ファイルのみ上書き
    for filter_file in filters_src.glob("*"):
        if filter_file.is_file():
            dest_file = filters_dest / filter_file.name
            shutil.copy2(filter_file, dest_file)


class MainWindow(tk.Tk):
    """Pandoc GUIアプリケーションのメインクラス.

    Main class for Pandoc GUI application.
    """

    def __init__(self):
        """初期化.

        Initialize.
        """
        super().__init__()

        # 初回起動時にDATA_DIRにフォルダを複製
        _init_data_folders()

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
        documents_dir = Path(os.path.expanduser("~")) / "Documents"
        self.last_input_dir = documents_dir
        self.last_output_dir = documents_dir
        self.last_filter_dir = DATA_DIR / "filters"

        # -------------------------
        # ログ設定
        # -------------------------
        self.logger = logging.getLogger("pandoc_gui")
        self.logger.setLevel(logging.INFO)

        # ログディレクトリの作成（DATA_DIRの下にlogサブフォルダ）
        log_dir = DATA_DIR / "log"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "pandoc_gui.log"

        # ローテーション付きファイルログ
        file_handler = RotatingFileHandler(str(log_file),
                                           maxBytes=1024 * 1024,
                                           backupCount=5,
                                           encoding="utf-8")
        # ロガーにハンドラーを追加
        self.logger.addHandler(file_handler)

        # ログウィンドウ（フローティング）
        self.log_window = LogWindow(self)

        # PandocServiceのインスタンスを作成
        self.pandoc_service = PandocService(self.logger)

        # pandocのインストール状況をチェック
        if not check_pandoc_installed():
            self.logger.warning("Pandoc is not installed or not in PATH")
            # 警告メッセージを表示（afterで少し遅延させてUI構築後に表示）
            self.after(
                100, lambda: messagebox.showwarning(
                    self.i18n.t("warning"),
                    self.i18n.t("pandoc_not_installed_warning")))

        # 環境変数の初期値をログ出力
        env_java = os.getenv("JAVA_PATH") or ""
        env_plantuml = os.getenv("PLANTUML_JAR") or ""
        self.logger.info(self.i18n.t("startup_java_path_env", path=env_java))
        self.logger.info(
            self.i18n.t("startup_plantuml_jar_env", path=env_plantuml))

        # 言語選択メニュー
        self._create_menu()

        # ログウィンドウトグルボタン
        log_toggle_frame = tk.Frame(self, padx=5, pady=2)
        log_toggle_frame.pack(fill=tk.X, padx=5, pady=2)
        self.log_button = tk.Button(log_toggle_frame,
                                    text=self.i18n.t("log_window_show"),
                                    command=self.toggle_log_window)
        self.log_button.pack(fill=tk.X)

        # フィルター管理ボタン
        filter_button_frame = tk.Frame(self, padx=5, pady=2)
        filter_button_frame.pack(fill=tk.X, padx=5, pady=2)
        self.filter_button = tk.Button(filter_button_frame,
                                       text=self.i18n.t("filter_management"),
                                       command=self.open_filter_window)
        self.filter_button.pack(fill=tk.X)

        # CSS設定ボタン
        css_button_frame = tk.Frame(self, padx=5, pady=2)
        css_button_frame.pack(fill=tk.X, padx=5, pady=2)
        self.css_button = tk.Button(css_button_frame,
                                    text=self.i18n.t("css_settings"),
                                    command=self.open_css_window)
        self.css_button.pack(fill=tk.X)

        # CSS設定表示ラベル
        self.css_info_label = tk.Label(self,
                                       text=self.i18n.t("css_info_not_set"),
                                       fg="gray",
                                       font=("Arial", 9))
        self.css_info_label.pack(fill=tk.X, padx=5, pady=1)

        # 除外パターン管理ボタン
        exclude_button_frame = tk.Frame(self, padx=5, pady=2)
        exclude_button_frame.pack(fill=tk.X, padx=5, pady=2)
        self.exclude_button = tk.Button(exclude_button_frame,
                                        text=self.i18n.t("exclude_management"),
                                        command=self.open_exclude_window)
        self.exclude_button.pack(fill=tk.X)

        # -------------------------
        # Java/PlantUML設定
        # -------------------------
        plantuml_frame = tk.LabelFrame(self,
                                       text=self.i18n.t("plantuml_settings"),
                                       padx=5,
                                       pady=3)
        plantuml_frame.pack(fill=tk.X, padx=5, pady=3)

        # PlantUML実行方法選択
        method_frame = tk.Frame(plantuml_frame)
        method_frame.pack(fill=tk.X, pady=2)
        tk.Label(method_frame,
                 text=self.i18n.t("plantuml_method"),
                 width=15,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.plantuml_method_var = tk.StringVar(value="jar")
        tk.Radiobutton(method_frame,
                       text=self.i18n.t("plantuml_jar_method"),
                       variable=self.plantuml_method_var,
                       value="jar",
                       command=self._on_plantuml_method_changed).pack(
                           side=tk.LEFT, padx=10)
        tk.Radiobutton(method_frame,
                       text=self.i18n.t("plantuml_server_method"),
                       variable=self.plantuml_method_var,
                       value="server",
                       command=self._on_plantuml_method_changed).pack(
                           side=tk.LEFT, padx=10)

        # Java Path
        java_frame = tk.Frame(plantuml_frame)
        java_frame.pack(fill=tk.X, pady=2)
        tk.Label(java_frame,
                 text=self.i18n.t("java_path"),
                 width=18,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.java_path_var = tk.StringVar()
        self.java_path_entry = tk.Entry(java_frame,
                                        textvariable=self.java_path_var,
                                        width=40)
        self.java_path_entry.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        self.java_path_button = tk.Button(java_frame,
                                          text="...",
                                          command=self.select_java_path,
                                          width=3)
        self.java_path_button.pack(side=tk.LEFT, padx=2)

        # PlantUML JAR
        jar_frame = tk.Frame(plantuml_frame)
        jar_frame.pack(fill=tk.X, pady=2)
        tk.Label(jar_frame,
                 text=self.i18n.t("plantuml_jar"),
                 width=18,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.plantuml_jar_var = tk.StringVar()
        self.plantuml_jar_entry = tk.Entry(jar_frame,
                                           textvariable=self.plantuml_jar_var,
                                           width=40)
        self.plantuml_jar_entry.pack(side=tk.LEFT,
                                     padx=2,
                                     fill=tk.X,
                                     expand=True)
        self.plantuml_jar_button = tk.Button(jar_frame,
                                             text="...",
                                             command=self.select_plantuml_jar,
                                             width=3)
        self.plantuml_jar_button.pack(side=tk.LEFT, padx=2)

        # PlantUML Server URL
        server_frame = tk.Frame(plantuml_frame)
        server_frame.pack(fill=tk.X, pady=2)
        tk.Label(server_frame,
                 text=self.i18n.t("plantuml_server_url"),
                 width=18,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.plantuml_server_url_var = tk.StringVar(
            value="http://www.plantuml.com/plantuml")
        self.plantuml_server_url_entry = tk.Entry(
            server_frame, textvariable=self.plantuml_server_url_var, width=40)
        self.plantuml_server_url_entry.pack(side=tk.LEFT,
                                            padx=2,
                                            fill=tk.X,
                                            expand=True)

        # -------------------------
        # Mermaid設定
        # -------------------------
        mermaid_frame = tk.LabelFrame(self,
                                      text=self.i18n.t("mermaid_settings"),
                                      padx=5,
                                      pady=3)
        mermaid_frame.pack(fill=tk.X, padx=5, pady=3)

        # Mermaid描画方法選択
        mermaid_method_frame = tk.Frame(mermaid_frame)
        mermaid_method_frame.pack(fill=tk.X, pady=2)
        tk.Label(mermaid_method_frame,
                 text=self.i18n.t("mermaid_method"),
                 width=15,
                 anchor=tk.W).pack(side=tk.LEFT, padx=2)
        self.mermaid_mode_var = tk.StringVar(value="browser")
        tk.Radiobutton(mermaid_method_frame,
                       text=self.i18n.t("mermaid_browser_method"),
                       variable=self.mermaid_mode_var,
                       value="browser").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mermaid_method_frame,
                       text=self.i18n.t("mermaid_mmdc_method"),
                       variable=self.mermaid_mode_var,
                       value="mmdc").pack(side=tk.LEFT, padx=10)

        # -------------------------
        # 入出力
        # -------------------------
        io_frame = tk.LabelFrame(self,
                                 text=self.i18n.t("input_output"),
                                 padx=5,
                                 pady=3)
        io_frame.pack(fill=tk.X, padx=5, pady=3)

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
        format_options = ["html", "pdf", "docx", "epub", "markdown"]
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
                                      pady=3)
        profile_frame.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(profile_frame,
                 text=self.i18n.t("profile_name")).pack(side=tk.LEFT, padx=5)
        self.profile_var = tk.StringVar(value="default")
        self.profile_combo = ttk.Combobox(profile_frame,
                                          textvariable=self.profile_var,
                                          values=self._get_available_profiles(),
                                          state="readonly",
                                          width=15)
        self.profile_combo.pack(side=tk.LEFT, padx=5)

        tk.Button(profile_frame,
                  text=self.i18n.t("add"),
                  command=self.add_new_profile).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_frame,
                  text=self.i18n.t("delete"),
                  command=self.delete_profile).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_frame,
                  text=self.i18n.t("save"),
                  command=self.save_profile).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_frame,
                  text=self.i18n.t("load"),
                  command=self.load_profile).pack(side=tk.LEFT, padx=2)
        tk.Button(profile_frame,
                  text=self.i18n.t("refresh"),
                  command=self._refresh_profile_list).pack(side=tk.LEFT, padx=2)

        # -------------------------
        # 実行
        # -------------------------
        exec_frame = tk.Frame(self, padx=5, pady=3)
        exec_frame.pack(fill=tk.X, padx=5, pady=3)
        self.run_button = tk.Button(exec_frame,
                                    text=self.i18n.t("run_conversion"),
                                    command=self.run_pandoc,
                                    bg="#4CAF50",
                                    fg="white",
                                    font=("Arial", 10, "bold"))
        self.run_button.pack(fill=tk.X)

        # ステータス表示
        self.status_label = tk.Label(exec_frame, text="", fg="#666")
        self.status_label.pack(fill=tk.X, pady=(5, 0))

        # プロセス管理
        self.current_proc = None
        self.proc_lock = threading.Lock()

        # ウィンドウクローズで子プロセスを終了させる
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # デフォルトプロファイルが存在する場合、起動時に自動ロード
        self._load_default_profile_on_startup()

    def _get_available_profiles(self):
        """利用可能なプロファイルのリストを取得する.

        Get list of available profiles.

        Returns
        -------
        list
            プロファイル名のリスト (List of profile names)
        """
        profiles_dir = DATA_DIR / "profiles"
        if not profiles_dir.exists():
            return ["default"]

        profile_files = list(profiles_dir.glob("*.json"))
        profile_names = [p.stem for p in profile_files]

        # defaultが含まれていない場合は追加
        if "default" not in profile_names:
            profile_names.insert(0, "default")

        return sorted(profile_names)

    def _refresh_profile_list(self):
        """プロファイルリストを更新する.

        Refresh profile list.
        """
        profiles = self._get_available_profiles()
        self.profile_combo.config(values=profiles)
        self.logger.info(self.i18n.t("profile_list_refreshed"))

    def add_new_profile(self):
        """新規プロファイルを作成する.

        Create a new profile.
        """
        # プロファイル名を入力
        new_profile_name = simpledialog.askstring(
            self.i18n.t("add_new_profile"), self.i18n.t("enter_profile_name"))

        if not new_profile_name:
            return

        # 無効な文字をチェック
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(c in new_profile_name for c in invalid_chars):
            messagebox.showerror(self.i18n.t("error"),
                                 self.i18n.t("invalid_profile_name"))
            return

        # 既存のプロファイルと重複チェック
        dest_file = DATA_DIR / "profiles" / f"{new_profile_name}.json"
        if dest_file.exists():
            messagebox.showerror(
                self.i18n.t("error"),
                self.i18n.t("profile_already_exists", name=new_profile_name))
            return

        # SCRIPT_DIR/profiles/default.json を読み込む
        src_file = SCRIPT_DIR / "profiles" / "default.json"
        if not src_file.exists():
            messagebox.showerror(self.i18n.t("error"),
                                 self.i18n.t("default_profile_not_found"))
            return

        try:
            # プロファイルディレクトリが存在しない場合は作成
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            # ファイルを複製
            with open(src_file, 'r', encoding='utf-8-sig') as f:
                profile_data = json.load(f)

            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)

            self.logger.info(
                self.i18n.t("profile_created", name=new_profile_name))

            # プロファイルリストを更新
            self._refresh_profile_list()

            # 新しいプロファイルを選択
            self.profile_var.set(new_profile_name)

            messagebox.showinfo(
                self.i18n.t("success"),
                self.i18n.t("profile_created", name=new_profile_name))

        except (OSError, ValueError) as e:
            self.logger.error(
                self.i18n.t("profile_creation_failed",
                            name=new_profile_name,
                            error=str(e)))
            messagebox.showerror(
                self.i18n.t("error"),
                self.i18n.t("profile_creation_failed",
                            name=new_profile_name,
                            error=str(e)))

    def delete_profile(self):
        """プロファイルを削除する.

        Delete a profile.
        """
        profile_name = self.profile_var.get()

        # defaultプロファイルは削除不可
        if profile_name == "default":
            messagebox.showerror(self.i18n.t("error"),
                                 self.i18n.t("cannot_delete_default_profile"))
            return

        # 削除確認
        if not messagebox.askyesno(
                self.i18n.t("confirm_delete"),
                self.i18n.t("confirm_delete_profile", name=profile_name)):
            return

        # プロファイルファイルのパス
        profile_file = DATA_DIR / "profiles" / f"{profile_name}.json"

        try:
            if profile_file.exists():
                profile_file.unlink()
                self.logger.info(
                    self.i18n.t("profile_deleted", name=profile_name))

                # プロファイルリストを更新
                self._refresh_profile_list()

                # defaultプロファイルを選択
                self.profile_var.set("default")

                messagebox.showinfo(
                    self.i18n.t("success"),
                    self.i18n.t("profile_deleted", name=profile_name))
            else:
                messagebox.showerror(self.i18n.t("error"),
                                     self.i18n.t("profile_not_found"))

        except OSError as e:
            self.logger.error(
                self.i18n.t("profile_deletion_failed",
                            name=profile_name,
                            error=str(e)))
            messagebox.showerror(
                self.i18n.t("error"),
                self.i18n.t("profile_deletion_failed",
                            name=profile_name,
                            error=str(e)))

    def _load_default_profile_on_startup(self):
        """起動時にデフォルトプロファイルを自動的にロードする.

        Automatically load default profile on startup.
        """
        # サービスにプロファイルをロード
        if not self.pandoc_service.load_profile_data("default"):
            return

        # 出力形式を読み込む
        self.format_var.set(self.pandoc_service.output_format)

        # Java/PlantUML設定を読み込む
        if self.pandoc_service.java_path:
            self.java_path_var.set(str(self.pandoc_service.java_path))
        else:
            self.java_path_var.set("")
        if self.pandoc_service.plantuml_jar:
            self.plantuml_jar_var.set(str(self.pandoc_service.plantuml_jar))
        else:
            self.plantuml_jar_var.set("")

        # PlantUMLサーバ設定を読み込む
        if hasattr(self.pandoc_service, 'plantuml_use_server'):
            method = ("server"
                      if self.pandoc_service.plantuml_use_server else "jar")
            self.plantuml_method_var.set(method)
        if hasattr(self.pandoc_service, 'plantuml_server_url'
                   ) and self.pandoc_service.plantuml_server_url:
            self.plantuml_server_url_var.set(
                self.pandoc_service.plantuml_server_url)

        # Mermaid設定を読み込む
        if hasattr(self.pandoc_service, 'mermaid_mode'):
            self.mermaid_mode_var.set(self.pandoc_service.mermaid_mode)

        # UIを更新
        self._on_plantuml_method_changed()
        self._update_css_info_label()
        self._on_format_changed()

        self.logger.info(self.i18n.t("profile_loaded", name="default"))

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
            self.pandoc_service.java_path = Path(file)
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
            self.pandoc_service.plantuml_jar = Path(file)
            self.logger.info(self.i18n.t("plantuml_jar_selected", path=file))

    def _on_plantuml_method_changed(self):
        """
        PlantUML実行方法が変更されたときの処理.

        Process when PlantUML execution method is changed.
        """
        is_jar = self.plantuml_method_var.get() == "jar"

        # JAR方式の場合はJavaとJARを有効化、サーバを無効化
        # If JAR method, enable Java and JAR, disable Server
        state_jar = tk.NORMAL if is_jar else tk.DISABLED
        state_server = tk.DISABLED if is_jar else tk.NORMAL

        self.java_path_entry.config(state=state_jar)
        self.java_path_button.config(state=state_jar)
        self.plantuml_jar_entry.config(state=state_jar)
        self.plantuml_jar_button.config(state=state_jar)
        self.plantuml_server_url_entry.config(state=state_server)

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
        help_menu.add_command(label=self.i18n.t("help"), command=self.open_help)
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
            # 入力ファイルが選択されていれば、その拡張子を変えたファイル名を初期表示
            initial_filename = ""
            if self.input_path and self.input_path.is_file():
                initial_filename = (self.input_path.stem +
                                    f".{self.output_format}")

            file = filedialog.asksaveasfilename(
                initialdir=str(self.last_output_dir),
                initialfile=initial_filename,
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
        filter_window.set_filters(self.pandoc_service.enabled_filters)
        result = filter_window.show_modal()

        if result is not None:
            self.pandoc_service.enabled_filters = result
            self.logger.info(self.i18n.t("filter_settings_updated"))

    def open_css_window(self):
        """CSS設定ウィンドウをモーダルで開いて結果を取得する.

        Open CSS settings window as modal and get results.
        """
        css_window = CSSWindow(self)
        css_window.set_css_config(self.pandoc_service.css_file,
                                  self.pandoc_service.embed_css)
        result = css_window.show_modal()

        if result is not None:
            self.pandoc_service.css_file = result["css_file"]
            self.pandoc_service.embed_css = result["embed_mode"]
            self._update_css_info_label()
            self.logger.info(self.i18n.t("css_settings_updated"))

    def open_exclude_window(self):
        """除外パターン管理ウィンドウを開く.

        Open exclude pattern management window.
        """

        def on_save(patterns):
            self.pandoc_service.exclude_patterns = patterns
            self.logger.info(self.i18n.t("exclude_patterns_updated"))

        ExcludeWindow(self, self.i18n, self.pandoc_service.exclude_patterns,
                      on_save)

    def open_help(self):
        """ヘルプファイルをブラウザで開く.

        Open help file in browser.
        """
        # 現在の言語設定に応じたヘルプファイルを決定
        # メソッド名を確認してください。以下のいずれかが正しい可能性があります:
        # - self.i18n.current_language (プロパティの場合)
        # - self.i18n.language (属性の場合)
        # - self.i18n.get_language() (異なるメソッド名の場合)
        lang_code = self.i18n.get_current_language()  # この行を修正
        help_file = f"help_{lang_code}.html"
        help_path = SCRIPT_DIR / "help" / help_file

        # ファイルが存在しない場合は英語版にフォールバック
        if not help_path.exists():
            help_file = "help_en.html"
            help_path = SCRIPT_DIR / "help" / help_file

        # それでも存在しない場合はエラーメッセージ
        if not help_path.exists():
            messagebox.showwarning(
                self.i18n.t("warning"),
                self.i18n.t("help_file_not_found", file=help_file))
            self.logger.warning("Help file not found: %s", help_path)
            return

        # ブラウザで開く
        try:
            webbrowser.open(help_path.as_uri())
            self.logger.info("Opened help file: %s", help_path)
        except (OSError, ValueError) as e:
            messagebox.showerror(self.i18n.t("error"),
                                 self.i18n.t("help_open_error", error=str(e)))
            self.logger.error("Failed to open help file: %s", e)

    def _update_css_info_label(self):
        """CSS設定情報ラベルを更新する.

        Update CSS settings information label.
        """
        if not self.pandoc_service.css_file:
            self.css_info_label.config(text=self.i18n.t("css_info_not_set"),
                                       fg="gray")
            return

        mode_text = self.i18n.t(
            "css_mode_embed") if self.pandoc_service.embed_css else self.i18n.t(
                "css_mode_external")
        self.css_info_label.config(text=self.i18n.t(
            "css_info_set",
            filename=self.pandoc_service.css_file.name,
            mode=mode_text),
                                   fg="black")

    def _set_converting_status(self, is_converting):
        """変換中のステータス表示を更新する.

        Update converting status display.

        Parameters
        ----------
        is_converting : bool
            変換中かどうか (Whether converting)
        """

        def update_ui():
            if is_converting:
                self.status_label.config(text=self.i18n.t("converting_status"),
                                         fg="#FF9800")
                self.run_button.config(state=tk.DISABLED)
            else:
                self.status_label.config(text="", fg="#666")
                self.run_button.config(state=tk.NORMAL)

        # メインスレッドでUI更新
        self.after(0, update_ui)

    def _on_format_changed(self):
        """出力形式が変更されたときの処理.

        Process when output format is changed.
        """
        self.pandoc_service.output_format = self.format_var.get()
        # DOCXはCSS非対応なので、CSS設定ボタンを非活性にする
        if self.pandoc_service.output_format == "docx":
            self.css_button.config(state=tk.DISABLED)
            self.css_info_label.config(fg="gray")
        else:
            self.css_button.config(state=tk.NORMAL)
            if self.pandoc_service.css_file:
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
        # PlantUML設定を反映
        self.pandoc_service.plantuml_use_server = (
            self.plantuml_method_var.get() == "server")
        self.pandoc_service.plantuml_server_url = (
            self.plantuml_server_url_var.get())

        # Mermaid設定を反映
        self.pandoc_service.mermaid_mode = self.mermaid_mode_var.get()

        self.pandoc_service.save_profile_data(self.profile_var.get())
        self.logger.info(
            self.i18n.t("profile_saved", name=self.profile_var.get()))
        # プロファイルリストを更新
        self._refresh_profile_list()

    def load_profile(self):
        """プロファイルを読み込む.

        Load profile.
        """
        if not self.pandoc_service.load_profile_data(self.profile_var.get()):
            self.logger.warning(self.i18n.t("profile_not_found"))
            return

        self.format_var.set(self.pandoc_service.output_format)

        # Java/PlantUML設定を読み込む
        if self.pandoc_service.java_path:
            self.java_path_var.set(str(self.pandoc_service.java_path))
        else:
            self.java_path_var.set("")
        if self.pandoc_service.plantuml_jar:
            self.plantuml_jar_var.set(str(self.pandoc_service.plantuml_jar))
        else:
            self.plantuml_jar_var.set("")

        # PlantUMLサーバ設定を読み込む
        if hasattr(self.pandoc_service, 'plantuml_use_server'):
            method = ("server"
                      if self.pandoc_service.plantuml_use_server else "jar")
            self.plantuml_method_var.set(method)
        if hasattr(self.pandoc_service, 'plantuml_server_url'
                   ) and self.pandoc_service.plantuml_server_url:
            self.plantuml_server_url_var.set(
                self.pandoc_service.plantuml_server_url)

        # Mermaid設定を読み込む
        if hasattr(self.pandoc_service, 'mermaid_mode'):
            self.mermaid_mode_var.set(self.pandoc_service.mermaid_mode)

        self._on_plantuml_method_changed()
        self._update_css_info_label()
        self._on_format_changed()

        self.logger.info(
            self.i18n.t("profile_loaded", name=self.profile_var.get()))

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
        ext = format_ext_map.get(self.pandoc_service.output_format, ".html")

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
        # ステータス表示と実行ボタンを無効化
        self._set_converting_status(True)

        # 長時間処理でもUIをブロックしないようスレッドで実行
        threading.Thread(target=self._run_pandoc_thread,
                         args=(input_file, output_file),
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
        # 別スレッドで順次変換を実行
        threading.Thread(target=self._run_folder_conversion_thread,
                         args=(input_folder, output_folder, ext),
                         daemon=True).start()

    def _run_folder_conversion_thread(self, input_folder, output_folder, ext):
        """フォルダ変換をバックグラウンドで順次実行する.

        Execute folder conversion sequentially in background.

        Parameters
        ----------
        input_folder : Path
            入力フォルダパス
        output_folder : Path
            出力フォルダパス
        ext : str
            出力ファイルの拡張子
        """
        try:
            # ステータス表示と実行ボタンを無効化
            self._set_converting_status(True)

            # 進捗コールバック
            def progress_callback(current, total, _relative_path):
                progress_msg = self.i18n.t("converting_progress",
                                           current=current,
                                           total=total)
                self.after(0,
                           lambda msg=progress_msg: self.status_label.config(
                               text=msg, fg="#FF9800"))

            # PandocServiceを使用して変換
            java_path_override = self.java_path_var.get().strip()
            plantuml_jar_override = self.plantuml_jar_var.get().strip()

            _success_count, _fail_count, _errors = (
                self.pandoc_service.convert_folder(input_folder, output_folder,
                                                   ext, java_path_override,
                                                   plantuml_jar_override,
                                                   progress_callback))

            self.logger.info(self.i18n.t("folder_conversion_complete"))

        finally:
            # ステータスをリセット
            self._set_converting_status(False)

    def _run_pandoc_thread(self, input_file, output_file):
        """バックグラウンドで pandoc を実行し、ログ出力を行う.

        Execute pandoc in background and output logs.

        Parameters
        ----------
        input_file : Path
            入力ファイルパス
        output_file : Path
            出力ファイルパス
        """
        try:
            self.logger.info(self.i18n.t("pandoc_process_starting"))

            # PandocServiceを使用して変換
            java_path_override = self.java_path_var.get().strip()
            plantuml_jar_override = self.plantuml_jar_var.get().strip()

            success, _stdout, _stderr, _returncode = (
                self.pandoc_service.convert_file(input_file, output_file,
                                                 java_path_override,
                                                 plantuml_jar_override))

            # 変換成功 & HTML出力 & browserモードの場合、サーバ起動してブラウザで開く
            if (success and output_file.suffix.lower() == '.html'
                    and self.pandoc_service.mermaid_mode == 'browser'):
                self._open_html_with_server(output_file)

        finally:
            # ステータスをリセット
            self._set_converting_status(False)

    def _open_html_with_server(self, html_file: Path):
        """HTMLファイルをローカルサーバ経由でブラウザで開く（Mermaid自動保存用）.

        Open HTML file in browser via local server for automatic Mermaid saving.

        Parameters
        ----------
        html_file : Path
            HTMLファイルのパス
        """
        try:
            # 出力ディレクトリでローカルサーバを起動
            output_dir = html_file.parent
            port = self.pandoc_service.start_local_server(output_dir)

            if port:
                # ブラウザで開く
                url = f"http://127.0.0.1:{port}/{html_file.name}"
                webbrowser.open(url)
                self.logger.info("Opened HTML in browser: %s", url)
            else:
                self.logger.warning("Failed to start local server")

        except (OSError, IOError, ValueError) as e:
            self.logger.error("Failed to open HTML with server: %s", e)

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

        self.logger.info(self.i18n.t("terminating_child_process", pid=proc.pid))

        # プラットフォーム依存のプロセス停止処理を共通関数に移管
        try:
            terminate_process(proc, logger=self.logger, timeout=5.0)
        except (OSError, IOError, ValueError) as e:
            self.logger.exception("terminate_process failed: %s", e)
            self.logger.exception(
                self.i18n.t("child_process_termination_error", error=str(e)))

        self._cleanup_and_close()

    def _cleanup_and_close(self):
        """ウィンドウをクリーンアップして閉じる.

        Clean up and close window.
        """
        # ローカルHTTPサーバを停止
        if self.pandoc_service.local_server:
            self.pandoc_service.stop_local_server()

        # ログウィンドウを閉じる
        if self.log_window:
            try:
                self.log_window.destroy()
            except (tk.TclError, AttributeError) as e:
                self.logger.warning(
                    self.i18n.t("log_window_destroy_failed", error=str(e)))

        # メインウィンドウを閉じる
        self.destroy()


def run_cli_mode(cli_args):
    """コマンドラインモードで実行.

    Run in command-line mode.

    Parameters
    ----------
    cli_args : argparse.Namespace
        コマンドライン引数

    Returns
    -------
    int
        終了コード (0: 成功, 1: 失敗)
    """
    # 初回起動時にDATA_DIRにフォルダを複製
    _init_data_folders()

    # デフォルトプロファイルを初期化
    init_default_profile()

    # プロファイルを読み込み
    profile_data = load_profile(cli_args.profile)
    if not profile_data:
        print(f"Error: Profile '{cli_args.profile}' not found.",
              file=sys.stderr)
        return 1

    # ロガーの設定
    logger = logging.getLogger("PandocGUI_CLI")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # pandocのチェック
    if not check_pandoc_installed():
        logger.error("Pandoc is not installed or not in PATH")
        return 1

    # PandocServiceのインスタンスを作成
    pandoc_service = PandocService(logger)

    # プロファイルから設定を読み込み
    pandoc_service.load_profile_data(cli_args.profile)

    # コマンドライン引数で上書き
    pandoc_service.output_format = cli_args.format

    # 入出力パスの処理
    input_path = Path(cli_args.input)
    output_path = Path(cli_args.output)

    if not input_path.exists():
        logger.error("Input path does not exist: %s", input_path)
        return 1

    # 入力がファイルかフォルダかを判定
    if input_path.is_file():
        # ファイル変換
        logger.info("Converting file: %s -> %s", input_path, output_path)
        success, stdout, stderr, returncode = pandoc_service.convert_file(
            input_path, output_path)

        if success:
            logger.info("Conversion successful: %s", output_path)
            if stdout.strip():
                print(stdout)
            return 0
        else:
            logger.error("Conversion failed (exit code %s)", returncode)
            if stderr.strip():
                print(stderr, file=sys.stderr)
            return 1

    elif input_path.is_dir():
        # フォルダ変換
        if not output_path.exists():
            output_path.mkdir(parents=True)

        # 出力拡張子を決定
        format_ext_map = {
            "html": ".html",
            "pdf": ".pdf",
            "docx": ".docx",
            "epub": ".epub",
            "markdown": ".md"
        }
        ext = format_ext_map.get(cli_args.format, ".html")

        logger.info("Converting folder: %s -> %s", input_path, output_path)

        success_count, fail_count, _errors = pandoc_service.convert_folder(
            input_path, output_path, ext)

        total_count = success_count + fail_count
        logger.info("Conversion completed: %s/%s files successful",
                    success_count, total_count)

        if success_count == total_count:
            return 0
        return 1
    else:
        logger.error("Invalid input path: %s", input_path)
        return 1


# -------------------------
# 起動
# -------------------------
if __name__ == "__main__":
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(
        description="Pandoc GUI - Markdown/HTML converter with GUI or CLI mode")
    parser.add_argument('-i', '--input', help='Input file or folder path')
    parser.add_argument('-o', '--output', help='Output file or folder path')
    parser.add_argument('-f',
                        '--format',
                        choices=['html', 'pdf', 'docx', 'epub', 'markdown'],
                        default='html',
                        help='Output format (default: html)')
    parser.add_argument('-p',
                        '--profile',
                        default='default',
                        help='Profile name to use (default: default)')

    args = parser.parse_args()

    # 入力が指定されている場合はCLIモード
    if args.input:
        if not args.output:
            parser.error("--output is required when --input is specified")
        sys.exit(run_cli_mode(args))

    # GUIモード
    app = MainWindow()
    app.mainloop()
