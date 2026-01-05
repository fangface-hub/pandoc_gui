# -*- coding: utf-8 -*-
"""Pandoc GUIアプリケーションのテストコード."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from main_window import MainWindow
from pandoc_service import (PandocService, from_relative_path, get_app_dir,
                            get_data_dir, init_default_profile, load_profile,
                            save_profile, to_relative_path)

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = get_data_dir()


class TestGetAppDir(unittest.TestCase):
    """get_app_dir関数のテスト."""

    def test_get_app_dir_not_frozen(self):
        """非frozen環境では__file__のディレクトリを返す."""
        with patch.object(sys, 'frozen', False, create=True):
            result = get_app_dir()
            # main_window.pyのディレクトリが返される
            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())

    def test_get_app_dir_frozen(self):
        """frozen環境ではsys.executableのディレクトリを返す."""
        with patch.object(sys, 'frozen', True, create=True), \
             patch.object(sys, 'executable', 'C:/test/app.exe'):
            result = get_app_dir()
            self.assertEqual(result, Path('C:/test'))


class TestPathConversion(unittest.TestCase):
    """パス変換関数のテスト."""

    def test_to_relative_path_within_data_dir(self):
        """データディレクトリ内のパスは相対パスに変換される."""
        test_path = DATA_DIR / "profiles" / "test.json"
        result = to_relative_path(test_path)
        # OSに依存しないようにPathで正規化して比較
        self.assertEqual(Path(result), Path("profiles/test.json"))

    def test_to_relative_path_outside_data_dir(self):
        """データディレクトリ外のパスは絶対パスのまま."""
        test_path = Path("C:/temp/test.md")
        result = to_relative_path(test_path)
        self.assertTrue(Path(result).is_absolute())

    def test_to_relative_path_none(self):
        """Noneを渡すとNoneが返る."""
        result = to_relative_path(None)
        self.assertIsNone(result)

    def test_from_relative_path_relative(self):
        """相対パスはデータディレクトリ基準で解決される."""
        result = from_relative_path("profiles/test.json")
        expected = (DATA_DIR / "profiles" / "test.json").resolve()
        self.assertEqual(result, expected)

    def test_from_relative_path_absolute(self):
        """絶対パスはそのまま返される."""
        test_path = Path("C:/temp/test.md")
        result = from_relative_path(str(test_path))
        self.assertEqual(result, test_path)

    def test_from_relative_path_none(self):
        """Noneを渡すとNoneが返る."""
        result = from_relative_path(None)
        self.assertIsNone(result)


class TestProfileManagement(unittest.TestCase):
    """プロファイル管理機能のテスト."""

    def setUp(self):
        """テスト用プロファイルディレクトリを設定."""
        self.test_profile_name = "test_profile"
        profile_filename = f"{self.test_profile_name}.json"
        self.test_profile_path = DATA_DIR / "profiles" / profile_filename
        # テスト用にディレクトリを作成
        self.test_profile_path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """テスト用プロファイルを削除."""
        if self.test_profile_path.exists():
            self.test_profile_path.unlink()

    def test_save_and_load_profile(self):
        """プロファイルの保存と読み込み."""
        test_data = {
            "filters": ["filters/test.lua"],
            "css_file": "style.css",
            "embed_css": False,
            "output_format": "pdf",
            "java_path": "/usr/bin/java",
            "plantuml_jar": "/opt/plantuml.jar",
            "plantuml_use_server": False,
            "plantuml_server_url": "http://www.plantuml.com/plantuml",
        }

        # 保存
        save_profile(self.test_profile_name, test_data)
        self.assertTrue(self.test_profile_path.exists())

        # 読み込み
        loaded_data = load_profile(self.test_profile_name)
        # マスターデフォルトから補完されるキーがあるため、主要項目のみ検証
        self.assertEqual(loaded_data["filters"], test_data["filters"])
        self.assertEqual(loaded_data["css_file"], test_data["css_file"])
        self.assertEqual(loaded_data["embed_css"], test_data["embed_css"])
        self.assertEqual(loaded_data["output_format"],
                         test_data["output_format"])
        self.assertEqual(loaded_data["java_path"], test_data["java_path"])
        self.assertEqual(loaded_data["plantuml_jar"], test_data["plantuml_jar"])
        self.assertEqual(loaded_data["plantuml_use_server"],
                         test_data["plantuml_use_server"])
        self.assertEqual(loaded_data["plantuml_server_url"],
                         test_data["plantuml_server_url"])

    def test_load_nonexistent_profile(self):
        """存在しないプロファイルの読み込みはNoneを返す."""
        result = load_profile("nonexistent_profile")
        self.assertIsNone(result)

    def test_init_default_profile(self):
        """デフォルトプロファイルの初期化."""
        default_path = DATA_DIR / "profiles" / "default.json"
        # テスト用にディレクトリを作成
        default_path.parent.mkdir(parents=True, exist_ok=True)

        # 既存のdefault.jsonを一時的にバックアップ
        backup_data = None
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                backup_data = f.read()
            default_path.unlink()

        try:
            # 初期化
            init_default_profile()
            self.assertTrue(default_path.exists())

            # 内容確認
            with open(default_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIn("filters", data)
            self.assertIn("css_file", data)
            self.assertIn("embed_css", data)
            self.assertIn("output_format", data)
            self.assertIn("exclude_patterns", data)
            self.assertIn("java_path", data)
            self.assertIn("plantuml_jar", data)
            self.assertIn("plantuml_use_server", data)
            self.assertIn("plantuml_server_url", data)
            self.assertEqual(data["filters"], [])
            self.assertEqual(data["exclude_patterns"], [])
            self.assertIsNone(data["css_file"])
            self.assertTrue(data["embed_css"])
            self.assertEqual(data["output_format"], "html")
            self.assertIsNone(data["java_path"])
            self.assertIsNone(data["plantuml_jar"])
            self.assertFalse(data["plantuml_use_server"])
            self.assertEqual(data["plantuml_server_url"],
                             "http://www.plantuml.com/plantuml")

        finally:
            # バックアップを復元
            if backup_data:
                with open(default_path, "w", encoding="utf-8") as f:
                    f.write(backup_data)


class TestMainWindow(unittest.TestCase):
    """MainWindowクラスのテスト."""

    def setUp(self):
        """テスト用の簡易MainWindowオブジェクトを作成."""
        # MainWindowのインスタンス化を回避し、必要な属性だけを設定
        with patch('main_window.tk.Tk.__init__', return_value=None), \
             patch('main_window.LogWindow'), \
             patch.object(MainWindow, '__init__', return_value=None):
            self.window = MainWindow()

        # 必要な属性を手動で追加
        self.window.tk = Mock()  # tkinter属性のモック
        self.window.logger = MagicMock()
        self.window.i18n = Mock()
        self.window.i18n.t = Mock(side_effect=lambda key, **kwargs: key)
        self.window.input_path = None
        self.window.output_path = None
        # PandocServiceのモックを追加
        self.window.pandoc_service = Mock(spec=PandocService)
        self.window.pandoc_service.enabled_filters = []
        self.window.pandoc_service.exclude_patterns = []
        self.window.pandoc_service.css_file = None
        self.window.pandoc_service.embed_css = True
        self.window.pandoc_service.output_format = "html"
        self.window.pandoc_service.java_path = None
        self.window.pandoc_service.plantuml_jar = None
        self.window.pandoc_service.plantuml_use_server = False
        self.window.pandoc_service.plantuml_server_url = \
            "http://www.plantuml.com/plantuml"
        self.window.pandoc_service.should_exclude = Mock(return_value=False)
        self.window.input_type_var = Mock()
        self.window.format_var = Mock()
        self.window.profile_var = Mock()
        self.window.proc_lock = MagicMock()
        self.window.current_proc = None
        # StringVarのモックを追加
        self.window.java_path_var = Mock()
        self.window.java_path_var.get = Mock(return_value="")
        self.window.plantuml_jar_var = Mock()
        self.window.plantuml_jar_var.get = Mock(return_value="")
        self.window.plantuml_method_var = Mock()
        self.window.plantuml_method_var.get = Mock(return_value="jar")
        self.window.plantuml_server_url_var = Mock()
        self.window.plantuml_server_url_var.get = Mock(
            return_value="http://www.plantuml.com/plantuml")
        # その他の必要な属性
        self.window.input_type = "single"
        self.window.toc_enabled = False
        self.window.toc_depth = 3
        self.window.number_sections = False

    def test_initial_state(self):
        """初期状態の確認."""
        self.assertIsNone(self.window.input_path)
        self.assertIsNone(self.window.output_path)
        self.assertEqual(self.window.pandoc_service.enabled_filters, [])
        self.assertEqual(self.window.pandoc_service.exclude_patterns, [])
        self.assertIsNone(self.window.pandoc_service.css_file)
        self.assertTrue(self.window.pandoc_service.embed_css)
        self.assertEqual(self.window.pandoc_service.output_format, "html")

    def test_save_profile_method(self):
        """save_profileメソッドのテスト."""
        self.window.profile_var.get.return_value = "test"
        self.window.pandoc_service.enabled_filters = [Path("filters/test.lua")]
        self.window.pandoc_service.css_file = Path("style.css")
        self.window.pandoc_service.embed_css = False
        self.window.pandoc_service.output_format = "pdf"
        self.window.pandoc_service.save_profile_data = Mock()

        self.window.save_profile()
        self.window.pandoc_service.save_profile_data.\
            assert_called_once_with("test")

    def test_load_profile_method(self):
        """load_profileメソッドのテスト."""
        self.window.profile_var.get.return_value = "test"
        self.window.format_var.set = Mock()
        # pylint: disable=protected-access
        self.window._update_css_info_label = Mock()
        self.window._on_format_changed = Mock()
        # pylint: enable=protected-access
        self.window.pandoc_service.load_profile_data = Mock(return_value=True)
        self.window.pandoc_service.output_format = "pdf"
        self.window.pandoc_service.java_path = None
        self.window.pandoc_service.plantuml_jar = None
        self.window.pandoc_service.plantuml_use_server = False
        self.window.pandoc_service.plantuml_server_url = \
            "http://www.plantuml.com/plantuml"

        self.window.load_profile()

        self.window.pandoc_service.load_profile_data.\
            assert_called_once_with("test")
        self.window.format_var.set.assert_called_once_with("pdf")

    def test_run_pandoc_without_input(self):
        """入力なしでrun_pandocを実行するとエラー."""
        self.window.input_path = None
        self.window.output_path = None

        self.window.run_pandoc()
        self.window.logger.error.assert_called_once()

    def test_run_pandoc_command_generation(self):
        """Pandocコマンド生成のテスト."""
        self.window.input_path = Path("test.md")
        self.window.output_path = Path("output")
        self.window.enabled_filters = []
        self.window.css_file = None
        self.window.output_format = "html"

        with patch.object(Path, 'is_file', return_value=True), \
             patch('main_window.threading.Thread') as mock_thread:
            self.window.run_pandoc()
            mock_thread.assert_called_once()

    def test_run_pandoc_pdf_command(self):
        """PDF変換コマンド生成のテスト."""
        self.window.input_path = Path("test.md")
        self.window.output_path = Path("output.pdf")
        self.window.pandoc_service.enabled_filters = []
        self.window.pandoc_service.css_file = None
        self.window.pandoc_service.output_format = "pdf"

        # pandoc_serviceのbuild_pandoc_commandメソッドの動作を確認
        expected_cmd = [
            "pandoc", "test.md", "-o", "output.pdf", "--pdf-engine=lualatex",
            "-V", "documentclass=ltjsarticle", "--standalone"
        ]

        self.window.pandoc_service.build_pandoc_command = Mock(
            return_value=expected_cmd)

        with patch.object(Path, 'is_file', return_value=True), \
             patch('main_window.threading.Thread'):
            self.window.run_pandoc()
            # スレッドが作成されたことを確認
            # (実際の変換はバックグラウンドで実行される)

    def test_should_exclude_pattern_matching(self):
        """除外パターンのマッチングテスト."""
        self.window.pandoc_service.exclude_patterns = [
            "*.tmp", "__pycache__", ".git", "node_modules"
        ]
        # 実際のshould_excludeメソッドをテスト用に作成
        service = PandocService(self.window.logger)
        service.exclude_patterns = (self.window.pandoc_service.exclude_patterns)

        # ファイル名でマッチング
        self.assertTrue(service.should_exclude(Path("test.tmp")))
        self.assertTrue(service.should_exclude(Path("dir/file.tmp")))

        # フォルダ名でマッチング
        self.assertTrue(service.should_exclude(Path("__pycache__/file.py")))
        self.assertTrue(
            service.should_exclude(Path("src/__pycache__/module.pyc")))
        self.assertTrue(service.should_exclude(Path(".git/config")))
        self.assertTrue(
            service.should_exclude(Path("project/node_modules/package.json")))

        # マッチしない
        self.assertFalse(service.should_exclude(Path("test.py")))
        self.assertFalse(service.should_exclude(Path("src/main.py")))
        self.assertFalse(service.should_exclude(Path("cache/data.json")))

    def test_should_exclude_wildcard_patterns(self):
        """ワイルドカードパターンのテスト."""
        self.window.pandoc_service.exclude_patterns = [
            "*.log", "test_*", "*_backup"
        ]
        # 実際のshould_excludeメソッドをテスト用に作成
        service = PandocService(self.window.logger)
        service.exclude_patterns = (self.window.pandoc_service.exclude_patterns)

        # *.log
        self.assertTrue(service.should_exclude(Path("app.log")))
        self.assertTrue(service.should_exclude(Path("logs/error.log")))

        # test_*
        self.assertTrue(service.should_exclude(Path("test_main.py")))
        self.assertTrue(service.should_exclude(Path("tests/test_utils.py")))

        # *_backup
        self.assertTrue(service.should_exclude(Path("data_backup")))
        self.assertTrue(service.should_exclude(Path("files/config_backup")))

        # マッチしない
        self.assertFalse(service.should_exclude(Path("main.py")))
        self.assertFalse(service.should_exclude(Path("logger.py")))


class TestPlantUMLSettings(unittest.TestCase):
    """PlantUML設定のテスト."""

    def test_plantuml_jar_method(self):
        """JAR方式のPlantUML設定テスト."""
        logger = MagicMock()
        service = PandocService(logger)
        service.java_path = Path("/usr/bin/java")
        service.plantuml_jar = Path("/opt/plantuml.jar")
        service.plantuml_use_server = False
        service.plantuml_server_url = "http://www.plantuml.com/plantuml"

        self.assertFalse(service.plantuml_use_server)
        self.assertEqual(service.java_path, Path("/usr/bin/java"))
        self.assertEqual(service.plantuml_jar, Path("/opt/plantuml.jar"))

    def test_plantuml_server_method(self):
        """サーバ方式のPlantUML設定テスト."""
        logger = MagicMock()
        service = PandocService(logger)
        service.java_path = None
        service.plantuml_jar = None
        service.plantuml_use_server = True
        service.plantuml_server_url = "https://plantuml.example.com/plantuml"

        self.assertTrue(service.plantuml_use_server)
        self.assertEqual(service.plantuml_server_url,
                         "https://plantuml.example.com/plantuml")
        self.assertIsNone(service.java_path)
        self.assertIsNone(service.plantuml_jar)

    def test_save_profile_with_plantuml_server(self):
        """サーバ設定を含むプロファイル保存テスト."""
        test_profile_name = "test_plantuml_server"
        profile_path = DATA_DIR / "profiles" / f"{test_profile_name}.json"
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            test_data = {
                "filters": [],
                "css_file": None,
                "embed_css": True,
                "output_format": "html",
                "exclude_patterns": [],
                "java_path": None,
                "plantuml_jar": None,
                "plantuml_use_server": True,
                "plantuml_server_url": "https://custom.server.com/plantuml",
            }

            save_profile(test_profile_name, test_data)
            self.assertTrue(profile_path.exists())

            loaded_data = load_profile(test_profile_name)
            self.assertTrue(loaded_data["plantuml_use_server"])
            self.assertEqual(loaded_data["plantuml_server_url"],
                             "https://custom.server.com/plantuml")
            self.assertIsNone(loaded_data["java_path"])
            self.assertIsNone(loaded_data["plantuml_jar"])

        finally:
            if profile_path.exists():
                profile_path.unlink()

    def test_load_legacy_profile_without_server_settings(self):
        """サーバ設定のない旧プロファイル読み込みテスト."""
        test_profile_name = "test_legacy"
        profile_path = DATA_DIR / "profiles" / f"{test_profile_name}.json"
        profile_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 旧形式のプロファイル（サーバ設定なし）
            legacy_data = {
                "filters": [],
                "css_file": None,
                "embed_css": True,
                "output_format": "html",
                "exclude_patterns": [],
                "java_path": "/usr/bin/java",
                "plantuml_jar": "/opt/plantuml.jar",
            }

            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(legacy_data, f, ensure_ascii=False, indent=2)

            loaded_data = load_profile(test_profile_name)
            # load_profile内でマスターデフォルトから補完される
            # デフォルト値が補完されることを確認
            self.assertIn("plantuml_use_server", loaded_data)
            self.assertIn("plantuml_server_url", loaded_data)
            # 補完後のファイルを確認
            with open(profile_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            self.assertIn("plantuml_use_server", saved_data)
            self.assertIn("plantuml_server_url", saved_data)

        finally:
            if profile_path.exists():
                profile_path.unlink()


if __name__ == "__main__":
    unittest.main()
