import tkinter as tk
from tkinter import messagebox, ttk

from routes.clientes import (
    crear_cliente, editar_cliente, eliminar_cliente,
    listar_clientes, buscar_clientes,
)
from ui.layout import ScrollableFrame, fit_tree_columns


BG, PANEL, INPUT = "#0f0f0f", "#1a1a1a", "#262626"
TEXT, MUTED, ORANGE = "#f5f5f5", "#9e9e9e", "#ff7b00"
FONT = "Segoe UI"


class ClientesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG)
        style = ttk.Style(parent)
        style.configure("Punihard.Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=24, font=(FONT, 10))
        style.configure("Punihard.Treeview.Heading", background="#292929",
                        foreground=TEXT, relief="flat", font=(FONT, 10, "bold"))
        self.selected_id = None
        self.search_job = None
        self._build()
        self.refrescar()

    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=68)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="Clientes", bg=PANEL, fg=TEXT, font=(FONT, 21, "bold")).pack(
            side="left", padx=24
        )
        scroll = ScrollableFrame(self, bg=BG)
        scroll.pack(fill="both", expand=True, padx=12, pady=8)
        content = scroll.content
        searchbar = tk.Frame(content, bg=BG)
        searchbar.pack(fill="x", pady=(0, 9))
        tk.Label(searchbar, text="Buscar", bg=BG, fg=MUTED).pack(side="left")
        self.search_var = tk.StringVar()
        tk.Entry(searchbar, textvariable=self.search_var, bg=INPUT, fg=TEXT,
                 insertbackground=TEXT, relief="flat").pack(
            side="left", fill="x", expand=True, padx=8, ipady=6
        )
        self.search_var.trace_add("write", self._schedule_refresh)
        table_panel = tk.Frame(content, bg=PANEL)
        table_panel.pack(fill="both", expand=True, pady=(0, 10))
        columns = ("nombre", "documento", "telefono", "direccion", "iva", "saldo", "accion")
        self.tree = ttk.Treeview(table_panel, columns=columns, show="headings", style="Punihard.Treeview")
        for col, title, width, anchor in (
            ("nombre", "Nombre / Razón social", 220, "w"),
            ("documento", "DNI / CUIT", 140, "w"),
            ("telefono", "Teléfono", 125, "w"),
            ("direccion", "Dirección", 230, "w"),
            ("iva", "Condición IVA", 150, "w"),
            ("saldo", "Saldo cta. cte.", 140, "e"),
            ("accion", "Acción", 78, "center"),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        fit_tree_columns(self.tree, {
            "nombre": 1.8, "documento": 1.1, "telefono": 1, "direccion": 1.7,
            "iva": 1.1, "saldo": 1, "accion": 0.7,
        })
        self.tree.bind("<Double-1>", self._seleccionar_evento)
        self.tree.bind("<Button-1>", self._click_editar)

        form = tk.LabelFrame(content, text="Alta / edición de cliente", bg=PANEL, fg=TEXT,
                             font=(FONT, 10, "bold"), padx=8, pady=5)
        form.pack(fill="x")
        for column in range(6):
            form.columnconfigure(column, weight=1)
        self.vars = {key: tk.StringVar() for key in (
            "nombre", "apellido", "dni_cuit", "telefono", "email", "direccion", "iva",
        )}
        fields = (
            ("Nombre / Razón social", "nombre", 0, 0),
            ("Apellido", "apellido", 0, 2),
            ("DNI / CUIT", "dni_cuit", 0, 4),
            ("Teléfono", "telefono", 1, 0),
            ("Email", "email", 1, 2),
            ("Dirección", "direccion", 1, 4),
        )
        self.inputs = {}
        for label, key, row, column in fields:
            self._field(form, label, key, row, column)
        self._field(form, "Condición IVA", "iva", 2, 0, values=(
            "Consumidor Final", "Responsable Inscripto", "Monotributista",
            "Exento", "No responsable",
        ))
        buttons = tk.Frame(form, bg=PANEL)
        buttons.grid(row=3, column=0, columnspan=6, sticky="e", pady=(4, 0))
        tk.Button(buttons, text="Limpiar", command=self.limpiar, bg="#353535",
                  fg=TEXT, relief="flat", padx=12, pady=6).pack(side="left", padx=4)
        tk.Button(buttons, text="Guardar cliente", command=self.guardar, bg=ORANGE,
                  fg="white", relief="flat", padx=15, pady=6).pack(side="left", padx=4)
        tk.Button(buttons, text="Desactivar", command=self.desactivar, bg="#8b2525",
                  fg="white", relief="flat", padx=12, pady=6).pack(side="left", padx=4)

    def _field(self, parent, label, key, row, column, values=None):
        cell = tk.Frame(parent, bg=PANEL)
        cell.grid(row=row, column=column, columnspan=2, sticky="ew", padx=3, pady=1)
        tk.Label(cell, text=label, bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        if values:
            widget = ttk.Combobox(cell, textvariable=self.vars[key], state="readonly", values=values)
        else:
            widget = tk.Entry(cell, textvariable=self.vars[key], bg=INPUT, fg=TEXT,
                              insertbackground=TEXT, relief="flat")
        widget.pack(fill="x", ipady=2)
        self.inputs[key] = widget

    def _schedule_refresh(self, *_):
        if self.search_job:
            self.after_cancel(self.search_job)
        self.search_job = self.after(180, self.refrescar)

    def refrescar(self):
        rows = buscar_clientes(self.search_var.get())
        for row in self.tree.get_children():
            self.tree.delete(row)
        for client in rows:
            self.tree.insert(
                "", "end", iid=str(client.id),
                values=(
                    client.nombre_completo, client.dni_cuit or "",
                    client.telefono or "", client.direccion or "",
                    client.condicion_iva or "", f"${client.saldo_cuenta_corriente:,.2f}",
                    "Editar",
                ),
            )

    def _click_editar(self, event):
        if self.tree.identify_region(event.x, event.y) == "cell" and self.tree.identify_column(event.x) == "#7":
            row = self.tree.identify_row(event.y)
            if row:
                self.seleccionar(int(row))

    def _seleccionar_evento(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self.seleccionar(int(row))

    def seleccionar(self, client_id):
        client = next((row for row in listar_clientes() if row.id == client_id), None)
        if not client:
            return
        self.selected_id = client.id
        for key, value in {
            "nombre": client.nombre, "apellido": client.apellido or "",
            "dni_cuit": client.dni_cuit or "", "telefono": client.telefono or "",
            "email": client.email or "", "direccion": client.direccion or "",
            "iva": client.condicion_iva or "Consumidor Final",
        }.items():
            self.vars[key].set(value)

    def guardar(self):
        values = {key: value.get().strip() for key, value in self.vars.items()}
        if not values["nombre"]:
            messagebox.showwarning("Cliente", "El nombre o razón social es obligatorio.")
            return
        callback = editar_cliente if self.selected_id else crear_cliente
        args = (
            self.selected_id, values["nombre"], values["apellido"], values["telefono"],
            values["dni_cuit"], values["email"], values["direccion"], values["iva"],
        ) if self.selected_id else (
            values["nombre"], values["apellido"], values["telefono"],
            values["dni_cuit"], values["email"], values["direccion"], values["iva"],
        )
        ok, message = callback(*args)
        if ok:
            messagebox.showinfo("Clientes", message)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showerror("Clientes", message)

    def limpiar(self):
        self.selected_id = None
        for key, variable in self.vars.items():
            variable.set("Consumidor Final" if key == "iva" else "")
        self.tree.selection_remove(self.tree.selection())

    def desactivar(self):
        selected = self.selected_id
        if not selected and self.tree.selection():
            selected = int(self.tree.selection()[0])
        if not selected:
            messagebox.showwarning("Clientes", "Seleccioná un cliente.")
            return
        if not messagebox.askyesno("Confirmar", "¿Desactivar este cliente? El historial de ventas se conserva."):
            return
        ok, message = eliminar_cliente(selected)
        if ok:
            self.limpiar()
            self.refrescar()
            messagebox.showinfo("Clientes", message)
        else:
            messagebox.showerror("Clientes", message)
