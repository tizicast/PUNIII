import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from routes.articulos import listar_articulos
from routes.clientes import listar_clientes
from routes.ventas import anular_venta, crear_venta, listar_ventas
from ui.layout import ScrollableFrame, fit_tree_columns


BG = "#0f0f0f"
PANEL = "#1a1a1a"
INPUT = "#262626"
TEXT = "#f5f5f5"
MUTED = "#9e9e9e"
ORANGE = "#ff7b00"
BORDER = "#2f2f2f"
FONT = "Segoe UI"


def _style_tree(parent):
    style = ttk.Style(parent)
    style.configure(
        "Punihard.Treeview",
        background=PANEL,
        fieldbackground=PANEL,
        foreground=TEXT,
        rowheight=24,
        borderwidth=0,
        font=(FONT, 10),
    )
    style.configure(
        "Punihard.Treeview.Heading",
        background="#292929",
        foreground=TEXT,
        relief="flat",
        font=(FONT, 10, "bold"),
    )
    style.map("Punihard.Treeview", background=[("selected", "#78400f")])


class VentasFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        _style_tree(parent)
        self.cart = {}
        self.articles = {}
        self.customer_ids = {}
        self.products_by_label = {}
        self._build()
        self.refrescar_articulos()
        self.refrescar_clientes()
        self.refrescar_ventas()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Punto de Venta", bg=PANEL, fg=TEXT,
            font=(FONT, 21, "bold")
        ).pack(side="left", padx=24)
        tk.Label(
            header, text="Escaneá un código o buscá por nombre",
            bg=PANEL, fg=MUTED, font=(FONT, 10)
        ).pack(side="right", padx=24)

        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        body = scroll.content
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=3)
        body.rowconfigure(5, weight=2)

        top = tk.Frame(body, bg=PANEL, padx=12, pady=10)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top.columnconfigure(1, weight=1)
        tk.Label(top, text="Artículo", bg=PANEL, fg=MUTED, font=(FONT, 10)).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.product_var = tk.StringVar()
        self.product_entry = ttk.Combobox(top, textvariable=self.product_var, font=(FONT, 11))
        self.product_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.product_entry.bind("<KeyRelease>", self._filtrar_productos)
        self.product_entry.bind("<Return>", self._enter_producto)
        self.product_entry.bind("<<ComboboxSelected>>", self._producto_seleccionado)
        tk.Label(top, text="Cantidad", bg=PANEL, fg=MUTED, font=(FONT, 10)).grid(
            row=0, column=2, padx=(4, 6)
        )
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_entry = tk.Entry(
            top, textvariable=self.quantity_var, width=8, bg=INPUT, fg=TEXT,
            insertbackground=TEXT, relief="flat", font=(FONT, 11)
        )
        self.quantity_entry.grid(row=0, column=3, padx=(0, 8), ipady=5)
        tk.Button(
            top, text="Agregar", command=self.agregar_producto,
            bg=ORANGE, fg="white", activebackground="#ff9500",
            relief="flat", padx=16, pady=6, cursor="hand2",
        ).grid(row=0, column=4)

        selection = tk.Frame(body, bg=BG)
        selection.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        tk.Label(selection, text="Cliente", bg=BG, fg=MUTED, font=(FONT, 10)).pack(side="left")
        self.customer_var = tk.StringVar(value="Consumidor Final")
        self.customer_combo = ttk.Combobox(
            selection, textvariable=self.customer_var, width=34
        )
        self.customer_combo.pack(side="left", padx=(8, 18))
        self.customer_combo.bind("<KeyRelease>", self._filtrar_clientes)
        tk.Label(selection, text="Medio de pago", bg=BG, fg=MUTED, font=(FONT, 10)).pack(side="left")
        self.payment_var = tk.StringVar(value="Efectivo")
        self.payment_combo = ttk.Combobox(
            selection, textvariable=self.payment_var, state="readonly", width=22,
            values=("Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito", "Cuenta Corriente"),
        )
        self.payment_combo.pack(side="left", padx=8)
        self.payment_combo.bind("<<ComboboxSelected>>", lambda _event: self._actualizar_totales())

        cart_panel = tk.Frame(body, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        cart_panel.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        columns = ("articulo", "cantidad", "precio", "subtotal")
        self.cart_tree = ttk.Treeview(
            cart_panel, columns=columns, show="headings", style="Punihard.Treeview",
            selectmode="browse",
        )
        for column, title, width, anchor in (
            ("articulo", "Artículo", 420, "w"),
            ("cantidad", "Cantidad", 100, "e"),
            ("precio", "Precio unitario", 140, "e"),
            ("subtotal", "Subtotal", 140, "e"),
        ):
            self.cart_tree.heading(column, text=title)
            self.cart_tree.column(column, width=width, anchor=anchor)
        self.cart_tree.pack(fill="both", expand=True, padx=8, pady=8)
        fit_tree_columns(self.cart_tree, {
            "articulo": 3.2, "cantidad": 0.8, "precio": 1.2, "subtotal": 1.2,
        })
        self.cart_tree.bind("<Double-1>", self._editar_cantidad)

        controls = tk.Frame(body, bg=BG)
        controls.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        tk.Button(
            controls, text="Quitar artículo seleccionado", command=self.quitar_producto,
            bg="#353535", fg=TEXT, relief="flat", padx=12, pady=5,
        ).pack(side="left")
        tk.Label(controls, text="Doble clic en cantidad para editarla", bg=BG, fg=MUTED).pack(
            side="left", padx=12
        )

        total_panel = tk.Frame(body, bg=PANEL, padx=12, pady=9)
        total_panel.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.discount_var = tk.StringVar(value="0")
        self.discount_mode_var = tk.StringVar(value="%")
        self.received_var = tk.StringVar(value="0")
        self.discount_var.trace_add("write", lambda *_: self._actualizar_totales())
        self.received_var.trace_add("write", lambda *_: self._actualizar_totales())
        tk.Label(total_panel, text="Descuento", bg=PANEL, fg=MUTED).pack(side="left")
        self.discount_mode_combo = ttk.Combobox(
            total_panel, textvariable=self.discount_mode_var, state="readonly",
            width=5, values=("%", "$"),
        )
        self.discount_mode_combo.pack(side="left", padx=(6, 5))
        self.discount_mode_combo.bind("<<ComboboxSelected>>", lambda _event: self._actualizar_totales())
        tk.Entry(
            total_panel, textvariable=self.discount_var, width=8, bg=INPUT, fg=TEXT,
            insertbackground=TEXT, relief="flat",
        ).pack(side="left", padx=(6, 18), ipady=4)
        tk.Label(total_panel, text="Recibido $", bg=PANEL, fg=MUTED).pack(side="left")
        self.received_entry = tk.Entry(
            total_panel, textvariable=self.received_var, width=12, bg=INPUT, fg=TEXT,
            insertbackground=TEXT, relief="flat",
        )
        self.received_entry.pack(side="left", padx=(6, 14), ipady=4)
        self.total_label = tk.Label(
            total_panel, text="TOTAL  $0.00", bg=PANEL, fg=ORANGE,
            font=(FONT, 17, "bold"),
        )
        self.total_label.pack(side="right", padx=14)
        self.change_label = tk.Label(total_panel, text="Vuelto: $0.00", bg=PANEL, fg=TEXT)
        self.change_label.pack(side="right")

        footer = tk.Frame(body, bg=BG)
        footer.grid(row=5, column=0, sticky="nsew")
        tk.Label(footer, text="Ventas recientes", bg=BG, fg=TEXT, font=(FONT, 12, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        history_panel = tk.Frame(footer, bg=PANEL)
        history_panel.pack(fill="both", expand=True)
        self.sales_tree = ttk.Treeview(
            history_panel, columns=("numero", "fecha", "cliente", "total", "pago"),
            show="headings", style="Punihard.Treeview", height=5,
        )
        for column, title, width, anchor in (
            ("numero", "Venta", 130, "w"),
            ("fecha", "Fecha", 155, "w"),
            ("cliente", "Cliente", 250, "w"),
            ("total", "Total", 120, "e"),
            ("pago", "Pago", 145, "w"),
        ):
            self.sales_tree.heading(column, text=title)
            self.sales_tree.column(column, width=width, anchor=anchor)
        self.sales_tree.pack(side="top", fill="both", expand=True)
        fit_tree_columns(self.sales_tree, {
            "numero": 1, "fecha": 1.1, "cliente": 1.8, "total": 0.9, "pago": 1.1,
        })
        history_actions = tk.Frame(history_panel, bg=PANEL)
        history_actions.pack(side="bottom", fill="x", padx=6, pady=6)
        tk.Button(
            history_actions, text="Anular venta", command=self.anular_seleccionada,
            bg="#8b2525", fg="white", relief="flat", padx=10, pady=4,
        ).pack(side="left")

    def refrescar_articulos(self):
        self.articles = {item.id: item for item in listar_articulos() if item.activo}
        self._establecer_opciones_productos(list(self.articles.values()))

    def _establecer_opciones_productos(self, articles):
        self.products_by_label = {}
        values = []
        for item in articles:
            label = f"{item.codigo or 'S/C'} — {item.nombre}  (stock {item.stock_actual:g})"
            self.products_by_label[label] = item.id
            values.append(label)
        self.product_entry.configure(values=values)

    def _filtrar_productos(self, event):
        if event.keysym in ("Return", "Up", "Down", "Escape"):
            return
        text = self.product_var.get().strip().casefold()
        matches = [
            item for item in self.articles.values()
            if text in (item.nombre or "").casefold()
            or text in (item.codigo or "").casefold()
        ] if text else list(self.articles.values())
        self._establecer_opciones_productos(matches)
        if matches and text:
            self.product_entry.event_generate("<Down>")

    def _producto_seleccionado(self, _event=None):
        self.agregar_producto()

    def _enter_producto(self, _event=None):
        text = self.product_var.get().strip()
        product_id = self.products_by_label.get(text)
        if product_id is None:
            exact = [
                item for item in self.articles.values()
                if text.casefold() in {
                    (item.codigo or "").casefold(), (item.nombre or "").casefold()
                }
            ]
            if len(exact) == 1:
                product_id = exact[0].id
            else:
                if exact:
                    self._establecer_opciones_productos(exact)
                    self.product_entry.event_generate("<Down>")
                    return "break"
                messagebox.showwarning("Artículo", "No se encontró el artículo. Elegilo de la lista.")
                return "break"
        self.agregar_producto(product_id)
        return "break"

    def agregar_producto(self, product_id=None):
        if product_id is None:
            product_id = self.products_by_label.get(self.product_var.get().strip())
        item = self.articles.get(product_id)
        if not item:
            messagebox.showwarning("Artículo", "Seleccioná un artículo válido.")
            return
        try:
            quantity = float(self.quantity_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Cantidad", "Ingresá una cantidad válida.")
            return
        if quantity <= 0:
            messagebox.showerror("Cantidad", "La cantidad debe ser mayor a cero.")
            return
        existing = self.cart.get(item.id, 0)
        if quantity + existing > item.stock_actual:
            messagebox.showwarning("Stock insuficiente", f"Disponible: {item.stock_actual:g} {item.unidad}.")
            return
        self.cart[item.id] = quantity + existing
        self._render_cart()
        self.product_var.set("")
        self.quantity_var.set("1")
        self.product_entry.focus_set()

    def _render_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for article_id, quantity in self.cart.items():
            item = self.articles[article_id]
            price = float(item.precio_venta or 0)
            self.cart_tree.insert(
                "", "end", iid=str(article_id),
                values=(item.nombre, f"{quantity:g} {item.unidad}", f"${price:,.2f}",
                        f"${quantity * price:,.2f}"),
            )
        self._actualizar_totales()

    def _editar_cantidad(self, event):
        row = self.cart_tree.identify_row(event.y)
        column = self.cart_tree.identify_column(event.x)
        if not row or column != "#2":
            return
        box = self.cart_tree.bbox(row, column)
        if not box:
            return
        editor = tk.Entry(self.cart_tree, bg=INPUT, fg=TEXT, insertbackground=TEXT)
        editor.place(x=box[0], y=box[1], width=box[2], height=box[3])
        editor.insert(0, str(self.cart[int(row)]))
        editor.select_range(0, "end")
        editor.focus_set()

        def save(_event=None):
            try:
                quantity = float(editor.get().replace(",", "."))
                item = self.articles[int(row)]
                if quantity <= 0 or quantity > item.stock_actual:
                    raise ValueError
                self.cart[int(row)] = quantity
                self._render_cart()
            except ValueError:
                messagebox.showerror("Cantidad", "Ingresá una cantidad mayor a cero y no superior al stock.")
            finally:
                editor.destroy()

        editor.bind("<Return>", save)
        editor.bind("<FocusOut>", save)

    def quitar_producto(self):
        selected = self.cart_tree.selection()
        if selected:
            self.cart.pop(int(selected[0]), None)
            self._render_cart()

    def _actualizar_totales(self):
        subtotal = sum(
            quantity * float(self.articles[article_id].precio_venta or 0)
            for article_id, quantity in self.cart.items()
            if article_id in self.articles
        )
        try:
            discount = float(self.discount_var.get().replace(",", ".") or 0)
            if discount < 0 or (
                self.discount_mode_var.get() == "%" and discount > 100
            ):
                discount = 0
        except ValueError:
            discount = 0
        total = max(
            subtotal - (subtotal * discount / 100 if self.discount_mode_var.get() == "%" else discount),
            0,
        )
        self.total_label.configure(text=f"TOTAL  ${total:,.2f}")
        try:
            received = float(self.received_var.get().replace(",", ".") or 0)
        except ValueError:
            received = 0
        self.change_label.configure(
            text=f"Vuelto: ${max(received - total, 0):,.2f}"
            if self.payment_var.get() == "Efectivo" else ""
        )

    def refrescar_clientes(self):
        labels = ["Consumidor Final"]
        self.customer_ids = {"Consumidor Final": None}
        for client in listar_clientes():
            label = f"{client.nombre_completo} — {client.dni_cuit or client.telefono or 'Cliente'}"
            labels.append(label)
            self.customer_ids[label] = client.id
        self.customer_combo.configure(values=labels)
        if self.customer_var.get() not in self.customer_ids:
            self.customer_var.set("Consumidor Final")
        self.customer_labels = labels

    def _filtrar_clientes(self, event):
        if event.keysym in ("Return", "Up", "Down", "Escape"):
            return
        text = self.customer_var.get().strip().casefold()
        matches = [
            label for label in self.customer_labels
            if text in label.casefold()
        ] if text else self.customer_labels
        self.customer_combo.configure(values=matches)
        if matches and text:
            self.customer_combo.event_generate("<Down>")

    def refrescar_ventas(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        for sale in listar_ventas()[:30]:
            customer = sale.cliente.nombre_completo if sale.cliente else "Consumidor Final"
            self.sales_tree.insert(
                "", "end", iid=str(sale.id),
                values=(sale.numero, sale.fecha.strftime("%d/%m/%Y %H:%M"),
                        customer, f"${sale.total_final:,.2f}", sale.metodo_pago),
            )

    def guardar(self):
        if not self.cart:
            messagebox.showwarning("Venta", "Agregá al menos un artículo al carrito.")
            return
        try:
            discount = float(self.discount_var.get().replace(",", ".") or 0)
            received = float(self.received_var.get().replace(",", ".") or 0)
        except ValueError:
            messagebox.showerror("Venta", "Revisá el descuento y el importe recibido.")
            return
        if discount < 0 or (
            self.discount_mode_var.get() == "%" and discount > 100
        ) or received < 0:
            messagebox.showerror("Venta", "Revisá el descuento y el importe recibido.")
            return
        if self.customer_var.get() not in self.customer_ids:
            messagebox.showerror("Cliente", "Elegí un cliente válido o Consumidor Final.")
            return
        payment = self.payment_var.get()
        if payment != "Efectivo":
            received = 0
        sale_number = datetime.now().strftime("V-%Y%m%d-%H%M%S-%f")[:-3]
        ok, message = crear_venta(
            sale_number,
            cliente_id=self.customer_ids.get(self.customer_var.get()),
            descuento=discount,
            metodo_pago=payment,
            descuento_tipo="porcentaje" if self.discount_mode_var.get() == "%" else "monto",
            items=[{"articulo_id": article_id, "cantidad": quantity}
                   for article_id, quantity in self.cart.items()],
            importe_recibido=received,
        )
        if not ok:
            messagebox.showerror("No se pudo completar la venta", message)
            self.refrescar_articulos()
            return
        messagebox.showinfo("Venta registrada", f"{message}\nComprobante: {sale_number}")
        sale = next((item for item in listar_ventas() if item.numero == sale_number), None)
        self.cart.clear()
        self._render_cart()
        self.discount_var.set("0")
        self.received_var.set("0")
        self.refrescar_articulos()
        self.refrescar_ventas()
        if sale and messagebox.askyesno("Ticket PDF", "¿Querés generar un ticket PDF de esta venta?"):
            self._exportar_ticket(sale)

    def _exportar_ticket(self, sale):
        path = filedialog.asksaveasfilename(
            title="Guardar ticket", defaultextension=".pdf",
            initialfile=f"ticket_{sale.numero}.pdf",
            filetypes=(("PDF", "*.pdf"),),
        )
        if not path:
            return
        from utils.pdf import generar_ticket_pdf
        with open(path, "wb") as ticket_file:
            ticket_file.write(generar_ticket_pdf(sale).getvalue())
        try:
            os.startfile(path)
        except (AttributeError, OSError):
            messagebox.showinfo("Ticket generado", f"Se guardó el ticket en:\n{path}")

    def anular_seleccionada(self):
        selected = self.sales_tree.selection()
        if not selected:
            messagebox.showwarning("Anular venta", "Seleccioná una venta reciente.")
            return
        sale_id = int(selected[0])
        if not messagebox.askyesno(
            "Confirmar anulación",
            "¿Anular esta venta? El stock se restituirá y la operación quedará en el historial.",
        ):
            return
        ok, message = anular_venta(sale_id)
        if ok:
            self.refrescar_articulos()
            self.refrescar_ventas()
            messagebox.showinfo("Venta anulada", message)
        else:
            messagebox.showerror("No se pudo anular", message)
