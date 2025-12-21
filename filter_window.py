# -*- coding: utf-8 -*-
"""フィルターウィンドウクラス定義."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog


class FilterWindow(tk.Toplevel):
    """フィルター管理用のモーダルウィンドウ."""

    def __init__(self, parent):
        """初期化.

        Parameters
        ----------
        parent : tk.Tk
            親ウィンドウ
        """
        super().__init__(parent)
        self.title("フィルター管理")
        self.geometry("500x400")
        self.logger = parent.logger
        self.parent = parent
        self.enabled_filters = []
        self.result = None

        # モーダル設定
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """ウィジェットを作成する."""
        # 有効フィルター
        tk.Label(self, text="有効フィルター").pack(padx=5, pady=5)
        self.enabled_list = tk.Listbox(self, height=15)
        self.enabled_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        # 操作ボタンフレーム
        btn_frame = tk.Frame(self)
        btn_frame.pack(padx=5, pady=5, fill=tk.X)

        tk.Button(btn_frame, text="ファイル追加",
                  command=self.add_user_filter).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="削除",
                  command=self.remove_filter).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="↑", command=self.move_up).pack(side=tk.LEFT,
                                                                  padx=2)
        tk.Button(btn_frame, text="↓",
                  command=self.move_down).pack(side=tk.LEFT, padx=2)

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

    def add_user_filter(self):
        """ユーザーフィルターを追加する."""
        file = filedialog.askopenfilename(filetypes=[("Lua filter", "*.lua")],
                                          initialdir=str(
                                              self.parent.last_filter_dir))
        if not file:
            return
        p = Path(file)
        self.parent.last_filter_dir = p.parent
        if p not in self.enabled_filters:
            self.enabled_filters.append(p)
            self._refresh_enabled_list()
            self.logger.info("ユーザーフィルター追加: %s", p)

    def remove_filter(self):
        """有効フィルターから削除する."""
        idx = self.enabled_list.curselection()
        if not idx:
            return
        i = idx[0]
        removed = self.enabled_filters.pop(i)
        self._refresh_enabled_list()
        self.logger.info("フィルター削除: %s", removed)

    def move_up(self):
        """有効フィルターを上に移動する."""
        idx = self.enabled_list.curselection()
        if not idx:
            return
        i = idx[0]
        if i == 0:
            return
        self.enabled_filters[i], self.enabled_filters[i - 1] = (
            self.enabled_filters[i - 1],
            self.enabled_filters[i],
        )
        self._refresh_enabled_list()
        self.enabled_list.select_set(i - 1)

    def move_down(self):
        """有効フィルターを下に移動する."""
        idx = self.enabled_list.curselection()
        if not idx:
            return
        i = idx[0]
        if i == len(self.enabled_filters) - 1:
            return
        self.enabled_filters[i], self.enabled_filters[i + 1] = (
            self.enabled_filters[i + 1],
            self.enabled_filters[i],
        )
        self._refresh_enabled_list()
        self.enabled_list.select_set(i + 1)

    def _refresh_enabled_list(self):
        """有効フィルターリストを更新する."""
        self.enabled_list.delete(0, tk.END)
        for f in self.enabled_filters:
            self.enabled_list.insert(tk.END, str(f))

    def get_filters(self):
        """有効フィルターを取得する.

        Returns
        -------
        list
            有効フィルターのリスト
        """
        return self.enabled_filters

    def set_filters(self, filters):
        """有効フィルターを設定する.

        Parameters
        ----------
        filters : list
            有効フィルターのリスト
        """
        self.enabled_filters = filters
        self._refresh_enabled_list()

    def confirm(self):
        """確定ボタンが押された時の処理."""
        self.result = self.enabled_filters
        self.destroy()

    def cancel(self):
        """キャンセルボタンが押された時の処理."""
        self.result = None
        self.destroy()

    def show_modal(self):
        """モーダルウィンドウを表示して結果を返す.

        Returns
        -------
        list or None
            選択されたフィルター、またはキャンセルされた場合はNone
        """
        self.deiconify()
        self.wait_window()
        return self.result
