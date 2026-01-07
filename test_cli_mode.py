# -*- coding: utf-8 -*-
"""コマンドラインモードのテストコード."""
import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from main_window import run_cli_mode


class TestCliMode(unittest.TestCase):
    """コマンドラインモードのテスト."""

    def setUp(self):
        """テスト前の準備."""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # テスト用の入力ファイルを作成
        self.input_file = self.temp_path / "test_input.md"
        self.input_file.write_text("# Test\n\nThis is a test.",
                                   encoding='utf-8')

        # テスト用の入力フォルダを作成
        self.input_folder = self.temp_path / "input_folder"
        self.input_folder.mkdir()
        (self.input_folder / "doc1.md").write_text("# Doc1", encoding='utf-8')
        (self.input_folder / "doc2.md").write_text("# Doc2", encoding='utf-8')

        # 出力先
        self.output_file = self.temp_path / "test_output.html"
        self.output_folder = self.temp_path / "output_folder"

    def tearDown(self):
        """テスト後のクリーンアップ."""
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_file_conversion_success(self, mock_service_class,
                                              mock_check_pandoc):
        """ファイル変換が成功する場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_file.return_value = (True, "Success", "", 0)

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_file),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 0)
        mock_service.convert_file.assert_called_once()
        mock_service.load_profile_data.assert_called_once()

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_file_conversion_failure(self, mock_service_class,
                                              mock_check_pandoc):
        """ファイル変換が失敗する場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_file.return_value = (False, "", "Error occurred",
                                                  1)

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_file),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 1)

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_folder_conversion_success(self, mock_service_class,
                                                mock_check_pandoc):
        """フォルダ変換が成功する場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_folder.return_value = (2, 0, [])  # 成功2, 失敗0, エラーなし

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_folder),
                                  output=str(self.output_folder),
                                  format='pdf',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 0)
        mock_service.convert_folder.assert_called_once()

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_folder_conversion_partial_failure(self,
                                                        mock_service_class,
                                                        mock_check_pandoc):
        """フォルダ変換が部分的に失敗する場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_folder.return_value = (1, 1, [("doc2.md", "Error")]
                                                    )  # 成功1, 失敗1

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_folder),
                                  output=str(self.output_folder),
                                  format='html',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 1)

    @patch('main_window.check_pandoc_installed')
    def test_cli_mode_pandoc_not_installed(self, mock_check_pandoc):
        """Pandocがインストールされていない場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = False

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_file),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 1)

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.load_profile')
    def test_cli_mode_profile_not_found(self, mock_load_profile,
                                        mock_check_pandoc):
        """プロファイルが見つからない場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_load_profile.return_value = None

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_file),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='nonexistent')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 1)

    @patch('main_window.check_pandoc_installed')
    def test_cli_mode_input_not_exists(self, mock_check_pandoc):
        """入力ファイルが存在しない場合のテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True

        # 引数を作成（存在しないファイル）
        args = argparse.Namespace(input=str(self.temp_path / "nonexistent.md"),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='default')

        # 実行
        result = run_cli_mode(args)

        # 検証
        self.assertEqual(result, 1)

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_different_formats(self, mock_service_class,
                                        mock_check_pandoc):
        """異なる出力形式でのテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_file.return_value = (True, "Success", "", 0)

        # 各形式でテスト
        formats = ['html', 'pdf', 'docx', 'epub', 'markdown']
        for fmt in formats:
            with self.subTest(format=fmt):
                args = argparse.Namespace(input=str(self.input_file),
                                          output=str(self.temp_path /
                                                     f"output.{fmt}"),
                                          format=fmt,
                                          profile='default')

                result = run_cli_mode(args)

                # 検証
                self.assertEqual(result, 0)
                # output_formatが正しく設定されたか確認
                self.assertEqual(mock_service.output_format, fmt)

    @patch('main_window.check_pandoc_installed')
    @patch('main_window.PandocService')
    def test_cli_mode_custom_profile(self, mock_service_class,
                                     mock_check_pandoc):
        """カスタムプロファイルを使用するテスト."""
        # モックの設定
        mock_check_pandoc.return_value = True
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.convert_file.return_value = (True, "Success", "", 0)

        # 引数を作成
        args = argparse.Namespace(input=str(self.input_file),
                                  output=str(self.output_file),
                                  format='html',
                                  profile='myprofile')

        # load_profileをモック
        with patch('main_window.load_profile') as mock_load_profile:
            mock_load_profile.return_value = {
                'filters': [],
                'css_file': None,
                'embed_css': False
            }

            result = run_cli_mode(args)

            # 検証
            self.assertEqual(result, 0)
            mock_load_profile.assert_called_once_with('myprofile')


class TestCliArguments(unittest.TestCase):
    """コマンドライン引数のパースのテスト."""

    def test_parse_arguments_minimal(self):
        """最小限の引数でパースできるか."""
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input')
        parser.add_argument('-o', '--output')
        parser.add_argument('-f', '--format', default='html')
        parser.add_argument('-p', '--profile', default='default')

        args = parser.parse_args(['-i', 'input.md', '-o', 'output.html'])

        self.assertEqual(args.input, 'input.md')
        self.assertEqual(args.output, 'output.html')
        self.assertEqual(args.format, 'html')
        self.assertEqual(args.profile, 'default')

    def test_parse_arguments_all_options(self):
        """すべてのオプションを指定してパースできるか."""
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input')
        parser.add_argument('-o', '--output')
        parser.add_argument('-f', '--format', default='html')
        parser.add_argument('-p', '--profile', default='default')

        args = parser.parse_args([
            '-i', 'input.md', '-o', 'output.pdf', '-f', 'pdf', '-p', 'myprofile'
        ])

        self.assertEqual(args.input, 'input.md')
        self.assertEqual(args.output, 'output.pdf')
        self.assertEqual(args.format, 'pdf')
        self.assertEqual(args.profile, 'myprofile')


if __name__ == '__main__':
    unittest.main()
