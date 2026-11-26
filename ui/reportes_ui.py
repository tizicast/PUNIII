import csv
import tkinter as tk
from datetime import date, timedelta
from tkinter import filedialog, messagebox, ttk

from routes.reportes import obtener_reporte
from ui.layout import ScrollableFrame, fit_tree_columns


BG = "#0f0f0f"
PANEL = "#1a1a1a"
TEXT = "#f5f5f5"
MUTED = "#9e9e9e"
ORANGE = "#ff7b00"
FONT = "Segoe UI"


class ReportesFrame(tk.Frame):
    def __init__(self, parent, usuario=None):
        super().__init__(parent, bg=BG)
        self.usuario_id = getattr(usuario, "id", None)
        style = ttk.Style(parent)
        style.configure(
            "Punihard.Treeview", background=PANEL, fieldbackground=PANEL,
            foreground=TEXT, rowheight=23, font=(FONT, 10),
        )
        style.configure(
            "Punihard.Treeview.Heading", background="#292929",
            foreground=TEXT, relief="flat", font=(FONT, 10, "bold"),
        )
        self.data = None
        self._build()
        self._set_period("Hoy")

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Reportes", bg=PANEL, fg=TEXT,
            font=(FONT, 21, "bold"),
        ).pack(side="left", padx=24)

        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        content = scroll.content
        filters = tk.Frame(content, bg=PANEL, padx=12, pady=10)
        filters.pack(fill="x", pady=(0, 12))
        tk.Label(filters, text="Período", bg=PANEL, fg=MUTED).pack(side="left")
        self.period_var = tk.StringVar(value="Hoy")
        self.period_combo = ttk.Combobox(
            filters, textvariable=self.period_var, state="readonly",
            values=("Hoy", "Esta semana", "Este mes", "Personalizado"), width=18,
        )
        self.period_combo.pack(side="left", padx=8)
        self.period_combo.bind("<<ComboboxSelected>>", self._period_changed)
        self.start_entry = self._date_field(filters)
        tk.Label(filters, text="a", bg=PANEL, fg=MUTED).pack(side="left", padx=5)
        self.end_entry = self._date_field(filters)
        tk.Button(
            filters, text="Actualizar", command=self.refrescar,
            bg=ORANGE, fg="white", activebackground="#ff9500",
            relief="flat", padx=15, pady=6,
        ).pack(side="left", padx=10)
        tk.Button(
            filters, text="Exportar reposición CSV", command=self.exportar_csv,
            bg="#353535", fg=TEXT, relief="flat", padx=12, pady=6,
        ).pack(side="right")

        self.kpis = tk.Frame(content, bg=BG)
        self.kpis.pack(fill="x", pady=(0, 12))
        for column in range(4):
            self.kpis.columnconfigure(column, weight=1, uniform="report")
        self.kpi_labels = []
        for i in range(4):
            box = tk.Frame(self.kpis, bg=PANEL, padx=14, pady=11)
            box.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 8))
            title = tk.Label(box, text="", bg=PANEL, fg=MUTED, font=(FONT, 10))
            title.pack(anchor="w")
            value = tk.Label(box, text="", bg=PANEL, fg=ORANGE, font=(FONT, 17, "bold"))
            value.pack(anchor="w", pady=(5, 0))
            self.kpi_labels.append((title, value))

        split = ttk.Panedwindow(content, orient="horizontal")
        split.pack(fill="both", expand=True)
        left = tk.Frame(split, bg=PANEL)
        right = tk.Frame(split, bg=PANEL)
        split.add(left, weight=1)
        split.add(right, weight=1)
        tk.Label(left, text="Ventas por medio de pago", bg=PANEL, fg=TEXT, font=(FONT, 12, "bold")).pack(
            anchor="w", padx=10, pady=8
        )
        self.payments_tree = self._tree(left, ("medio", "cantidad", "total"), (
            ("medio", "Medio", 190, "w"),
            ("cantidad", "Ventas", 90, "e"),
            ("total", "Importe", 140, "e"),
        ))
        tk.Label(right, text="Top 10 artículos vendidos", bg=PANEL, fg=TEXT, font=(FONT, 12, "bold")).pack(
            anchor="w", padx=10, pady=8
        )
        self.top_tree = self._tree(right, ("articulo", "cantidad", "total"), (
            ("articulo", "Artículo", 250, "w"),
            ("cantidad", "Cantidad", 100, "e"),
            ("total", "Ventas", 130, "e"),
        ))
        bottom = tk.Frame(content, bg=BG)
        bottom.pack(fill="both", expand=True, pady=(12, 0))
        tk.Label(
            bottom, text="Artículos por debajo del stock mínimo",
            bg=BG, fg=TEXT, font=(FONT, 12, "bold"),
        ).pack(anchor="w", pady=(0, 6))
        self.stock_tree = self._tree(bottom, ("codigo", "articulo", "stock", "minimo", "unidad"), (
            ("codigo", "SKU", 130, "w"),
            ("articulo", "Artículo", 360, "w"),
            ("stock", "Stock", 100, "e"),
            ("minimo", "Mínimo", 100, "e"),
            ("unidad", "Unidad", 100, "w"),
        ))

    @staticmethod
    def _date_field(parent):
        field = tk.Entry(
            parent, bg="#262626", fg=TEXT, insertbackground=TEXT,
            relief="flat", width=12,
        )
        field.pack(side="left", ipady=5)
        return field

    @staticmethod
    def _tree(parent, columns, specs):
        tree = ttk.Treeview(
            parent, columns=columns, show="headings", style="Punihard.Treeview",
        )
        for column, title, width, anchor in specs:
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor=anchor)
        fit_tree_columns(tree, {column: width for column, _title, width, _anchor in specs})
        tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        return tree

    def _period_changed(self, _event=None):
        if self.period_var.get() != "Personalizado":
            self._set_period(self.period_var.get())

    def _set_period(self, period):
        today = date.today()
        if period == "Hoy":
            start = end = today
        elif period == "Esta semana":
            start = today - timedelta(days=today.weekday())
            end = today
        elif period == "Este mes":
            start = today.replace(day=1)
            end = today
        else:
            return
        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, start.isoformat())
        self.end_entry.delete(0, "end")
        self.end_entry.insert(0, end.isoformat())
        self.refrescar()

    def refrescar(self):
        try:
            start = date.fromisoformat(self.start_entry.get().strip())
            end = date.fromisoformat(self.end_entry.get().strip())
        except ValueError:
            messagebox.showerror("Fechas inválidas", "Ingresá las fechas como AAAA-MM-DD.")
            return
        if start > end:
            messagebox.showerror("Rango inválido", "La fecha inicial no puede ser posterior a la final.")
            return
        try:
            self.data = obtener_reporte(start, end, self.usuario_id)
        except Exception as error:
            messagebox.showerror("Error al consultar reportes", str(error))
            return
        values = (
            ("Ingresos por ventas", f"${self.data['ingresos']:,.2f}"),
            ("Egresos por compras", f"${self.data['egresos']:,.2f}"),
            ("Ganancia bruta estimada", f"${self.data['ganancia_estimada']:,.2f}"),
            ("Ventas registradas", str(self.data["cantidad_ventas"])),
        )
        for (title_label, value_label), (title, value) in zip(self.kpi_labels, values):
            title_label.configure(text=title)
            value_label.configure(text=value)
        self._fill(self.payments_tree, [
            (row["metodo"], row["cantidad"], f"${row['total']:,.2f}")
            for row in self.data["pagos"]
        ])
        self._fill(self.top_tree, [
            (row["nombre"], f"{row['cantidad']:g}", f"${row['total']:,.2f}")
            for row in self.data["top_articulos"]
        ])
        self._fill(self.stock_tree, [
            (
                row["codigo"], row["nombre"], f"{row['stock']:g}",
                f"{row['minimo']:g}", row["unidad"],
            )
            for row in self.data["stock_bajo"]
        ])

    @staticmethod
    def _fill(tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=row)

    def exportar_csv(self):
        if self.data is None:
            return
        path = filedialog.asksaveasfilename(
            title="Exportar listado de reposición",
            defaultextension=".csv",
            initialfile="reposicion.csv",
            filetypes=(("CSV", "*.csv"),),
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(("Código", "Artículo", "Stock actual", "Stock mínimo", "Unidad"))
            for row in self.data["stock_bajo"]:
                writer.writerow((
                    row["codigo"], row["nombre"], row["stock"],
                    row["minimo"], row["unidad"],
                ))
        messagebox.showinfo("Exportación completa", f"Se guardó el CSV en:\n{path}")
