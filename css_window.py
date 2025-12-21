# -*- coding: utf-8 -*-
"""CSS設定ウィンドウクラス定義."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog


class CSSWindow(tk.Toplevel):
    """CSS設定用のモーダルウィンドウ."""

    def __init__(self, parent):
        """初期化.

        Parameters
        ----------
        parent : tk.Tk
            親ウィンドウ
        """
        super().__init__(parent)
        self.title("CSS設定")
        self.geometry("500x300")
        self.logger = parent.logger
        self.parent = parent
        self.css_file = None
        self.embed_mode = True
        self.result = None

        # モーダル設定
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成する."""
        # CSSファイル選択フレーム
        file_frame = tk.LabelFrame(self, text="CSSファイル", padx=5, pady=5)
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(file_frame, text="ファイル選択",
                  command=self.select_css_file).pack(fill=tk.X, padx=2, pady=2)

        self.css_label = tk.Label(file_frame, text="未選択", fg="gray")
        self.css_label.pack(fill=tk.X, pady=2)

        # スタイル設定フレーム
        style_frame = tk.LabelFrame(self, text="スタイル適用方法", padx=5, pady=5)
        style_frame.pack(fill=tk.X, padx=5, pady=5)

        self.style_var = tk.StringVar(value="embed")
        tk.Radiobutton(style_frame,
                       text="埋め込み（HTML内に含める）",
                       variable=self.style_var,
                       value="embed").pack(anchor=tk.W, pady=5)
        tk.Radiobutton(style_frame,
                       text="外部スタイル（別ファイルとしてリンク）",
                       variable=self.style_var,
                       value="external").pack(anchor=tk.W, pady=5)

        # 確定/キャンセルボタン
        dialog_frame = tk.Frame(self, padx=5, pady=5)
        dialog_frame.pack(fill=tk.X)
        tk.Button(dialog_frame, text="確定",
                  command=self.confirm).pack(side=tk.LEFT, padx=5)
        tk.Button(dialog_frame, text="キャンセル",
                  command=self.cancel).pack(side=tk.LEFT, padx=5)

        # ウィンドウをセンタリング
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() //
                                2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() //
                                2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def select_css_file(self):
        """CSSファイルを選択する."""
        file = filedialog.askopenfilename(filetypes=[("CSS files", "*.css")],
                                          initialdir=str(
                                              self.parent.last_filter_dir))
        if not file:
            return
        self.css_file = Path(file)
        self.parent.last_filter_dir = self.css_file.parent
        self.css_label.config(text=str(self.css_file), fg="black")
        self.logger.info("CSSファイル選択: %s", self.css_file)

    def set_css_config(self, css_file, embed_mode):
        """CSS設定を設定する.

        Parameters
        ----------
        css_file : Path or None
            CSSファイルパス
        embed_mode : bool
            True=埋め込み, False=外部スタイル
        """
        self.css_file = css_file
        if css_file:
            self.css_label.config(text=str(css_file), fg="black")
        else:
            self.css_label.config(text="未選択", fg="gray")

        self.style_var.set("embed" if embed_mode else "external")

    def confirm(self):
        """確定ボタンが押された時の処理."""
        self.result = {
            "css_file": self.css_file,
            "embed_mode": self.style_var.get() == "embed"
        }
        self.destroy()

    def cancel(self):
        """キャンセルボタンが押された時の処理."""
        self.result = None
        self.destroy()

    def show_modal(self):
        """モーダルウィンドウを表示して結果を返す.

        Returns
        -------
        dict or None
            {"css_file": Path, "embed_mode": bool}、またはキャンセルされた場合はNone
        """
        self.deiconify()
        self.wait_window()
        return self.result
