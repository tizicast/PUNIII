import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg="#0f0f0f", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_content)
        self.canvas.bind("<MouseWheel>", self._mousewheel)

    def _update_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event):
        self.canvas.itemconfigure(self._window, width=event.width)
        requested_height = self.content.winfo_reqheight()
        self.canvas.itemconfigure(self._window, height=max(requested_height, event.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _mousewheel(self, event):
        if not self.winfo_ismapped():
            return
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


def set_compact_scaling(root, factor=0.9):
    root.tk.call("tk", "scaling", factor)


def fit_tree_columns(tree, columns):
    """Resize columns to the visible table width; columns maps names to weights."""
    def resize(event):
        available = max(event.width - 6, 1)
        total_weight = sum(columns.values())
        for name, weight in columns.items():
            tree.column(name, width=max(48, int(available * weight / total_weight)), stretch=True)

    tree.bind("<Configure>", resize, add="+")
