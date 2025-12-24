# -*- coding: utf-8 -*-
"""Pandoc GUIアプリケーションのテストコード."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from main_window import (MainWindow, from_relative_path, get_app_dir,
                         init_default_profile, load_profile, save_profile,
                         to_relative_path)

SCRIPT_DIR = Path(__file__).parent


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

    def test_to_relative_path_within_script_dir(self):
        """スクリプトディレクトリ内のパスは相対パスに変換される."""
        test_path = SCRIPT_DIR / "profiles" / "test.json"
        result = to_relative_path(test_path)
        # OSに依存しないようにPathで正規化して比較
        self.assertEqual(Path(result), Path("profiles/test.json"))

    def test_to_relative_path_outside_script_dir(self):
        """スクリプトディレクトリ外のパスは絶対パスのまま."""
        test_path = Path("C:/temp/test.md")
        result = to_relative_path(test_path)
        self.assertTrue(Path(result).is_absolute())

    def test_to_relative_path_none(self):
        """Noneを渡すとNoneが返る."""
        result = to_relative_path(None)
        self.assertIsNone(result)

    def test_from_relative_path_relative(self):
        """相対パスはスクリプトディレクトリ基準で解決される."""
        result = from_relative_path("profiles/test.json")
        expected = (SCRIPT_DIR / "profiles" / "test.json").resolve()
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
        self.test_profile_path = Path(
            "profiles") / f"{self.test_profile_name}.json"

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
        }

        # 保存
        save_profile(self.test_profile_name, test_data)
        self.assertTrue(self.test_profile_path.exists())

        # 読み込み
        loaded_data = load_profile(self.test_profile_name)
        self.assertEqual(loaded_data, test_data)

    def test_load_nonexistent_profile(self):
        """存在しないプロファイルの読み込みはNoneを返す."""
        result = load_profile("nonexistent_profile")
        self.assertIsNone(result)

    def test_init_default_profile(self):
        """デフォルトプロファイルの初期化."""
        default_path = Path("profiles") / "default.json"

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
            self.assertEqual(data["filters"], [])
            self.assertIsNone(data["css_file"])
            self.assertTrue(data["embed_css"])
            self.assertEqual(data["output_format"], "html")

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
        self.window.enabled_filters = []
        self.window.css_file = None
        self.window.embed_css = True
        self.window.output_format = "html"
        self.window.input_type_var = Mock()
        self.window.format_var = Mock()
        self.window.profile_var = Mock()
        self.window.proc_lock = MagicMock()
        self.window.current_proc = None
        # StringVarのモックを追加
        self.window.java_path_var = Mock()
        self.window.java_path_var.get = Mock(return_value="")
        self.window.java_path = None
        self.window.plantuml_jar = None
        # その他の必要な属性
        self.window.input_type = "single"
        self.window.toc_enabled = False
        self.window.toc_depth = 3
        self.window.number_sections = False

    def test_initial_state(self):
        """初期状態の確認."""
        self.assertIsNone(self.window.input_path)
        self.assertIsNone(self.window.output_path)
        self.assertEqual(self.window.enabled_filters, [])
        self.assertIsNone(self.window.css_file)
        self.assertTrue(self.window.embed_css)
        self.assertEqual(self.window.output_format, "html")

    def test_save_profile_method(self):
        """save_profileメソッドのテスト."""
        self.window.profile_var.get.return_value = "test"
        self.window.enabled_filters = [Path("filters/test.lua")]
        self.window.css_file = Path("style.css")
        self.window.embed_css = False
        self.window.output_format = "pdf"

        with patch('main_window.save_profile') as mock_save:
            self.window.save_profile()
            mock_save.assert_called_once()

            # 引数の確認
            call_args = mock_save.call_args[0]
            self.assertEqual(call_args[0], "test")
            self.assertIn("filters", call_args[1])
            self.assertIn("css_file", call_args[1])
            self.assertIn("embed_css", call_args[1])
            self.assertIn("output_format", call_args[1])

    def test_load_profile_method(self):
        """load_profileメソッドのテスト."""
        test_data = {
            "filters": ["filters/test.lua"],
            "css_file": "style.css",
            "embed_css": False,
            "output_format": "pdf",
        }

        self.window.profile_var.get.return_value = "test"
        self.window.format_var.set = Mock()
        # pylint: disable=protected-access
        self.window._update_css_info_label = Mock()
        self.window._on_format_changed = Mock()
        # pylint: enable=protected-access

        with patch('main_window.load_profile', return_value=test_data):
            self.window.load_profile()

            self.assertEqual(len(self.window.enabled_filters), 1)
            self.assertIsNotNone(self.window.css_file)
            self.assertFalse(self.window.embed_css)
            self.assertEqual(self.window.output_format, "pdf")

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
        self.window.enabled_filters = []
        self.window.css_file = None
        self.window.output_format = "pdf"

        cmd = None

        def capture_cmd(*_args, **kwargs):
            nonlocal cmd
            # kwargs['args']にコマンドが入っている
            cmd = kwargs.get('args', [None])[0] if 'args' in kwargs else None
            # Mockオブジェクトを返して.start()が呼べるようにする
            return Mock()

        with patch.object(Path, 'is_file', return_value=True), \
             patch('main_window.threading.Thread', side_effect=capture_cmd):
            self.window.run_pandoc()

            # PDFコマンドには--pdf-engine=lualatexが含まれるはず
            self.assertIsNotNone(cmd, "Command was not captured")
            self.assertIn("--pdf-engine=lualatex", cmd)
            self.assertIn("--standalone", cmd)


if __name__ == "__main__":
    unittest.main()
