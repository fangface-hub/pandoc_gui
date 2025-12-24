# -*- coding: utf-8 -*-
"""国際化モジュールのテストコード."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from i18n import I18n, get_app_dir


class TestGetAppDir(unittest.TestCase):
    """get_app_dir関数のテスト."""

    def test_get_app_dir_not_frozen(self):
        """非frozen環境では__file__のディレクトリを返す."""
        with patch.object(sys, 'frozen', False, create=True):
            result = get_app_dir()
            # i18n.pyのディレクトリが返される
            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())

    def test_get_app_dir_frozen(self):
        """frozen環境ではsys.executableのディレクトリを返す."""
        with patch.object(sys, 'frozen', True, create=True), \
             patch.object(sys, 'executable', 'C:/test/app.exe'):
            result = get_app_dir()
            self.assertEqual(result, Path('C:/test'))


class TestI18n(unittest.TestCase):
    """I18nクラスのテスト."""

    def test_initialization_with_lang(self):
        """言語コード指定での初期化."""
        i18n = I18n(lang='en')
        self.assertEqual(i18n.lang, 'en')
        self.assertIsInstance(i18n.translations, dict)

    def test_initialization_auto_detect(self):
        """言語の自動検出."""
        i18n = I18n()
        self.assertIn(i18n.lang, ['en', 'ja'])

    def test_translation_key_exists(self):
        """翻訳キーが存在する場合."""
        i18n = I18n(lang='en')
        # 実際の翻訳ファイルに存在するキーを使用
        result = i18n.t('app_title')
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, '')

    def test_translation_key_not_exists(self):
        """翻訳キーが存在しない場合はキーをそのまま返す."""
        i18n = I18n(lang='en')
        result = i18n.t('nonexistent_key')
        self.assertEqual(result, 'nonexistent_key')

    def test_translation_with_params(self):
        """パラメータ付き翻訳."""
        i18n = I18n(lang='en')
        # profile_savedキーは{name}というパラメータを持つ
        result = i18n.t('profile_saved', name='test')
        self.assertIn('test', result)

    def test_change_language(self):
        """言語切り替え."""
        i18n = I18n(lang='en')
        self.assertEqual(i18n.lang, 'en')

        i18n.change_language('ja')
        self.assertEqual(i18n.lang, 'ja')

    def test_get_available_languages(self):
        """利用可能な言語リストの取得."""
        i18n = I18n(lang='en')
        languages = i18n.get_available_languages()

        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 0)

        # 各言語エントリにcodeとnameがあることを確認
        for lang in languages:
            self.assertIn('code', lang)
            self.assertIn('name', lang)


if __name__ == "__main__":
    unittest.main()
