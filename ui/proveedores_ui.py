import tkinter as tk
from tkinter import messagebox, ttk

from routes.proveedores import (
    listar_proveedores,
    crear_proveedor,
    eliminar_proveedor
)

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"
COLOR_CARD = "#202020"
COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"
COLOR_ROJO = "#ef4444"
COLOR_ROJO_HOVER = "#dc2626"
COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"
COLOR_INPUT = "#262626"
COLOR_BORDE = "#2f2f2f"
FUENTE = "Segoe UI"

def hover(btn, normal, hover_color):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal))

class ProveedoresFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FONDO)

        # ==================================================
        # HEADER
        # ==================================================
        header = tk.Frame(self, bg=COLOR_PANEL, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="📦 Gestión de Proveedores",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 22, "bold")
        ).pack(side="left", padx=30, pady=20)

        # ==================================================
        # CONTENIDO PRINCIPAL
        # ==================================================
        contenido = tk.Frame(self, bg=COLOR_FONDO)
        contenido.pack(fill="both", expand=True, padx=25, pady=20)

        # ==================================================
        # PANEL LISTA (IZQUIERDA) - Renderizado Seguro
        # ==================================================
        panel_lista = tk.Frame(
            contenido, bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE, highlightthickness=1
        )
        panel_lista.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            panel_lista, text="📋 Proveedores registrados",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        canvas_container = tk.Frame(panel_lista, bg=COLOR_PANEL)
        canvas_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.canvas = tk.Canvas(canvas_container, bg=COLOR_PANEL, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.frame_lista = tk.Frame(self.canvas, bg=COLOR_PANEL)
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        
        self.frame_lista.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width))

        # ==================================================
        # PANEL FORMULARIO (DERECHA) - Espaciado Arreglado
        # ==================================================
        panel_form = tk.Frame(
            contenido, bg=COLOR_PANEL, width=360,
            highlightbackground=COLOR_BORDE, highlightthickness=1
        )
        panel_form.pack(side="right", fill="y")
        panel_form.pack_propagate(False)

        tk.Label(
            panel_form, text="➕ Nuevo proveedor",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # --- Nombre ---
        tk.Label(panel_form, text="Nombre / Razón Social", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_nombre = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_nombre.pack(fill="x", padx=20, pady=(8, 18), ipady=8)

        # --- Contacto ---
        tk.Label(panel_form, text="Nombre de Contacto", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_contacto = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_contacto.pack(fill="x", padx=20, pady=(8, 18), ipady=8)

        # --- Teléfono ---
        tk.Label(panel_form, text="Teléfono", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_telefono = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_telefono.pack(fill="x", padx=20, pady=(8, 30), ipady=8)

        # --- Botón Crear ---
        btn_crear = tk.Button(
            panel_form, text="➕ Crear proveedor", command=self.guardar,
            bg=COLOR_NARANJA, fg="white", activebackground=COLOR_NARANJA_HOVER, activeforeground="white",
            relief="flat", bd=0, cursor="hand2", font=(FUENTE, 11, "bold"), pady=12
        )
        btn_crear.pack(fill="x", padx=20)
        hover(btn_crear, COLOR_NARANJA, COLOR_NARANJA_HOVER)

        self.refrescar()

    # ======================================================
    # REFRESCAR LISTADO
    # ======================================================
    def refrescar(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        proveedores = listar_proveedores()
        if not proveedores:
            tk.Label(self.frame_lista, text="No hay proveedores registrados", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 11)).pack(pady=20)
            return

        for p in proveedores:
            info = f"📦 {p.nombre}\n👤 Contacto: {p.contacto or 'N/C'}  |  📞 {p.telefono or 'N/C'}"

            fila = tk.Frame(self.frame_lista, bg=COLOR_CARD, highlightbackground=COLOR_BORDE, highlightthickness=1)
            fila.pack(fill="x", pady=5, ipady=8, padx=10)

            tk.Label(fila, text=info, bg=COLOR_CARD, fg=COLOR_TEXTO, anchor="w", justify="left", font=(FUENTE, 10)).pack(side="left", padx=15, expand=True, fill="x")

            # Botón Eliminar con diseño limpio y funcional
            btn_delete = tk.Button(
                fila, text="Eliminar", command=lambda pid=p.id: self.borrar(pid),
                bg=COLOR_ROJO, fg="white", activebackground=COLOR_ROJO_HOVER, activeforeground="white",
                relief="flat", bd=0, cursor="hand2", font=(FUENTE, 9, "bold"), padx=15, pady=6
            )
            btn_delete.pack(side="right", padx=15)
            hover(btn_delete, COLOR_ROJO, COLOR_ROJO_HOVER)

    # ======================================================
    # GUARDAR PROVEEDOR
    # ======================================================
    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        contacto = self.entry_contacto.get().strip()
        telefono = self.entry_telefono.get().strip()

        if not nombre:
            messagebox.showwarning("Campos vacíos", "El campo Nombre / Razón Social es obligatorio.")
            return

        ok, msg = crear_proveedor(nombre, contacto, telefono)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.entry_nombre.delete(0, "end")
            self.entry_contacto.delete(0, "end")
            self.entry_telefono.delete(0, "end")
            self.refrescar()
        else:
            messagebox.showerror("Error", msg)

    # ======================================================
    # ELIMINAR PROVEEDOR
    # ======================================================
    def borrar(self, id):
        if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este proveedor?"):
            ok, msg = eliminar_proveedor(id)
            if ok:
                messagebox.showinfo("Información", msg)
                self.refrescar()
            else:
                messagebox.showerror("Error", msg)