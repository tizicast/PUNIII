import tkinter as tk
from tkinter import messagebox, ttk

from routes.articulos import (
    crear_articulo,
    editar_articulo,
    eliminar_articulo,
    listar_articulos,
    listar_categorias,
)
from ui.layout import ScrollableFrame, fit_tree_columns


BG = "#0f0f0f"
PANEL = "#1a1a1a"
INPUT = "#262626"
TEXT = "#f5f5f5"
MUTED = "#9e9e9e"
ORANGE = "#ff7b00"
FONT = "Segoe UI"


class ArticulosFrame(tk.Frame):
    def __init__(self, parent, usuario=None):
        super().__init__(parent, bg=BG)
        self.usuario = usuario
        self.usuario_id = getattr(usuario, "id", None)
        self.is_admin = getattr(usuario, "rol", None) == "admin"
        self.selected_id = None
        self.selected_article = None
        self.categories = {}
        self.search_job = None
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
        self._build()
        self._load_categories()
        self.refrescar()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Inventario de Artículos", bg=PANEL, fg=TEXT,
            font=(FONT, 21, "bold"),
        ).pack(side="left", padx=24)

        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        content = scroll.content
        searchbar = tk.Frame(content, bg=BG)
        searchbar.pack(fill="x", pady=(0, 9))
        tk.Label(searchbar, text="Buscar", bg=BG, fg=MUTED).pack(side="left")
        self.search_var = tk.StringVar()
        search = tk.Entry(
            searchbar, textvariable=self.search_var, bg=INPUT, fg=TEXT,
            insertbackground=TEXT, relief="flat",
        )
        search.pack(side="left", fill="x", expand=True, padx=8, ipady=6)
        self.search_var.trace_add("write", self._schedule_refresh)
        tk.Label(searchbar, text="Categoría", bg=BG, fg=MUTED).pack(side="left")
        self.category_filter = ttk.Combobox(searchbar, state="readonly", width=18)
        self.category_filter.pack(side="left", padx=7)
        self.category_filter.bind("<<ComboboxSelected>>", lambda _event: self.refrescar())
        self.low_stock_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            searchbar, text="Stock bajo", variable=self.low_stock_var,
            command=self.refrescar, bg=BG, fg=TEXT, selectcolor=INPUT,
            activebackground=BG,
        ).pack(side="left", padx=5)

        table_panel = tk.Frame(content, bg=PANEL)
        table_panel.pack(fill="both", expand=True, pady=(0, 10))
        columns = ["codigo", "nombre", "categoria", "unidad"]
        specs = [
            ("codigo", "SKU / Código", 135, "w"),
            ("nombre", "Artículo", 260, "w"),
            ("categoria", "Categoría", 145, "w"),
            ("unidad", "Unidad", 85, "w"),
        ]
        if self.is_admin:
            columns.extend(("costo", "margen", "precio"))
            specs.extend((
                ("costo", "Costo", 105, "e"),
                ("margen", "Margen %", 90, "e"),
                ("precio", "Venta", 105, "e"),
            ))
        columns.extend(("stock", "minimo", "accion"))
        specs.extend((
            ("stock", "Stock", 95, "e"),
            ("minimo", "Mínimo", 90, "e"),
            ("accion", "Acción", 78, "center"),
        ))
        self.tree = ttk.Treeview(
            table_panel, columns=columns, show="headings", style="Punihard.Treeview",
        )
        for column, title, width, anchor in specs:
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor=anchor)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        fit_tree_columns(self.tree, {
            "codigo": 1.0, "nombre": 2.2, "categoria": 1.3, "unidad": 0.8,
            **({"costo": 0.9, "margen": 0.8, "precio": 0.9} if self.is_admin else {}),
            "stock": 0.8, "minimo": 0.8, "accion": 0.8,
        })
        scrollbar = ttk.Scrollbar(table_panel, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=8)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Button-1>", self._table_click)
        self.tree.bind("<Double-1>", self._table_double_click)

        form = tk.LabelFrame(
            content, text="Artículo — alta / edición", bg=PANEL,
            fg=TEXT, font=(FONT, 10, "bold"), padx=8, pady=5,
        )
        form.pack(fill="x")
        for column in range(6):
            form.columnconfigure(column, weight=1)
        self.vars = {
            "codigo": tk.StringVar(),
            "nombre": tk.StringVar(),
            "categoria": tk.StringVar(),
            "unidad": tk.StringVar(value="Unidad"),
            "costo": tk.StringVar(value="0"),
            "margen": tk.StringVar(value="0"),
            "precio": tk.StringVar(value="0"),
            "stock": tk.StringVar(value="0"),
            "minimo": tk.StringVar(value="0"),
        }
        inputs = (
            ("Código / SKU", "codigo", 0, 0),
            ("Nombre", "nombre", 0, 2),
            ("Categoría", "categoria", 0, 4),
            ("Unidad", "unidad", 1, 0),
            ("Stock inicial", "stock", 1, 2),
            ("Stock mínimo", "minimo", 1, 4),
        )
        for label, key, row, column in inputs:
            self._field(form, label, key, row, column)
        self.cost_widgets = []
        if self.is_admin:
            for label, key, row, column in (
                ("Costo", "costo", 2, 0),
                ("Margen %", "margen", 2, 2),
                ("Precio de venta", "precio", 2, 4),
            ):
                self._field(form, label, key, row, column)
                self.cost_widgets.append(self.inputs[key])
            self.vars["costo"].trace_add("write", self._calcular_precio)
            self.vars["margen"].trace_add("write", self._calcular_precio)
        else:
            self._field(form, "Precio de venta", "precio", 2, 0)
        self.buttons = tk.Frame(form, bg=PANEL)
        self.buttons.grid(row=3, column=0, columnspan=6, sticky="e", pady=(4, 0))
        tk.Button(
            self.buttons, text="Limpiar", command=self.limpiar,
            bg="#353535", fg=TEXT, relief="flat", padx=12, pady=6,
        ).pack(side="left", padx=4)
        tk.Button(
            self.buttons, text="Guardar artículo", command=self.guardar,
            bg=ORANGE, fg="white", activebackground="#ff9500",
            relief="flat", padx=16, pady=6,
        ).pack(side="left", padx=4)
        tk.Button(
            self.buttons, text="Desactivar seleccionado", command=self.desactivar,
            bg="#8b2525", fg="white", relief="flat", padx=12, pady=6,
        ).pack(side="left", padx=4)

    def _field(self, parent, label, key, row, column):
        cell = tk.Frame(parent, bg=PANEL)
        cell.grid(row=row, column=column, columnspan=2, sticky="ew", padx=3, pady=1)
        tk.Label(cell, text=label, bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        if key == "categoria":
            widget = ttk.Combobox(
                cell, textvariable=self.vars[key], state="readonly",
            )
        elif key == "unidad":
            widget = ttk.Combobox(
                cell, textvariable=self.vars[key], state="readonly",
                values=("Unidad", "Metro", "Kilo", "Caja", "Litro"),
            )
        else:
            widget = tk.Entry(
                cell, textvariable=self.vars[key], bg=INPUT, fg=TEXT,
                insertbackground=TEXT, relief="flat",
            )
        widget.pack(fill="x", ipady=2)
        self.inputs = getattr(self, "inputs", {})
        self.inputs[key] = widget

    def _load_categories(self):
        categories = listar_categorias()
        self.categories = {category.nombre: category.id for category in categories}
        names = ["Sin categoría", *self.categories]
        self.inputs["categoria"].configure(values=names)
        self.category_filter.configure(values=["Todas", *self.categories])
        self.category_filter.set("Todas")

    def _schedule_refresh(self, *_):
        if self.search_job:
            self.after_cancel(self.search_job)
        self.search_job = self.after(180, self.refrescar)

    def refrescar(self):
        if not hasattr(self, "tree"):
            return
        category_id = self.categories.get(self.category_filter.get())
        articles = listar_articulos(
            texto=self.search_var.get(),
            categoria_id=category_id,
            bajo_stock=self.low_stock_var.get(),
        )
        for row in self.tree.get_children():
            self.tree.delete(row)
        for index, article in enumerate(articles):
            values = [
                article.codigo or "",
                article.nombre,
                article.categoria.nombre if article.categoria else "Sin categoría",
                article.unidad,
            ]
            if self.is_admin:
                values.extend((
                    f"${article.precio_compra:,.2f}",
                    f"{article.margen_porcentaje:g}%",
                    f"${article.precio_venta:,.2f}",
                ))
            values.extend((
                f"{article.stock_actual:g}",
                f"{article.stock_minimo:g}",
                "Editar",
            ))
            self.tree.insert(
                "", "end", iid=str(article.id), values=values,
                tags=("low" if article.stock_actual <= article.stock_minimo else
                      "even" if index % 2 == 0 else "odd",),
            )
        self.tree.tag_configure("low", foreground="#ff8b67")
        self.tree.tag_configure("even", background="#202020")
        self.tree.tag_configure("odd", background=PANEL)

    def _table_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        if self.tree.identify_column(event.x) == f"#{len(self.tree['columns'])}":
            row = self.tree.identify_row(event.y)
            if row:
                self.seleccionar(int(row))

    def _table_double_click(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.seleccionar(int(row))

    def seleccionar(self, article_id):
        article = next((item for item in listar_articulos() if item.id == article_id), None)
        if not article:
            messagebox.showerror("Artículo", "El artículo ya no está disponible.")
            return
        self.selected_id = article.id
        self.selected_article = article
        values = {
            "codigo": article.codigo or "",
            "nombre": article.nombre,
            "categoria": article.categoria.nombre if article.categoria else "Sin categoría",
            "unidad": article.unidad,
            "costo": str(article.precio_compra or 0),
            "margen": str(article.margen_porcentaje or 0),
            "precio": str(article.precio_venta or 0),
            "stock": str(article.stock_actual or 0),
            "minimo": str(article.stock_minimo or 0),
        }
        for key, value in values.items():
            self.vars[key].set(value)
        self.inputs["stock"].configure(state="disabled")
        self.inputs["stock"].master.winfo_children()[0].configure(text="Stock actual (solo lectura)")

    def _calcular_precio(self, *_):
        try:
            cost = float(self.vars["costo"].get().replace(",", "."))
            margin = float(self.vars["margen"].get().replace(",", "."))
            if cost >= 0 and margin >= 0:
                self.vars["precio"].set(f"{cost * (1 + margin / 100):.2f}")
        except ValueError:
            return

    def guardar(self):
        try:
            category_id = self.categories.get(self.vars["categoria"].get())
            cost = float(self.vars["costo"].get().replace(",", ".") or 0) if self.is_admin else (
                self.selected_article.precio_compra if self.selected_article else 0
            )
            margin = float(self.vars["margen"].get().replace(",", ".") or 0) if self.is_admin else (
                self.selected_article.margen_porcentaje if self.selected_article else 0
            )
            price = float(self.vars["precio"].get().replace(",", ".") or 0)
            stock = float(self.vars["stock"].get().replace(",", ".") or 0)
            minimum = float(self.vars["minimo"].get().replace(",", ".") or 0)
        except ValueError:
            messagebox.showerror("Datos inválidos", "Los precios y cantidades deben ser números.")
            return
        args = (
            self.vars["nombre"].get(),
            self.selected_article.descripcion if self.selected_article else "",
            category_id,
            cost,
            price,
            minimum,
            self.vars["codigo"].get(),
            self.vars["unidad"].get(),
            margin,
        )
        if self.selected_id:
            ok, message = editar_articulo(
                self.selected_id, *args, usuario_id=self.usuario_id
            )
        else:
            ok, message = crear_articulo(
                self.vars["codigo"].get(),
                self.vars["nombre"].get(),
                "",
                category_id,
                cost,
                price,
                stock,
                minimum,
                self.vars["unidad"].get(),
                margin,
                self.usuario_id,
            )
        if not ok:
            messagebox.showerror("No se pudo guardar", message)
            return
        messagebox.showinfo("Inventario", message)
        self.limpiar()
        self.refrescar()

    def limpiar(self):
        self.selected_id = None
        self.selected_article = None
        for key, variable in self.vars.items():
            variable.set("Unidad" if key == "unidad" else "0" if key in {
                "costo", "margen", "precio", "stock", "minimo",
            } else "")
        self.inputs["stock"].configure(state="normal")
        self.inputs["stock"].master.winfo_children()[0].configure(text="Stock inicial")
        self.tree.selection_remove(self.tree.selection())

    def desactivar(self):
        article_id = self.selected_id
        if not article_id:
            selection = self.tree.selection()
            article_id = int(selection[0]) if selection else None
        if not article_id:
            messagebox.showwarning("Inventario", "Seleccioná un artículo.")
            return
        if not messagebox.askyesno(
            "Confirmar desactivación",
            "El artículo dejará de aparecer en ventas y compras. ¿Continuar?",
        ):
            return
        ok, message = eliminar_articulo(article_id)
        if ok:
            self.limpiar()
            self.refrescar()
            messagebox.showinfo("Inventario", message)
        else:
            messagebox.showerror("Inventario", message)
