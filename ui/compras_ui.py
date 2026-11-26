import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from routes.articulos import listar_articulos
from routes.compras import anular_compra, crear_compra, listar_compras
from routes.proveedores import listar_proveedores
from ui.layout import ScrollableFrame, fit_tree_columns


BG = "#0f0f0f"
PANEL = "#1a1a1a"
INPUT = "#262626"
TEXT = "#f5f5f5"
MUTED = "#9e9e9e"
ORANGE = "#ff7b00"
FONT = "Segoe UI"


class ComprasFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        style = ttk.Style(parent)
        style.configure(
            "Punihard.Treeview", background=PANEL, fieldbackground=PANEL,
            foreground=TEXT, rowheight=24, font=(FONT, 10),
        )
        style.configure(
            "Punihard.Treeview.Heading", background="#292929",
            foreground=TEXT, relief="flat", font=(FONT, 10, "bold"),
        )
        style.map("Punihard.Treeview", background=[("selected", "#78400f")])
        self.providers = {}
        self.articles = {}
        self.product_labels = {}
        self.cart = []
        self._build()
        self.refrescar_proveedores()
        self.refrescar_articulos()
        self.refrescar_compras()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Ingreso de Mercadería", bg=PANEL, fg=TEXT,
            font=(FONT, 21, "bold"),
        ).pack(side="left", padx=24)

        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        body = scroll.content
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=3)
        body.rowconfigure(5, weight=2)

        header_form = tk.Frame(body, bg=PANEL, padx=12, pady=10)
        header_form.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        tk.Label(header_form, text="Proveedor", bg=PANEL, fg=MUTED).grid(
            row=0, column=0, sticky="w"
        )
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(
            header_form, textvariable=self.provider_var, width=34,
        )
        self.provider_combo.grid(row=1, column=0, padx=(0, 14), sticky="ew")
        self.provider_combo.bind("<KeyRelease>", self._filtrar_proveedores)
        tk.Label(header_form, text="Comprobante", bg=PANEL, fg=MUTED).grid(
            row=0, column=1, sticky="w"
        )
        self.document_type = ttk.Combobox(
            header_form, state="readonly", width=16,
            values=("Factura", "Remito", "Nota de crédito", "Otro"),
        )
        self.document_type.set("Factura")
        self.document_type.grid(row=1, column=1, padx=(0, 10))
        tk.Label(header_form, text="Número", bg=PANEL, fg=MUTED).grid(
            row=0, column=2, sticky="w"
        )
        self.number_entry = tk.Entry(
            header_form, bg=INPUT, fg=TEXT, insertbackground=TEXT,
            relief="flat", width=20,
        )
        self.number_entry.grid(row=1, column=2, padx=(0, 10), ipady=5)
        tk.Label(header_form, text="Fecha (AAAA-MM-DD)", bg=PANEL, fg=MUTED).grid(
            row=0, column=3, sticky="w"
        )
        self.date_entry = tk.Entry(
            header_form, bg=INPUT, fg=TEXT, insertbackground=TEXT,
            relief="flat", width=15,
        )
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=3, ipady=5)
        header_form.columnconfigure(0, weight=1)

        add_panel = tk.Frame(body, bg=BG)
        add_panel.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        tk.Label(add_panel, text="Artículo", bg=BG, fg=MUTED).pack(side="left")
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(add_panel, textvariable=self.product_var)
        self.product_combo.pack(side="left", fill="x", expand=True, padx=(7, 12))
        self.product_combo.bind("<KeyRelease>", self._filtrar_articulos)
        self.product_combo.bind("<Return>", self._agregar_enter)
        self.product_combo.bind("<<ComboboxSelected>>", self._seleccionar_articulo)
        tk.Label(add_panel, text="Cantidad", bg=BG, fg=MUTED).pack(side="left")
        self.quantity_entry = tk.Entry(
            add_panel, bg=INPUT, fg=TEXT, insertbackground=TEXT,
            relief="flat", width=8,
        )
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side="left", padx=(6, 10), ipady=5)
        tk.Label(add_panel, text="Costo unitario $", bg=BG, fg=MUTED).pack(side="left")
        self.cost_entry = tk.Entry(
            add_panel, bg=INPUT, fg=TEXT, insertbackground=TEXT,
            relief="flat", width=12,
        )
        self.cost_entry.pack(side="left", padx=(6, 10), ipady=5)
        tk.Button(
            add_panel, text="Agregar ítem", command=self.agregar_articulo,
            bg=ORANGE, fg="white", activebackground="#ff9500",
            relief="flat", padx=13, pady=6,
        ).pack(side="left")

        cart_panel = tk.Frame(body, bg=PANEL)
        cart_panel.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self.cart_tree = ttk.Treeview(
            cart_panel, columns=("articulo", "cantidad", "costo", "total"),
            show="headings", style="Punihard.Treeview", selectmode="browse",
        )
        for column, title, width, anchor in (
            ("articulo", "Artículo", 420, "w"),
            ("cantidad", "Cantidad", 110, "e"),
            ("costo", "Costo unitario", 145, "e"),
            ("total", "Subtotal", 145, "e"),
        ):
            self.cart_tree.heading(column, text=title)
            self.cart_tree.column(column, width=width, anchor=anchor)
        self.cart_tree.pack(fill="both", expand=True, padx=8, pady=8)
        fit_tree_columns(self.cart_tree, {
            "articulo": 3.2, "cantidad": 0.9, "costo": 1.2, "total": 1.2,
        })
        buttons = tk.Frame(body, bg=BG)
        buttons.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        tk.Button(
            buttons, text="Quitar ítem seleccionado", command=self.quitar_articulo,
            bg="#353535", fg=TEXT, relief="flat", padx=12, pady=5,
        ).pack(side="left")
        self.total_label = tk.Label(
            buttons, text="TOTAL COMPRA  $0.00", bg=BG, fg=ORANGE,
            font=(FONT, 16, "bold"),
        )
        self.total_label.pack(side="right", padx=8)

        notes = tk.Frame(body, bg=BG)
        notes.grid(row=4, column=0, sticky="ew", pady=(0, 9))
        tk.Label(notes, text="Observaciones", bg=BG, fg=MUTED).pack(side="left")
        self.notes_entry = tk.Entry(
            notes, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat",
        )
        self.notes_entry.pack(side="left", fill="x", expand=True, padx=8, ipady=5)
        tk.Button(
            notes, text="Registrar compra", command=self.guardar,
            bg=ORANGE, fg="white", activebackground="#ff9500",
            relief="flat", padx=20, pady=7, cursor="hand2",
        ).pack(side="right")

        history = tk.Frame(body, bg=BG)
        history.grid(row=5, column=0, sticky="nsew")
        tk.Label(history, text="Compras recientes", bg=BG, fg=TEXT, font=(FONT, 12, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        history_panel = tk.Frame(history, bg=PANEL)
        history_panel.pack(fill="both", expand=True)
        self.history_tree = ttk.Treeview(
            history_panel, columns=("numero", "proveedor", "fecha", "total"),
            show="headings", style="Punihard.Treeview", height=5,
        )
        for column, title, width, anchor in (
            ("numero", "Comprobante", 180, "w"),
            ("proveedor", "Proveedor", 300, "w"),
            ("fecha", "Fecha", 160, "w"),
            ("total", "Total", 130, "e"),
        ):
            self.history_tree.heading(column, text=title)
            self.history_tree.column(column, width=width, anchor=anchor)
        self.history_tree.pack(side="top", fill="both", expand=True)
        fit_tree_columns(self.history_tree, {
            "numero": 1.2, "proveedor": 2, "fecha": 1.1, "total": 0.9,
        })
        history_actions = tk.Frame(history_panel, bg=PANEL)
        history_actions.pack(side="bottom", fill="x", padx=6, pady=6)
        tk.Button(
            history_actions, text="Anular compra", command=self.anular_seleccionada,
            bg="#8b2525", fg="white", relief="flat", padx=10, pady=4,
        ).pack(side="left")

    def refrescar_proveedores(self):
        self.providers = {}
        labels = []
        for provider in listar_proveedores():
            label = f"{provider.nombre} — {provider.cuit or provider.telefono or 'Proveedor'}"
            self.providers[label] = provider.id
            labels.append(label)
        self.provider_combo.configure(values=labels)
        self.provider_labels = labels

    def _filtrar_proveedores(self, event):
        if event.keysym in ("Return", "Up", "Down", "Escape"):
            return
        text = self.provider_var.get().strip().casefold()
        matches = [
            label for label in self.provider_labels
            if text in label.casefold()
        ] if text else self.provider_labels
        self.provider_combo.configure(values=matches)
        if matches and text:
            self.provider_combo.event_generate("<Down>")

    def refrescar_articulos(self):
        self.articles = {item.id: item for item in listar_articulos() if item.activo}
        self._set_product_options(self.articles.values())

    def _set_product_options(self, articles):
        self.product_labels = {}
        labels = []
        for item in articles:
            label = f"{item.codigo or 'S/C'} — {item.nombre}"
            self.product_labels[label] = item.id
            labels.append(label)
        self.product_combo.configure(values=labels)

    def _filtrar_articulos(self, event):
        if event.keysym in ("Return", "Up", "Down", "Escape"):
            return
        text = self.product_var.get().strip().casefold()
        matches = [
            item for item in self.articles.values()
            if text in (item.nombre or "").casefold()
            or text in (item.codigo or "").casefold()
        ] if text else list(self.articles.values())
        self._set_product_options(matches)
        if matches and text:
            self.product_combo.event_generate("<Down>")

    def _resolve_product(self):
        product_id = self.product_labels.get(self.product_var.get().strip())
        if product_id:
            return self.articles.get(product_id)
        text = self.product_var.get().strip().casefold()
        matches = [
            item for item in self.articles.values()
            if text in {(item.codigo or "").casefold(), (item.nombre or "").casefold()}
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            self._set_product_options(matches)
            self.product_combo.event_generate("<Down>")
        return None

    def _seleccionar_articulo(self, _event=None):
        item = self._resolve_product()
        if item:
            self.cost_entry.delete(0, "end")
            self.cost_entry.insert(0, str(item.precio_compra or 0))

    def _agregar_enter(self, _event=None):
        self.agregar_articulo()
        return "break"

    def agregar_articulo(self):
        item = self._resolve_product()
        if not item:
            messagebox.showwarning("Artículo", "Elegí un artículo válido de la lista.")
            return
        try:
            quantity = float(self.quantity_entry.get().replace(",", "."))
            cost = float(self.cost_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Compra", "Ingresá una cantidad y costo válidos.")
            return
        if quantity <= 0 or cost < 0:
            messagebox.showerror("Compra", "La cantidad debe ser mayor a cero y el costo no puede ser negativo.")
            return
        self.cart.append({
            "articulo_id": item.id,
            "cantidad": quantity,
            "costo_unitario": cost,
        })
        self.product_var.set("")
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")
        self.cost_entry.delete(0, "end")
        self._render_cart()

    def _render_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0.0
        for index, values in enumerate(self.cart):
            article_id = values["articulo_id"]
            item = self.articles[article_id]
            quantity = values["cantidad"]
            cost = values["costo_unitario"]
            subtotal = quantity * cost
            total += subtotal
            self.cart_tree.insert(
                "", "end", iid=str(index),
                values=(item.nombre, f"{quantity:g} {item.unidad}",
                        f"${cost:,.2f}", f"${subtotal:,.2f}"),
            )
        self.total_label.configure(text=f"TOTAL COMPRA  ${total:,.2f}")

    def quitar_articulo(self):
        selection = self.cart_tree.selection()
        if selection:
            self.cart.pop(int(selection[0]))
            self._render_cart()

    def guardar(self):
        proveedor_id = self.providers.get(self.provider_var.get())
        number = self.number_entry.get().strip()
        if not proveedor_id or not number or not self.cart:
            messagebox.showwarning(
                "Datos incompletos",
                "Elegí un proveedor de la lista, indicá comprobante y agregá artículos.",
            )
            return
        try:
            purchase_date = datetime.strptime(self.date_entry.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Fecha inválida", "Usá el formato AAAA-MM-DD.")
            return
        ok, message = crear_compra(
            number,
            proveedor_id,
            observaciones=self.notes_entry.get().strip(),
            tipo_comprobante=self.document_type.get(),
            fecha=purchase_date,
            items=list(self.cart),
        )
        if not ok:
            messagebox.showerror("No se pudo registrar la compra", message)
            return
        messagebox.showinfo("Compra registrada", message)
        self.cart.clear()
        self.number_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.refrescar_articulos()
        self.refrescar_compras()
        self._render_cart()

    def refrescar_compras(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for purchase in listar_compras()[:30]:
            supplier = purchase.proveedor.nombre if purchase.proveedor else "Sin proveedor"
            self.history_tree.insert(
                "", "end", iid=str(purchase.id),
                values=(f"{purchase.tipo_comprobante} {purchase.numero}", supplier,
                        purchase.fecha.strftime("%d/%m/%Y"), f"${purchase.total:,.2f}"),
            )

    def anular_seleccionada(self):
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Anular compra", "Seleccioná una compra reciente.")
            return
        if not messagebox.askyesno(
            "Confirmar anulación",
            "¿Anular esta compra? Solo es posible si todavía hay stock suficiente para revertirla.",
        ):
            return
        ok, message = anular_compra(int(selection[0]))
        if ok:
            self.refrescar_articulos()
            self.refrescar_compras()
            messagebox.showinfo("Compra anulada", message)
        else:
            messagebox.showerror("No se pudo anular", message)
