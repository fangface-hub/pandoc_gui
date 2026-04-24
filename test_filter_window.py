# -*- coding: utf-8 -*-
"""フィルター管理ウィンドウのテストコード."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from filter_window import FilterWindow


class TestFilterWindow(unittest.TestCase):
    """FilterWindowクラスのテスト."""

    def setUp(self):
        """テスト用のFilterWindowインスタンスを作成."""
        # 親ウィンドウのモックを作成
        self.parent = Mock()
        self.parent.logger = MagicMock()
        self.parent.last_filter_dir = Path(".")
        self.parent.i18n = Mock()
        self.parent.i18n.t.side_effect = lambda key, **kwargs: key

        # FilterWindowのGUI初期化をモックして回避
        with patch.object(FilterWindow, '__init__', return_value=None):
            self.window = FilterWindow(self.parent)

        # 必要な属性を手動で設定
        self.window.parent = self.parent
        self.window.logger = self.parent.logger
        self.window.i18n = self.parent.i18n
        self.window.enabled_filters = []
        self.window.result = None
        self.window.enabled_list = Mock()

    def test_initial_state(self):
        """初期状態の確認."""
        self.assertEqual(self.window.enabled_filters, [])
        self.assertIsNone(self.window.result)

    def test_set_filters(self):
        """フィルター設定のテスト."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.set_filters(test_filters)

        self.assertEqual(self.window.enabled_filters, test_filters)
        self.window.enabled_list.delete.assert_called_once()

    def test_get_filters(self):
        """フィルター取得のテスト."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.enabled_filters = test_filters

        result = self.window.get_filters()
        self.assertEqual(result, test_filters)

    def test_add_user_filter(self):
        """ユーザーフィルター追加のテスト."""
        test_file = "C:/filters/custom.lua"

        with patch('filter_window.filedialog.askopenfilename',
                   return_value=test_file):
            self.window.add_user_filter()

            self.assertEqual(len(self.window.enabled_filters), 1)
            self.assertEqual(self.window.enabled_filters[0], Path(test_file))
            self.assertEqual(self.parent.last_filter_dir,
                             Path(test_file).parent)
            self.window.logger.info.assert_called_once()

    def test_add_user_filter_duplicate(self):
        """重複フィルター追加の防止."""
        test_file = Path("filter.lua")
        self.window.enabled_filters = [test_file]

        with patch('filter_window.filedialog.askopenfilename',
                   return_value=str(test_file)):
            self.window.add_user_filter()

            # 重複は追加されない
            self.assertEqual(len(self.window.enabled_filters), 1)

    def test_add_user_filter_cancelled(self):
        """フィルター追加のキャンセル."""
        with patch('filter_window.filedialog.askopenfilename', return_value=""):
            self.window.add_user_filter()

            # ファイルが選択されなかった場合は変更なし
            self.assertEqual(len(self.window.enabled_filters), 0)

    def test_remove_filter(self):
        """フィルター削除のテスト."""
        test_filters = [
            Path("filter1.lua"),
            Path("filter2.lua"),
            Path("filter3.lua")
        ]
        self.window.enabled_filters = test_filters
        self.window.enabled_list.curselection.return_value = (1, )

        self.window.remove_filter()

        self.assertEqual(len(self.window.enabled_filters), 2)
        self.assertNotIn(Path("filter2.lua"), self.window.enabled_filters)
        self.window.logger.info.assert_called_once()

    def test_remove_filter_no_selection(self):
        """選択なしでのフィルター削除."""
        test_filters = [Path("filter1.lua")]
        self.window.enabled_filters = test_filters
        self.window.enabled_list.curselection.return_value = ()

        self.window.remove_filter()

        # 選択がない場合は変更なし
        self.assertEqual(len(self.window.enabled_filters), 1)

    def test_move_up(self):
        """フィルターを上に移動."""
        test_filters = [
            Path("filter1.lua"),
            Path("filter2.lua"),
            Path("filter3.lua")
        ]
        self.window.enabled_filters = test_filters.copy()
        self.window.enabled_list.curselection.return_value = (1, )

        self.window.move_up()

        self.assertEqual(self.window.enabled_filters[0], Path("filter2.lua"))
        self.assertEqual(self.window.enabled_filters[1], Path("filter1.lua"))
        self.window.enabled_list.select_set.assert_called_with(0)

    def test_move_up_first_item(self):
        """最初のアイテムは上に移動できない."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.enabled_filters = test_filters.copy()
        self.window.enabled_list.curselection.return_value = (0, )

        self.window.move_up()

        # 変更なし
        self.assertEqual(self.window.enabled_filters, test_filters)

    def test_move_down(self):
        """フィルターを下に移動."""
        test_filters = [
            Path("filter1.lua"),
            Path("filter2.lua"),
            Path("filter3.lua")
        ]
        self.window.enabled_filters = test_filters.copy()
        self.window.enabled_list.curselection.return_value = (1, )

        self.window.move_down()

        self.assertEqual(self.window.enabled_filters[1], Path("filter3.lua"))
        self.assertEqual(self.window.enabled_filters[2], Path("filter2.lua"))
        self.window.enabled_list.select_set.assert_called_with(2)

    def test_move_down_last_item(self):
        """最後のアイテムは下に移動できない."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.enabled_filters = test_filters.copy()
        self.window.enabled_list.curselection.return_value = (1, )

        self.window.move_down()

        # 変更なし
        self.assertEqual(self.window.enabled_filters, test_filters)

    def test_refresh_enabled_list(self):
        """フィルターリスト更新のテスト."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.enabled_filters = test_filters

        self.window._refresh_enabled_list()  # pylint: disable=protected-access

        self.window.enabled_list.delete.assert_called_with(0, unittest.mock.ANY)
        self.assertEqual(self.window.enabled_list.insert.call_count, 2)

    def test_confirm(self):
        """確定ボタンのテスト."""
        test_filters = [Path("filter1.lua"), Path("filter2.lua")]
        self.window.enabled_filters = test_filters
        self.window.destroy = Mock()

        self.window.confirm()

        self.assertEqual(self.window.result, test_filters)
        self.window.destroy.assert_called_once()

    def test_cancel(self):
        """キャンセルボタンのテスト."""
        test_filters = [Path("filter1.lua")]
        self.window.enabled_filters = test_filters
        self.window.destroy = Mock()

        self.window.cancel()

        self.assertIsNone(self.window.result)
        self.window.destroy.assert_called_once()

    def test_reset_filters(self):
        """初期化で組み込みフィルターに戻る."""
        with tempfile.TemporaryDirectory() as src_tmp, \
             tempfile.TemporaryDirectory() as dst_tmp, \
             patch('filter_window.messagebox.askyesno', return_value=True), \
             patch('filter_window.messagebox.showinfo'):
            src_filters = Path(src_tmp) / "filters"
            dst_filters = Path(dst_tmp) / "filters"
            src_filters.mkdir(parents=True, exist_ok=True)
            (src_filters / "md2html.lua").write_text("-- md2html",
                                                     encoding='utf-8')
            (src_filters / "diaglam.lua").write_text("-- diaglam",
                                                     encoding='utf-8')
            (src_filters / "wikilink.lua").write_text("-- wikilink",
                                                      encoding='utf-8')
            dst_filters.mkdir(parents=True, exist_ok=True)
            (dst_filters / "custom.lua").write_text("-- custom",
                                                    encoding='utf-8')

            with patch('filter_window.SCRIPT_DIR', Path(src_tmp)), \
                 patch('filter_window.DATA_DIR', Path(dst_tmp)):
                self.window.reset_filters()

            self.assertEqual(len(self.window.enabled_filters), 4)
            self.assertEqual(self.parent.last_filter_dir, dst_filters)
            self.assertTrue((dst_filters / "md2html.lua").exists())
            self.assertTrue((dst_filters / "diaglam.lua").exists())
            self.assertTrue((dst_filters / "wikilink.lua").exists())
            self.assertIn(dst_filters / "custom.lua",
                          self.window.enabled_filters)


if __name__ == "__main__":
    unittest.main()
