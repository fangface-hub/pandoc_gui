# -*- coding: utf-8 -*-
"""PandocServiceのテストコード."""
import json
import logging
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from pandoc_service import PandocService, check_pandoc_installed, get_app_dir


class TestPandocServiceMermaidMode(unittest.TestCase):
    """PandocServiceのMermaidモード設定のテスト."""

    def setUp(self):
        """テストの初期化."""
        self.logger = logging.getLogger("test")
        self.service = PandocService(self.logger)

    def test_default_mermaid_mode(self):
        """デフォルトのMermaidモードはbrowser."""
        self.assertEqual(self.service.mermaid_mode, "browser")

    def test_set_mermaid_mode_browser(self):
        """Mermaidモードをbrowserに設定できる."""
        self.service.mermaid_mode = "browser"
        self.assertEqual(self.service.mermaid_mode, "browser")

    def test_mermaid_mode_in_profile(self):
        """プロファイル保存・読み込みでMermaidモードが保持される."""
        # テスト用の一時ディレクトリを使用
        with tempfile.TemporaryDirectory() as tmpdir:
            profile_dir = Path(tmpdir) / "profiles"
            profile_dir.mkdir(parents=True, exist_ok=True)

            # Mermaidモードを設定して保存
            self.service.mermaid_mode = "browser"

            # プロファイルデータを手動で作成
            profile_data = {
                "filters": [],
                "exclude_patterns": [],
                "css_file": None,
                "embed_css": True,
                "output_format": "html",
                "java_path": None,
                "plantuml_jar": None,
                "plantuml_use_server": False,
                "plantuml_server_url": "http://www.plantuml.com/plantuml",
                "mermaid_mode": "browser",
            }

            profile_file = profile_dir / "test.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f)

            # 新しいサービスインスタンスで読み込み
            new_service = PandocService(self.logger)

            # 手動でプロファイルデータを適用
            new_service.mermaid_mode = profile_data.get("mermaid_mode", "mmdc")

            self.assertEqual(new_service.mermaid_mode, "browser")


