import tkinter as tk
from tkinter import messagebox, ttk

from routes.proveedores import (
    buscar_proveedores, crear_proveedor, editar_proveedor,
    eliminar_proveedor, listar_proveedores,
)
from ui.layout import ScrollableFrame, fit_tree_columns


BG, PANEL, INPUT = "#0f0f0f", "#1a1a1a", "#262626"
TEXT, MUTED, ORANGE = "#f5f5f5", "#9e9e9e", "#ff7b00"
FONT = "Segoe UI"


class ProveedoresFrame(tk.Frame):
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
        tk.Label(header, text="Proveedores", bg=PANEL, fg=TEXT, font=(FONT, 21, "bold")).pack(
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
        columns = ("nombre", "cuit", "contacto", "telefono", "email", "rubro", "accion")
        self.tree = ttk.Treeview(table_panel, columns=columns, show="headings", style="Punihard.Treeview")
        for col, title, width, anchor in (
            ("nombre", "Razón social", 220, "w"),
            ("cuit", "CUIT", 140, "w"),
            ("contacto", "Contacto", 170, "w"),
            ("telefono", "Teléfono", 125, "w"),
            ("email", "Email", 220, "w"),
            ("rubro", "Rubro", 150, "w"),
            ("accion", "Acción", 78, "center"),
        ):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor=anchor)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        fit_tree_columns(self.tree, {
            "nombre": 1.5, "cuit": 1, "contacto": 1.2, "telefono": 1,
            "email": 1.5, "rubro": 1, "accion": 0.7,
        })
        self.tree.bind("<Double-1>", self._seleccionar_evento)
        self.tree.bind("<Button-1>", self._click_editar)

        form = tk.LabelFrame(content, text="Alta / edición de proveedor", bg=PANEL, fg=TEXT,
                             font=(FONT, 10, "bold"), padx=8, pady=5)
        form.pack(fill="x")
        for column in range(6):
            form.columnconfigure(column, weight=1)
        self.vars = {key: tk.StringVar() for key in (
            "nombre", "cuit", "contacto", "telefono", "email", "rubro", "direccion",
        )}
        fields = (
            ("Razón social", "nombre", 0, 0), ("CUIT", "cuit", 0, 2),
            ("Contacto", "contacto", 0, 4), ("Teléfono", "telefono", 1, 0),
            ("Email", "email", 1, 2), ("Rubro", "rubro", 1, 4),
            ("Dirección", "direccion", 2, 0),
        )
        for label, key, row, column in fields:
            cell = tk.Frame(form, bg=PANEL)
            cell.grid(row=row, column=column, columnspan=2, sticky="ew", padx=3, pady=1)
            tk.Label(cell, text=label, bg=PANEL, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
            tk.Entry(cell, textvariable=self.vars[key], bg=INPUT, fg=TEXT,
                     insertbackground=TEXT, relief="flat").pack(fill="x", ipady=2)
        buttons = tk.Frame(form, bg=PANEL)
        buttons.grid(row=3, column=0, columnspan=6, sticky="e", pady=(4, 0))
        tk.Button(buttons, text="Limpiar", command=self.limpiar, bg="#353535",
                  fg=TEXT, relief="flat", padx=12, pady=6).pack(side="left", padx=4)
        tk.Button(buttons, text="Guardar proveedor", command=self.guardar, bg=ORANGE,
                  fg="white", relief="flat", padx=15, pady=6).pack(side="left", padx=4)
        tk.Button(buttons, text="Desactivar", command=self.desactivar, bg="#8b2525",
                  fg="white", relief="flat", padx=12, pady=6).pack(side="left", padx=4)

    def _schedule_refresh(self, *_):
        if self.search_job:
            self.after_cancel(self.search_job)
        self.search_job = self.after(180, self.refrescar)

    def refrescar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for provider in buscar_proveedores(self.search_var.get()):
            self.tree.insert(
                "", "end", iid=str(provider.id),
                values=(
                    provider.nombre, provider.cuit or "", provider.contacto or "",
                    provider.telefono or "", provider.email or "", provider.rubro or "",
                    "Editar",
                ),
            )

    def _click_editar(self, event):
        if self.tree.identify_region(event.x, event.y) == "cell" and self.tree.identify_column(event.x) == "#7":
            row = self.tree.identify_row(event.y)
            if row:
                self._load_provider(int(row))

    def _seleccionar_evento(self, event):
        row = self.tree.identify_row(event.y)
        if row:
            self._load_provider(int(row))

    def _load_provider(self, provider_id):
        provider = next((item for item in listar_proveedores() if item.id == provider_id), None)
        if provider:
            self.selected_id = provider.id
            for key in self.vars:
                self.vars[key].set(getattr(provider, key) or "")

    def guardar(self):
        values = {key: value.get().strip() for key, value in self.vars.items()}
        if not values["nombre"]:
            messagebox.showwarning("Proveedor", "La razón social es obligatoria.")
            return
        callback = editar_proveedor if self.selected_id else crear_proveedor
        args = (
            self.selected_id, values["nombre"], values["contacto"], values["telefono"],
            values["cuit"], values["email"], values["rubro"], values["direccion"],
        ) if self.selected_id else (
            values["nombre"], values["contacto"], values["telefono"],
            values["cuit"], values["email"], values["rubro"], values["direccion"],
        )
        ok, message = callback(*args)
        if ok:
            messagebox.showinfo("Proveedores", message)
            self.limpiar()
            self.refrescar()
        else:
            messagebox.showerror("Proveedores", message)

    def limpiar(self):
        self.selected_id = None
        for value in self.vars.values():
            value.set("")
        self.tree.selection_remove(self.tree.selection())

    def desactivar(self):
        selected = self.selected_id
        if not selected and self.tree.selection():
            selected = int(self.tree.selection()[0])
        if not selected:
            messagebox.showwarning("Proveedores", "Seleccioná un proveedor.")
            return
        if not messagebox.askyesno("Confirmar", "¿Desactivar este proveedor? El historial de compras se conserva."):
            return
        ok, message = eliminar_proveedor(selected)
        if ok:
            self.limpiar()
            self.refrescar()
            messagebox.showinfo("Proveedores", message)
        else:
            messagebox.showerror("Proveedores", message)
