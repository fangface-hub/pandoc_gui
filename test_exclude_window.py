# -*- coding: utf-8 -*-
"""除外パターン管理ウィンドウのテストコード."""
import tkinter as tk
import unittest
from unittest.mock import patch

from exclude_window import ExcludeWindow
from i18n import I18n


class TestExcludeWindow(unittest.TestCase):
    """ExcludeWindowクラスのテスト."""

    def setUp(self):
        """各テストの前処理."""
        self.root = tk.Tk()
        self.i18n = I18n("ja")
        self.saved_patterns = None

        def on_save(patterns):
            self.saved_patterns = patterns

        self.exclude_patterns = ["*.tmp", "__pycache__"]
        self.window = ExcludeWindow(self.root, self.i18n, self.exclude_patterns,
                                    on_save)

    def tearDown(self):
        """各テストの後処理."""
        try:
            self.window.destroy()
        except tk.TclError:
            pass
        self.root.destroy()

    def test_initial_patterns_loaded(self):
        """初期パターンがリストボックスに読み込まれる."""
        self.assertEqual(self.window.listbox.size(), 2)
        self.assertEqual(self.window.listbox.get(0), "*.tmp")
        self.assertEqual(self.window.listbox.get(1), "__pycache__")

    def test_add_pattern(self):
        """パターンを追加できる."""
        self.window.pattern_entry.insert(0, "*.log")
        self.window.add_pattern()

        self.assertIn("*.log", self.window.exclude_patterns)
        self.assertEqual(self.window.listbox.size(), 3)
        self.assertEqual(self.window.listbox.get(2), "*.log")

    def test_add_empty_pattern(self):
        """空のパターンは追加されない."""
        initial_size = self.window.listbox.size()
        self.window.pattern_entry.insert(0, "  ")
        self.window.add_pattern()

        self.assertEqual(self.window.listbox.size(), initial_size)

    @patch('tkinter.messagebox.showwarning')
    def test_add_duplicate_pattern(self, mock_warning):
        """重複パターンは追加されない."""
        initial_size = self.window.listbox.size()
        self.window.pattern_entry.insert(0, "*.tmp")
        self.window.add_pattern()

        self.assertEqual(self.window.listbox.size(), initial_size)
        mock_warning.assert_called_once()

    def test_remove_pattern(self):
        """パターンを削除できる."""
        self.window.listbox.selection_set(0)
        self.window.remove_pattern()

        self.assertNotIn("*.tmp", self.window.exclude_patterns)
        self.assertEqual(self.window.listbox.size(), 1)

    def test_remove_multiple_patterns(self):
        """複数のパターンを削除できる."""
        self.window.listbox.selection_set(0, 1)
        self.window.remove_pattern()

        self.assertEqual(self.window.listbox.size(), 0)
        self.assertEqual(len(self.window.exclude_patterns), 0)

    @patch('tkinter.messagebox.askyesno', return_value=True)
    def test_clear_patterns_confirmed(self, mock_confirm):
        """確認後にすべてのパターンをクリアできる."""
        self.window.clear_patterns()

        self.assertEqual(len(self.window.exclude_patterns), 0)
        self.assertEqual(self.window.listbox.size(), 0)
        mock_confirm.assert_called_once()

    @patch('tkinter.messagebox.askyesno', return_value=False)
    def test_clear_patterns_cancelled(self, mock_confirm):
        """クリアをキャンセルできる."""
        initial_size = self.window.listbox.size()
        self.window.clear_patterns()

        self.assertEqual(self.window.listbox.size(), initial_size)
        mock_confirm.assert_called_once()

    def test_save_patterns(self):
        """パターンを保存できる."""
        self.window.pattern_entry.insert(0, ".git")
        self.window.add_pattern()
        self.window.save()

        self.assertIsNotNone(self.saved_patterns)
        self.assertIn("*.tmp", self.saved_patterns)
        self.assertIn("__pycache__", self.saved_patterns)
        self.assertIn(".git", self.saved_patterns)


if __name__ == '__main__':
    unittest.main()
