import tkinter as tk
from tkinter import ttk

from routes.dashboard import obtener_resumen_diario
from ui.layout import ScrollableFrame, fit_tree_columns


BG = "#0f0f0f"
PANEL = "#1a1a1a"
TEXT = "#f5f5f5"
MUTED = "#9e9e9e"
ORANGE = "#ff7b00"
FONT = "Segoe UI"


class DashboardFrame(tk.Frame):
    def __init__(self, parent, usuario=None):
        super().__init__(parent, bg=BG)
        self.usuario = usuario
        self._render()

    def _render(self):
        for child in self.winfo_children():
            child.destroy()

        data = obtener_resumen_diario()
        header = tk.Frame(self, bg=PANEL, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Panel Principal", bg=PANEL, fg=TEXT,
            font=(FONT, 21, "bold"),
        ).pack(side="left", padx=24)
        tk.Label(
            header, text="Resumen operativo de hoy",
            bg=PANEL, fg=MUTED, font=(FONT, 10),
        ).pack(side="right", padx=24)

        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        content = scroll.content
        for column in range(4):
            content.columnconfigure(column, weight=1, uniform="kpi")

        cards = (
            ("Ventas del día", f"${data['ventas_dia']:,.2f}", ORANGE),
            ("Cantidad de ventas", str(data["cantidad_ventas"]), "#55c78a"),
            ("Artículos con stock bajo", str(data["stock_bajo"]), "#ef6b45"),
            ("Valor del inventario", f"${data['valor_inventario']:,.2f}", TEXT),
        )
        for index, (title, value, color) in enumerate(cards):
            card = tk.Frame(content, bg=PANEL, padx=16, pady=14)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 8), pady=(0, 18))
            tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=(FONT, 10)).pack(anchor="w")
            tk.Label(card, text=value, bg=PANEL, fg=color, font=(FONT, 19, "bold")).pack(
                anchor="w", pady=(8, 0)
            )

        actions = tk.Frame(content, bg=BG)
        actions.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 18))
        tk.Label(
            actions, text="Accesos rápidos", bg=BG, fg=TEXT,
            font=(FONT, 12, "bold"),
        ).pack(side="left", padx=(0, 12))
        callbacks = getattr(self.master, "menu_actions", {})
        for label, key in (
            ("Nueva venta", "ventas"),
            ("Nuevo artículo", "articulos"),
            ("Registrar compra", "compras"),
        ):
            tk.Button(
                actions, text=label, command=callbacks.get(key, lambda: None),
                bg=ORANGE, fg="white", activebackground="#ff9500",
                relief="flat", padx=15, pady=8, cursor="hand2",
            ).pack(side="left", padx=5)

        tk.Label(
            content, text="Últimos movimientos del día",
            bg=BG, fg=TEXT, font=(FONT, 12, "bold"),
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 7))
        style = ttk.Style(self)
        style.configure(
            "Punihard.Treeview", background=PANEL, fieldbackground=PANEL,
            foreground=TEXT, rowheight=24, font=(FONT, 10),
        )
        style.configure(
            "Punihard.Treeview.Heading", background="#292929",
            foreground=TEXT, relief="flat", font=(FONT, 10, "bold"),
        )
        tree = ttk.Treeview(
            content, columns=("hora", "tipo", "articulo", "cantidad"),
            show="headings", style="Punihard.Treeview", height=12,
        )
        for column, title, width, anchor in (
            ("hora", "Hora", 150, "w"),
            ("tipo", "Movimiento", 190, "w"),
            ("articulo", "Artículo", 400, "w"),
            ("cantidad", "Cantidad", 140, "e"),
        ):
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor=anchor)
        tree.grid(row=3, column=0, columnspan=4, sticky="nsew")
        fit_tree_columns(tree, {"hora": 0.9, "tipo": 1.2, "articulo": 3, "cantidad": 1})
        content.rowconfigure(3, weight=1)
        for index, movement in enumerate(data["movimientos"]):
            sign = "+" if movement["cantidad"] > 0 else ""
            tree.insert(
                "", "end",
                values=(
                    movement["fecha"].strftime("%H:%M"),
                    movement["tipo"].replace("_", " ").title(),
                    movement["articulo"],
                    f"{sign}{movement['cantidad']:g}",
                ),
                tags=("even" if index % 2 == 0 else "odd",),
            )
        tree.tag_configure("even", background="#202020")
        tree.tag_configure("odd", background=PANEL)
