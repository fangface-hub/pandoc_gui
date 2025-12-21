# -*- coding: utf-8 -*-
"""ログウィンドウのテストコード."""
import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

from log_window import LogWindow, TextHandler


class TestTextHandler(unittest.TestCase):
    """TextHandlerクラスのテスト."""

    def test_emit(self):
        """ログメッセージの出力テスト."""
        widget = MagicMock()  # Mock → MagicMock
        handler = TextHandler(widget)
        handler.setFormatter(logging.Formatter("%(message)s"))

        record = logging.LogRecord(name="test",
                                   level=logging.INFO,
                                   pathname="",
                                   lineno=0,
                                   msg="Test message",
                                   args=(),
                                   exc_info=None)

        handler.emit(record)

        widget.insert.assert_called_once()
        widget.see.assert_called_once()


class TestLogWindow(unittest.TestCase):
    """LogWindowクラスのテスト."""

    def setUp(self):
        """テスト用のLogWindowインスタンスを作成."""
        # 親ウィンドウのモックを作成
        self.parent = Mock()
        self.parent.logger = logging.getLogger("test_logger")
        self.parent.log_button = Mock()
        self.parent.i18n = Mock()
        self.parent.i18n.t = Mock(return_value="ログウィンドウを表示")

        # LogWindowのGUI初期化をモックして回避
        with patch.object(LogWindow, '__init__', return_value=None):
            self.window = LogWindow(self.parent)

        # 必要な属性を手動で設定
        self.window.parent = self.parent
        self.window.logger = self.parent.logger
        self.window.i18n = self.parent.i18n
        self.window.log_level_var = Mock()
        self.window.log_text = Mock()

    def test_initial_state(self):
        """初期状態の確認."""
        self.assertEqual(self.window.logger, self.parent.logger)
        self.assertEqual(self.window.parent, self.parent)

    def test_change_log_level_info(self):
        """ログレベルをINFOに変更."""
        # pylint: disable=protected-access
        self.window._change_log_level("INFO")

        self.assertEqual(self.window.logger.level, logging.INFO)

    def test_change_log_level_debug(self):
        """ログレベルをDEBUGに変更."""
        # pylint: disable=protected-access
        self.window._change_log_level("DEBUG")

        self.assertEqual(self.window.logger.level, logging.DEBUG)

    def test_change_log_level_warning(self):
        """ログレベルをWARNINGに変更."""
        # pylint: disable=protected-access
        self.window._change_log_level("WARNING")

        self.assertEqual(self.window.logger.level, logging.WARNING)

    def test_change_log_level_error(self):
        """ログレベルをERRORに変更."""
        # pylint: disable=protected-access
        self.window._change_log_level("ERROR")

        self.assertEqual(self.window.logger.level, logging.ERROR)

    def test_clear_log(self):
        """ログクリアのテスト."""
        # 初期レベルをINFOに設定
        self.window.logger.setLevel(logging.INFO)

        self.window.clear_log()

        self.window.log_text.delete.assert_called_once()
        # clear_log実行後もログレベルは維持される
        self.assertEqual(self.window.logger.level, logging.INFO)

    def test_on_close(self):
        """ウィンドウクローズのテスト."""
        self.window.withdraw = Mock()
        self.window.parent = self.parent

        # pylint: disable=protected-access
        self.window._on_close()

        self.window.withdraw.assert_called_once()
        # parent.i18n.t("log_window_show")が呼ばれることを確認
        self.parent.i18n.t.assert_called_with("log_window_show")
        self.parent.log_button.config.assert_called_once()


if __name__ == "__main__":
    unittest.main()
