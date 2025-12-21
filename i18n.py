# -*- coding: utf-8 -*-
"""国際化(i18n)モジュール."""
import json
import locale
import sys
from pathlib import Path


def get_app_dir() -> Path:
    """アプリケーションのルートディレクトリを取得.

    Get application root directory.

    PyInstallerでビルドされた場合は実行ファイルのディレクトリ、
    開発環境ではスクリプトのディレクトリを返します。

    Returns
    -------
    Path
        アプリケーションのルートディレクトリ
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた場合
        return Path(sys.executable).parent
    else:
        # 通常のPythonスクリプトとして実行される場合
        return Path(__file__).parent


class I18n:
    """国際化クラス.

    Internationalization class.
    """

    def __init__(self, lang=None):
        """初期化.

        Initialize.

        Parameters
        ----------
        lang : str, optional
            言語コード（'ja', 'en'等）。Noneの場合はシステムロケールから自動検出
            (Language code ('ja', 'en', etc.).
            Auto-detect from system locale if None)
        """
        # PyInstallerビルド時のパス解決
        self.base_dir = get_app_dir()

        if lang is None:
            lang = self._detect_system_language()
        self.lang = lang
        self.translations = {}
        self.load_translations()

    def _detect_system_language(self):
        """システムのロケールから言語を検出.

        Detect language from system locale.

        Returns
        -------
        str
            言語コード（'ja', 'en'等） (Language code ('ja', 'en', etc.))
        """
        try:
            # locale.getdefaultlocale()の代わりにgetlocale()を使用
            sys_locale = locale.getlocale()[0]
            if sys_locale:
                # 'ja_JP' -> 'ja', 'en_US' -> 'en'
                lang = sys_locale.split('_')[0]
                # サポートされている言語かチェック
                if (self.base_dir / "locales" / f"{lang}.json").exists():
                    return lang
        except (ValueError, IndexError):
            pass
        # デフォルトは英語
        return 'en'

    def load_translations(self):
        """翻訳ファイルを読み込む.

        Load translation files.
        """
        locale_file = self.base_dir / "locales" / f"{self.lang}.json"
        if locale_file.exists():
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        else:
            # フォールバック: 英語を読み込む
            fallback_file = self.base_dir / "locales" / "en.json"
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)

    def t(self, key, **kwargs):
        """翻訳を取得.

        Get translation.

        Parameters
        ----------
        key : str
            翻訳キー (Translation key)
        **kwargs
            フォーマット用のパラメータ (Parameters for formatting)

        Returns
        -------
        str
            翻訳されたテキスト (Translated text)
        """
        text = self.translations.get(key, key)
        return text.format(**kwargs) if kwargs else text

    def change_language(self, lang):
        """言語を変更.

        Change language.

        Parameters
        ----------
        lang : str
            新しい言語コード (New language code)
        """
        self.lang = lang
        self.load_translations()

    def get_available_languages(self):
        """利用可能な言語のリストを取得.

        Get list of available languages.

        Returns
        -------
        list of dict
            [{"code": "en", "name": "English"}, {"code": "ja", "name": "日本語"}]
        """
        locales_dir = self.base_dir / "locales"
        languages = []

        for locale_file in locales_dir.glob("*.json"):
            lang_code = locale_file.stem
            with open(locale_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                lang_name = data.get("language_name", lang_code)
                languages.append({"code": lang_code, "name": lang_name})

        return sorted(languages, key=lambda x: x["code"])

    def get_current_language(self) -> str:
        """現在の言語コードを取得する.
        
        Returns:
            str: 現在の言語コード (例: 'ja', 'en')
        """
        return self.lang  # または適切な属性名
