import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from routes.articulos import listar_articulos
from routes.remitos import crear_remito, listar_remitos, marcar_entregado
from routes.ventas import listar_ventas
from utils.pdf import generar_remito_pdf
from ui.layout import ScrollableFrame, fit_tree_columns


BG, PANEL, INPUT = "#0f0f0f", "#1a1a1a", "#262626"
TEXT, MUTED, ORANGE = "#f5f5f5", "#9e9e9e", "#ff7b00"
FONT = "Segoe UI"


class RemitosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        style = ttk.Style(parent)
        style.configure("Punihard.Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=24, font=(FONT, 10))
        style.configure("Punihard.Treeview.Heading", background="#292929",
                        foreground=TEXT, relief="flat", font=(FONT, 10, "bold"))
        self.sales = {}
        self.articles = {}
        self.article_labels = {}
        self.lines = {}
        self.remitos = {}
        self._build()
        self._load_sales()
        self._load_articles()
        self.refrescar()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Remitos de Entrega", bg=PANEL, fg=TEXT,
                 font=(FONT, 21, "bold")).pack(side="left", padx=24)
        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        content = scroll.content
        content.rowconfigure(2, weight=2)
        content.rowconfigure(4, weight=3)

        form = tk.LabelFrame(content, text="Nuevo remito", bg=PANEL, fg=TEXT,
                             font=(FONT, 10, "bold"), padx=10, pady=8)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)
        tk.Label(form, text="Número", bg=PANEL, fg=MUTED).grid(row=0, column=0, sticky="w")
        self.number_entry = tk.Entry(form, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.number_entry.insert(0, datetime.now().strftime("R-%Y%m%d-%H%M%S"))
        self.number_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), ipady=5)
        tk.Label(form, text="Venta existente (opcional)", bg=PANEL, fg=MUTED).grid(
            row=0, column=1, sticky="w"
        )
        self.sale_var = tk.StringVar(value="Remito independiente")
        self.sale_combo = ttk.Combobox(form, textvariable=self.sale_var, state="readonly")
        self.sale_combo.grid(row=1, column=1, sticky="ew", padx=(0, 10))
        self.sale_combo.bind("<<ComboboxSelected>>", self._sale_changed)
        tk.Label(form, text="Destinatario", bg=PANEL, fg=MUTED).grid(row=0, column=2, sticky="w")
        self.recipient_entry = tk.Entry(form, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.recipient_entry.grid(row=1, column=2, sticky="ew", padx=(0, 10), ipady=5)
        tk.Label(form, text="Dirección de entrega", bg=PANEL, fg=MUTED).grid(
            row=0, column=3, sticky="w"
        )
        self.address_entry = tk.Entry(form, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.address_entry.grid(row=1, column=3, sticky="ew", ipady=5)
        tk.Label(form, text="Observaciones", bg=PANEL, fg=MUTED).grid(
            row=2, column=0, sticky="w", pady=(7, 0)
        )
        self.notes_entry = tk.Entry(form, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat")
        self.notes_entry.grid(row=3, column=0, columnspan=4, sticky="ew", ipady=5)

        self.lines_panel = tk.Frame(content, bg=BG)
        self.lines_panel.grid(row=1, column=0, sticky="ew", pady=(0, 7))
        tk.Label(self.lines_panel, text="Artículo", bg=BG, fg=MUTED).pack(side="left")
        self.article_var = tk.StringVar()
        self.article_combo = ttk.Combobox(self.lines_panel, textvariable=self.article_var, state="readonly")
        self.article_combo.pack(side="left", fill="x", expand=True, padx=(6, 12))
        tk.Label(self.lines_panel, text="Cantidad", bg=BG, fg=MUTED).pack(side="left")
        self.quantity_entry = tk.Entry(self.lines_panel, bg=INPUT, fg=TEXT, insertbackground=TEXT,
                                       relief="flat", width=9)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side="left", padx=(6, 9), ipady=5)
        self.add_button = tk.Button(
            self.lines_panel, text="Agregar artículo", command=self.agregar_linea,
            bg="#353535", fg=TEXT, relief="flat", padx=12, pady=5,
        )
        self.add_button.pack(side="left")

        self.lines_tree = ttk.Treeview(
            content, columns=("articulo", "cantidad", "unidad"),
            show="headings", style="Punihard.Treeview", height=4,
        )
        for col, title, width, anchor in (
            ("articulo", "Detalle del remito independiente", 450, "w"),
            ("cantidad", "Cantidad", 120, "e"),
            ("unidad", "Unidad", 120, "w"),
        ):
            self.lines_tree.heading(col, text=title)
            self.lines_tree.column(col, width=width, anchor=anchor)
        self.lines_tree.grid(row=2, column=0, sticky="nsew", pady=(0, 7))
        fit_tree_columns(self.lines_tree, {"articulo": 3.2, "cantidad": 1, "unidad": 1})
        self.lines_tree.bind("<Double-1>", lambda _event: self.quitar_linea())

        actions = tk.Frame(content, bg=BG)
        actions.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        tk.Button(actions, text="Quitar línea", command=self.quitar_linea, bg="#353535",
                  fg=TEXT, relief="flat", padx=10, pady=5).pack(side="left")
        tk.Button(actions, text="Registrar remito", command=self.guardar, bg=ORANGE,
                  fg="white", relief="flat", padx=16, pady=6).pack(side="right")

        history_panel = tk.Frame(content, bg=PANEL)
        history_panel.grid(row=4, column=0, sticky="nsew")
        self.tree = ttk.Treeview(
            history_panel, columns=("numero", "fecha", "destinatario", "venta", "estado"),
            show="headings", style="Punihard.Treeview",
        )
        for col, title, width, anchor in (
            ("numero", "Remito", 150, "w"),
            ("fecha", "Fecha", 155, "w"),
            ("destinatario", "Destinatario", 260, "w"),
            ("venta", "Venta vinculada", 170, "w"),
            ("estado", "Estado", 170, "w"),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(side="top", fill="both", expand=True, padx=8, pady=8)
        fit_tree_columns(self.tree, {
            "numero": 1, "fecha": 1.1, "destinatario": 1.8, "venta": 1.3, "estado": 1.2,
        })
        actions = tk.Frame(history_panel, bg=PANEL)
        actions.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        tk.Button(actions, text="Marcar entregado", command=self.entregar, bg="#287a55",
                  fg="white", relief="flat", padx=10, pady=5).pack(side="left", padx=(0, 6))
        tk.Button(actions, text="Exportar PDF", command=self.exportar_pdf, bg="#353535",
                  fg=TEXT, relief="flat", padx=10, pady=5).pack(side="left")

    def _load_sales(self):
        self.sales = {}
        labels = ["Remito independiente"]
        for sale in listar_ventas()[:100]:
            customer = sale.cliente.nombre_completo if sale.cliente else "Consumidor Final"
            label = f"{sale.numero} — {customer} — {sale.fecha:%d/%m/%Y}"
            labels.append(label)
            self.sales[label] = sale
        self.sale_combo.configure(values=labels)

    def _load_articles(self):
        self.articles = {}
        labels = []
        for item in listar_articulos():
            label = f"{item.codigo or 'S/C'} — {item.nombre}"
            self.articles[label] = item
            labels.append(label)
        self.article_combo.configure(values=labels)

    def _sale_changed(self, _event=None):
        independent = self.sale_var.get() == "Remito independiente"
        state = "normal" if independent else "disabled"
        self.article_combo.configure(state="readonly" if independent else "disabled")
        self.quantity_entry.configure(state=state)
        self.add_button.configure(state=state)
        sale = self.sales.get(self.sale_var.get())
        if sale:
            if sale.cliente:
                self.recipient_entry.delete(0, "end")
                self.recipient_entry.insert(0, sale.cliente.nombre_completo)
                self.address_entry.delete(0, "end")
                self.address_entry.insert(0, sale.cliente.direccion or "")
            for row in self.lines_tree.get_children():
                self.lines_tree.delete(row)
        else:
            self.lines.clear()
            self._render_lines()

    def agregar_linea(self):
        item = self.articles.get(self.article_var.get())
        if not item:
            messagebox.showwarning("Remito", "Elegí un artículo.")
            return
        try:
            quantity = float(self.quantity_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Cantidad", "Ingresá una cantidad válida.")
            return
        if quantity <= 0:
            messagebox.showerror("Cantidad", "La cantidad debe ser mayor a cero.")
            return
        self.lines[item.id] = self.lines.get(item.id, 0) + quantity
        self._render_lines()

    def _render_lines(self):
        for row in self.lines_tree.get_children():
            self.lines_tree.delete(row)
        for article_id, quantity in self.lines.items():
            item = self.articles[article_id]
            self.lines_tree.insert(
                "", "end", iid=str(article_id),
                values=(item.nombre, f"{quantity:g}", item.unidad),
            )

    def quitar_linea(self):
        selection = self.lines_tree.selection()
        if selection:
            self.lines.pop(int(selection[0]), None)
            self._render_lines()

    def guardar(self):
        sale = self.sales.get(self.sale_var.get())
        items = [
            {"articulo_id": article_id, "cantidad": quantity}
            for article_id, quantity in self.lines.items()
        ]
        ok, message = crear_remito(
            self.number_entry.get(),
            venta_id=sale.id if sale else None,
            observaciones=self.notes_entry.get(),
            destinatario=self.recipient_entry.get(),
            direccion_entrega=self.address_entry.get(),
            items=items,
        )
        if not ok:
            messagebox.showerror("No se pudo crear el remito", message)
            return
        messagebox.showinfo("Remitos", message)
        self.lines.clear()
        self._render_lines()
        self.number_entry.delete(0, "end")
        self.number_entry.insert(0, datetime.now().strftime("R-%Y%m%d-%H%M%S"))
        self.sale_var.set("Remito independiente")
        self._sale_changed()
        self.recipient_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.refrescar()

    def refrescar(self):
        self.remitos = {item.id: item for item in listar_remitos()}
        self.tree.delete(*self.tree.get_children())
        for remito in self.remitos.values():
            self.tree.insert(
                "", "end", iid=str(remito.id),
                values=(
                    remito.numero, remito.fecha.strftime("%d/%m/%Y %H:%M"),
                    remito.destinatario or (
                        remito.venta.cliente.nombre_completo
                        if remito.venta and remito.venta.cliente else "—"
                    ),
                    remito.venta.numero if remito.venta else "Independiente",
                    remito.estado,
                ),
            )

    def _selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Remitos", "Seleccioná un remito.")
            return None
        return self.remitos.get(int(selection[0]))

    def entregar(self):
        remito = self._selected()
        if not remito:
            return
        if not messagebox.askyesno("Confirmar entrega", f"¿Marcar {remito.numero} como entregado?"):
            return
        ok, message = marcar_entregado(remito.id)
        if ok:
            self.refrescar()
            messagebox.showinfo("Remitos", message)
        else:
            messagebox.showerror("Remitos", message)

    def exportar_pdf(self):
        remito = self._selected()
        if not remito:
            return
        path = filedialog.asksaveasfilename(
            title="Exportar remito", defaultextension=".pdf",
            initialfile=f"remito_{remito.numero}.pdf",
            filetypes=(("PDF", "*.pdf"),),
        )
        if not path:
            return
        with open(path, "wb") as file:
            file.write(generar_remito_pdf(remito).getvalue())
        try:
            os.startfile(path)
        except (AttributeError, OSError):
            messagebox.showinfo("Remito PDF", f"Se guardó el archivo en:\n{path}")
