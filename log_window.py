# -*- coding: utf-8 -*-
"""ログウィンドウクラス定義."""
import logging
import tkinter as tk


class TextHandler(logging.Handler):
    """ログテキストウィジェット用ハンドラー.

    Handler for log text widget.
    """

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.insert(tk.END, msg + "\n")
        self.widget.see(tk.END)


class LogWindow(tk.Toplevel):
    """ログ表示用のフローティングウィンドウ.

    Floating window for log display.
    """

    def __init__(self, parent):
        """初期化.

        Initialize.

        Parameters
        ----------
        parent : tk.Tk
            親ウィンドウ (Parent window)
        """
        super().__init__(parent)
        self.title("ログ")
        self.geometry("600x300")
        self.logger = parent.logger
        self.parent = parent
        self.i18n = parent.i18n

        # ログレベル変数（内部で管理）
        self.log_level_var = tk.StringVar(value="INFO")

        # ウィンドウを閉じた時の処理
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成する.

        Create widgets.
        """
        # ログテキスト
        log_frame = tk.Frame(self, padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # スクロールバー付きテキストウィジェット
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_frame,
                                height=15,
                                yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.log_text.yview)

        # テキストハンドラーを追加
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(message)s"))
        self.logger.addHandler(text_handler)

        # ログレベル選択
        control_frame = tk.Frame(self, padx=5, pady=5)
        control_frame.pack(fill=tk.X)

        tk.Label(control_frame,
                 text=self.i18n.t("log_level") + ":").pack(side=tk.LEFT, padx=5)
        tk.OptionMenu(
            control_frame,
            self.log_level_var,
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
            command=self._change_log_level,
        ).pack(side=tk.LEFT)

        tk.Button(control_frame,
                  text=self.i18n.t("clear_log"),
                  command=self.clear_log).pack(side=tk.RIGHT, padx=5)

        # 初期状態で非表示
        self.withdraw()

    def _change_log_level(self, selected):
        """ログレベルを変更する.

        Change log level.

        Parameters
        ----------
        selected : str
            選択されたログレベル (Selected log level)
        """
        level = getattr(logging, selected)
        self.logger.setLevel(level)
        self.logger.info(self.i18n.t("log_level_changed", level=selected))

    def _on_close(self):
        """ウィンドウを閉じる時の処理.

        Process when closing window.
        """
        self.withdraw()
        self.parent.log_button.config(text=self.i18n.t("log_window_show"))

    def clear_log(self):
        """ログをクリアする.

        Clear log.
        """
        self.log_text.delete(1.0, tk.END)
        self.logger.info("ログをクリアしました")
