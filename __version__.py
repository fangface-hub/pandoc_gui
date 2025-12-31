# -*- coding: utf-8 -*-
"""バージョン情報を管理するモジュール.

バージョン番号の取得優先順位:
1. pip installされている場合: importlib.metadataから取得
2. 開発環境の場合: pyproject.tomlから直接読み込み
3. どちらも失敗: フォールバックとして "1.0.0"

Python 3.11以降は標準ライブラリのtomlllib、
それ以前はサードパーティのtomliパッケージを使用。
"""
import sys
from pathlib import Path

# Python 3.11+ では標準のtomllib、それ以前はtomliを使用
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        # tomliがインストールされていない場合はpyproject.tomlの読み込みをスキップ
        tomllib = None

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as metadata_version
except ImportError:
    # Python 3.7以前ではimportlib.metadataが存在しない
    class PackageNotFoundError(Exception):  # type: ignore[no-redef]
        """Custom exception for package not found."""

    metadata_version = None


def get_version() -> str:
    """pyproject.tomlからバージョン情報を取得.

    Returns
    -------
    str
        バージョン番号
    """
    # 方法1: pip installされている場合、パッケージメタデータから取得
    if metadata_version is not None:
        try:
            return metadata_version("pandoc-gui")
        except PackageNotFoundError:
            pass

    # 方法2: 開発環境の場合、pyproject.tomlから直接読み込む
    if tomllib is not None:
        pyproject_path = Path(__file__).parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "1.0.0")

    # 方法3: フォールバック（古いPython環境やpyproject.tomlが見つからない場合）
    return "1.0.0"


__version__ = get_version()
