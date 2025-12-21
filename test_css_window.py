# -*- coding: utf-8 -*-
"""CSS設定ウィンドウのテストコード."""
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from css_window import CSSWindow


class TestCSSWindow(unittest.TestCase):
    """CSSWindowクラスのテスト."""

    def setUp(self):
        """テスト用のCSSWindowインスタンスを作成."""
        # 親ウィンドウのモックを作成
        self.parent = Mock()
        self.parent.logger = MagicMock()
        self.parent.last_filter_dir = Path(".")

        # CSSWindowのGUI初期化をモックして回避
        with patch.object(CSSWindow, '__init__', return_value=None):
            self.window = CSSWindow(self.parent)

        # 必要な属性を手動で設定
        self.window.parent = self.parent
        self.window.logger = self.parent.logger
        self.window.css_file = None
        self.window.embed_mode = True
        self.window.result = None
        self.window.style_var = Mock()
        self.window.css_label = Mock()

    def test_initial_state(self):
        """初期状態の確認."""
        self.assertIsNone(self.window.css_file)
        self.assertTrue(self.window.embed_mode)
        self.assertIsNone(self.window.result)

    def test_set_css_config_with_file(self):
        """CSSファイルありでの設定."""
        test_file = Path("test.css")
        self.window.set_css_config(test_file, True)

        self.assertEqual(self.window.css_file, test_file)
        self.window.css_label.config.assert_called_with(text=str(test_file),
                                                        fg="black")
        self.window.style_var.set.assert_called_with("embed")

    def test_set_css_config_without_file(self):
        """CSSファイルなしでの設定."""
        self.window.set_css_config(None, False)

        self.assertIsNone(self.window.css_file)
        self.window.css_label.config.assert_called_with(text="未選択", fg="gray")
        self.window.style_var.set.assert_called_with("external")

    def test_set_css_config_external_mode(self):
        """外部スタイルモードでの設定."""
        test_file = Path("external.css")
        self.window.set_css_config(test_file, False)

        self.assertEqual(self.window.css_file, test_file)
        self.window.style_var.set.assert_called_with("external")

    def test_select_css_file(self):
        """CSSファイル選択のテスト."""
        test_file = "C:/test/style.css"

        with patch('css_window.filedialog.askopenfilename',
                   return_value=test_file):
            self.window.select_css_file()

            self.assertEqual(self.window.css_file, Path(test_file))
            self.assertEqual(self.parent.last_filter_dir,
                             Path(test_file).parent)
            self.window.css_label.config.assert_called_once()
            self.window.logger.info.assert_called_once()

    def test_select_css_file_cancelled(self):
        """CSSファイル選択のキャンセル."""
        with patch('css_window.filedialog.askopenfilename', return_value=""):
            self.window.select_css_file()

            # ファイルが選択されなかった場合は変更なし
            self.assertIsNone(self.window.css_file)

    def test_confirm_embed_mode(self):
        """確定ボタン（埋め込みモード）のテスト."""
        self.window.css_file = Path("test.css")
        self.window.style_var.get.return_value = "embed"
        self.window.destroy = Mock()

        self.window.confirm()

        self.assertIsNotNone(self.window.result)
        self.assertEqual(self.window.result["css_file"], Path("test.css"))
        self.assertTrue(self.window.result["embed_mode"])
        self.window.destroy.assert_called_once()

    def test_confirm_external_mode(self):
        """確定ボタン（外部スタイルモード）のテスト."""
        self.window.css_file = Path("test.css")
        self.window.style_var.get.return_value = "external"
        self.window.destroy = Mock()

        self.window.confirm()

        self.assertIsNotNone(self.window.result)
        self.assertEqual(self.window.result["css_file"], Path("test.css"))
        self.assertFalse(self.window.result["embed_mode"])
        self.window.destroy.assert_called_once()

    def test_cancel(self):
        """キャンセルボタンのテスト."""
        self.window.css_file = Path("test.css")
        self.window.destroy = Mock()

        self.window.cancel()

        self.assertIsNone(self.window.result)
        self.window.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
