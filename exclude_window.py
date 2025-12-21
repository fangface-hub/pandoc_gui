"""除外パターン管理ウィンドウ.

Exclude Pattern Management Window.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, List

from i18n import I18n


class ExcludeWindow(tk.Toplevel):
    """除外パターン管理ウィンドウクラス.

    Exclude Pattern Management Window Class.
    """

    def __init__(self, parent, i18n: I18n, exclude_patterns: List[str],
                 on_save: Callable[[List[str]], None]):
        """初期化.

        Initialize.

        Parameters
        ----------
        parent : tk.Widget
            親ウィジェット (Parent widget)
        i18n : I18n
            国際化オブジェクト (Internationalization object)
        exclude_patterns : List[str]
            除外パターンリスト (Exclude pattern list)
        on_save : Callable[[List[str]], None]
            保存時のコールバック (Callback on save)
        """
        super().__init__(parent)
        self.i18n = i18n
        self.exclude_patterns = exclude_patterns.copy()
        self.on_save = on_save

        self.title(self.i18n.t("exclude_window_title"))
        self.geometry("600x500")

        # メインフレーム
        main_frame = ttk.Frame(self, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 説明ラベル
        info_label = ttk.Label(main_frame,
                               text=self.i18n.t("exclude_window_info"),
                               wraplength=550,
                               justify=tk.LEFT)
        info_label.grid(row=0,
                        column=0,
                        columnspan=3,
                        sticky=tk.W,
                        pady=(0, 10))

        # リストボックスとスクロールバー
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1,
                        column=0,
                        columnspan=3,
                        sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        self.listbox = tk.Listbox(list_frame,
                                  yscrollcommand=scrollbar.set,
                                  selectmode=tk.EXTENDED,
                                  height=15)
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.listbox.yview)

        # リストに既存のパターンを追加
        for pattern in self.exclude_patterns:
            self.listbox.insert(tk.END, pattern)

        # 入力フレーム
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2,
                         column=0,
                         columnspan=3,
                         sticky=(tk.W, tk.E),
                         pady=10)
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame,
                  text=self.i18n.t("exclude_pattern_label")).grid(row=0,
                                                                  column=0,
                                                                  sticky=tk.W,
                                                                  padx=(0, 5))

        self.pattern_entry = ttk.Entry(input_frame)
        self.pattern_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.pattern_entry.bind('<Return>', lambda e: self.add_pattern())

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=10)

        ttk.Button(button_frame,
                   text=self.i18n.t("add_button"),
                   command=self.add_pattern).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame,
                   text=self.i18n.t("remove_button"),
                   command=self.remove_pattern).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame,
                   text=self.i18n.t("clear_button"),
                   command=self.clear_patterns).grid(row=0, column=2, padx=5)

        # 保存・キャンセルボタン
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ttk.Button(bottom_frame,
                   text=self.i18n.t("save_button"),
                   command=self.save,
                   width=12).grid(row=0, column=0, padx=5)
        ttk.Button(bottom_frame,
                   text=self.i18n.t("cancel_button"),
                   command=self.destroy,
                   width=12).grid(row=0, column=1, padx=5)

        # ウィンドウを前面に
        self.lift()
        self.focus_force()

    def add_pattern(self):
        """パターンを追加する.

        Add pattern.
        """
        pattern = self.pattern_entry.get().strip()
        if not pattern:
            return

        if pattern in self.exclude_patterns:
            messagebox.showwarning(self.i18n.t("warning"),
                                   self.i18n.t("pattern_already_exists"))
            return

        self.exclude_patterns.append(pattern)
        self.listbox.insert(tk.END, pattern)
        self.pattern_entry.delete(0, tk.END)

    def remove_pattern(self):
        """選択されたパターンを削除する.

        Remove selected pattern.
        """
        selection = self.listbox.curselection()
        if not selection:
            return

        # 逆順で削除（インデックスのずれを防ぐ）
        for idx in reversed(selection):
            pattern = self.listbox.get(idx)
            self.exclude_patterns.remove(pattern)
            self.listbox.delete(idx)

    def clear_patterns(self):
        """すべてのパターンをクリアする.

        Clear all patterns.
        """
        if not self.exclude_patterns:
            return

        result = messagebox.askyesno(self.i18n.t("confirm"),
                                     self.i18n.t("confirm_clear_patterns"))

        if result:
            self.exclude_patterns.clear()
            self.listbox.delete(0, tk.END)

    def save(self):
        """パターンを保存して閉じる.

        Save patterns and close.
        """
        self.on_save(self.exclude_patterns)
        self.destroy()
