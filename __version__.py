# -*- coding: utf-8 -*-
"""バージョン情報を管理するモジュール.

バージョン番号の取得優先順位:
1. pip installされている場合: importlib.metadataから取得
2. 開発環境の場合: pyproject.tomlから直接読み込み
3. frozen/MSIX環境の場合: AppxManifest.xmlから取得
4. どちらも失敗: プロジェクト既定バージョンにフォールバック

Python 3.11以降は標準ライブラリのtomllib、
それ以前はサードパーティのtomliパッケージを使用。
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Keep this in sync with pyproject.toml [project].version.
PROJECT_FALLBACK_VERSION = "1.3.2"

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
                return data.get("project", {}).get("version",
                                                   PROJECT_FALLBACK_VERSION)

    # 方法3: frozen/MSIX環境ではAppxManifest.xmlから取得を試す
    # MSIXでは実行ファイルの1階層上にAppxManifest.xmlが存在する。
    if getattr(sys, "frozen", False):
        manifest_candidates = [
            Path(sys.executable).parent.parent / "AppxManifest.xml",
            Path(sys.executable).parent / "AppxManifest.xml",
        ]
        for manifest_path in manifest_candidates:
            if not manifest_path.exists():
                continue
            try:
                root = ET.parse(manifest_path).getroot()
                identity = root.find("{*}Identity")
                if identity is None:
                    continue
                version = identity.attrib.get("Version", "").strip()
                if version:
                    # 1.3.2.0 -> 1.3.2
                    if version.endswith(".0"):
                        return version[:-2]
                    return version
            except (ET.ParseError, OSError, ValueError):
                continue

    # 方法4: フォールバック
    return PROJECT_FALLBACK_VERSION


__version__ = get_version()