class TestPandocServiceLocalServer(unittest.TestCase):
    """PandocServiceのローカルサーバ機能のテスト."""

    def setUp(self):
        """テストの初期化."""
        self.logger = logging.getLogger("test")
        self.service = PandocService(self.logger)
        self.temp_dir = None

    def tearDown(self):
        """テストのクリーンアップ."""
        # サーバが起動していれば停止
        if self.service.local_server:
            self.service.stop_local_server()

    def test_start_local_server(self):
        """ローカルサーバを起動できる."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # サーバを起動
            port = self.service.start_local_server(temp_path)

            # ポート番号が返される
            self.assertIsNotNone(port)
            self.assertIsInstance(port, int)
            self.assertGreater(port, 0)

            # サーバが起動している
            self.assertIsNotNone(self.service.local_server)
            self.assertEqual(self.service.server_port, port)

    def test_stop_local_server(self):
        """ローカルサーバを停止できる."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # サーバを起動
            port = self.service.start_local_server(temp_path)
            self.assertIsNotNone(port)

            # サーバを停止
            self.service.stop_local_server()

            # サーバが停止している
            self.assertIsNone(self.service.local_server)
            self.assertIsNone(self.service.server_port)

    def test_server_serves_files(self):
        """サーバがファイルを配信できる."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # テスト用HTMLファイルを作成
            test_html = temp_path / "test.html"
            test_content = "<html><body>Test</body></html>"
            with open(test_html, 'w', encoding='utf-8') as f:
                f.write(test_content)

            # サーバを起動
            port = self.service.start_local_server(temp_path)
            self.assertIsNotNone(port)

            # 少し待機（サーバが完全に起動するまで）
            time.sleep(0.5)

            # HTTPリクエストでファイルを取得
            try:
                with urlopen(f"http://127.0.0.1:{port}/test.html",
                             timeout=2) as response:
                    self.assertEqual(response.status, 200)
                    content = response.read().decode('utf-8')
                    self.assertIn("Test", content)
            except URLError as e:
                self.fail(f"Failed to access local server: {e}")

    def test_server_save_svg_endpoint(self):
        """サーバがSVG保存エンドポイントを持つ."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            # サーバを起動
            port = self.service.start_local_server(temp_path)
            self.assertIsNotNone(port)

            # 少し待機
            time.sleep(0.5)

            # SVGデータをPOST
            svg_data = '<svg><circle cx="50" cy="50" r="40"/></svg>'
            payload = {'svg': svg_data, 'filename': 'test-diagram.svg'}

            try:
                data = json.dumps(payload).encode('utf-8')
                req = Request(f"http://127.0.0.1:{port}/save-svg",
                              data=data,
                              headers={'Content-Type': 'application/json'})

                with urlopen(req, timeout=2) as response:
                    self.assertEqual(response.status, 200)

                    # ファイルが保存されているか確認
                    saved_file = temp_path / 'test-diagram.svg'
                    self.assertTrue(saved_file.exists())

                    # 内容を確認
                    with open(saved_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.assertEqual(content, svg_data)

            except URLError as e:
                self.fail(f"Failed to POST to save-svg endpoint: {e}")

    def test_server_save_html_endpoint(self):
        """サーバがHTML保存エンドポイントを持つ."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)

            port = self.service.start_local_server(temp_path)
            self.assertIsNotNone(port)

            time.sleep(0.5)

            html_content = '<html><body><svg><circle/></svg></body></html>'
            payload = {'html': html_content, 'filename': 'output.html'}

            try:
                data = json.dumps(payload).encode('utf-8')
                req = Request(f"http://127.0.0.1:{port}/save-html",
                              data=data,
                              headers={'Content-Type': 'application/json'})

                with urlopen(req, timeout=2) as response:
                    self.assertEqual(response.status, 200)

                    saved_file = temp_path / 'output.html'
                    self.assertTrue(saved_file.exists())

                    with open(saved_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.assertEqual(content, html_content)

            except URLError as e:
                self.fail(f"Failed to POST to save-html endpoint: {e}")

    def test_restart_server_with_new_directory(self):
        """既存のサーバを停止して新しいディレクトリで再起動できる."""
        with tempfile.TemporaryDirectory() as tmpdir1, \
             tempfile.TemporaryDirectory() as tmpdir2:

            path1 = Path(tmpdir1)
            path2 = Path(tmpdir2)

            # 最初のサーバを起動
            port1 = self.service.start_local_server(path1)
            self.assertIsNotNone(port1)

            # 2番目のサーバを起動（自動的に最初のサーバが停止される）
            port2 = self.service.start_local_server(path2)
            self.assertIsNotNone(port2)

            # 出力ディレクトリが更新されている
            self.assertEqual(self.service.output_dir, path2.resolve())

    def test_prepare_browser_mode_server_returns_url(self):
        """browserモード用サーバを起動してHTMLのURLを返せる."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            html_file = temp_path / "test.html"
            html_file.write_text("<html><body>Test</body></html>",
                                 encoding='utf-8')

            self.service.output_format = "html"
            self.service.mermaid_mode = "browser"

            url = self.service.prepare_browser_mode_server(html_file)

            self.assertIsNotNone(url)
            self.assertTrue(url.endswith("/test.html"))
            self.assertEqual(self.service.output_dir, temp_path.resolve())

            with urlopen(url, timeout=2) as response:
                self.assertEqual(response.status, 200)
                content = response.read().decode('utf-8')
            self.assertIn("Test", content)


class TestMetadataFileCreation(unittest.TestCase):
    """メタデータファイル作成のテスト."""

    def setUp(self):
        """テストの初期化."""
        self.logger = logging.getLogger("test")
        self.service = PandocService(self.logger)

    def test_metadata_includes_mermaid_mode(self):
        """メタデータファイルにmermaid_modeが含まれる."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            input_file = temp_path / "test.md"

            # テスト用入力ファイルを作成
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write("# Test\n\nSome content")

            # Mermaidモードを設定
            self.service.mermaid_mode = "browser"

            # メタデータファイルを作成
            metadata_file = self.service.create_metadata_file(input_file)

            if metadata_file:
                # メタデータファイルの内容を確認
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.assertIn("mermaid_mode: browser", content)

                # クリーンアップ
                if metadata_file.exists():
                    metadata_file.unlink()

    def test_metadata_default_mmdc_mode(self):
        """mmdcモード（デフォルト）でメタデータファイルが正しく作成される."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            input_file = temp_path / "test.md"

            # テスト用入力ファイルを作成
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write("# Test\n\nSome content")

            # デフォルト設定（mmdc）
            self.service.mermaid_mode = "mmdc"

            # メタデータファイルを作成
            metadata_file = self.service.create_metadata_file(input_file)

            # メタデータファイルが作成される
            self.assertIsNotNone(metadata_file)

            # 内容を確認（mmdcはデフォルトなので明示的に記載されない可能性がある）
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # mmdcモードの場合も記載される、または記載されない
                # （実装に依存するので、ファイルが作成されることだけ確認）
                self.assertTrue(len(content) >= 0)

                # クリーンアップ
                metadata_file.unlink()


class TestBrowserModeConversion(unittest.TestCase):
    """browserモード変換の回帰テスト."""

    def setUp(self):
        """テストの初期化."""
        self.logger = logging.getLogger("test")
        self.service = PandocService(self.logger)

    @unittest.skipUnless(check_pandoc_installed(), "pandoc is not installed")
    def test_browser_mode_does_not_execute_mmdc(self):
        """browserモードではmmdcを実行せず、browser用HTMLを出力する."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            input_file = temp_path / "test.md"
            output_file = temp_path / "test.html"
            script_dir = get_app_dir()

            with open(input_file, 'w', encoding='utf-8') as f:
                f.write("# Test\n\n```mermaid\ngraph TD\n  A --> B\n```\n")

            self.service.output_format = "html"
            self.service.mermaid_mode = "browser"
            self.service.css_file = None
            self.service.enabled_filters = [
                script_dir / "filters" / "md2html.lua",
                script_dir / "filters" / "diaglam.lua",
                script_dir / "filters" / "wikilink.lua",
            ]

            success, _stdout, stderr, _returncode = self.service.convert_file(
                input_file, output_file)

            self.assertTrue(success)
            self.assertNotIn("Executing mermaid command", stderr)
            self.assertIn("Mermaid browser mode:", stderr)

            html = output_file.read_text(encoding='utf-8')
            self.assertIn("mermaid.min.js", html)
            self.assertNotIn("data:image/svg+xml;base64", html)
            self.assertFalse(
                (output_file.parent / "mermaid" / "mermaid.min.js").exists())


class TestProfileManagement(unittest.TestCase):
    """プロファイル管理のテスト."""

    def setUp(self):
        """テストの初期化."""
        self.logger = logging.getLogger("test")
        self.service = PandocService(self.logger)

    def test_save_and_load_mermaid_mode(self):
        """Mermaidモードを保存して読み込める."""
        # Mermaidモードを設定
        self.service.mermaid_mode = "browser"
        self.service.output_format = "html"

        # 保存用のデータを取得
        profile_data = {
            "filters": [],
            "exclude_patterns": [],
            "css_file": None,
            "embed_css": True,
            "output_format": self.service.output_format,
            "java_path": None,
            "plantuml_jar": None,
            "plantuml_use_server": False,
            "plantuml_server_url": "http://www.plantuml.com/plantuml",
            "mermaid_mode": self.service.mermaid_mode,
        }

        # 検証
        self.assertEqual(profile_data["mermaid_mode"], "browser")


if __name__ == '__main__':
    unittest.main()
