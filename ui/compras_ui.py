import tkinter as tk
from tkinter import messagebox, ttk

from routes.compras import (
    listar_compras,
    crear_compra,
    eliminar_compra
)

# Paleta Dark Orange de Punihard
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

class ComprasFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=COLOR_FONDO)

        # ==================================================
        # HEADER (TÍTULO PRINCIPAL)
        # ==================================================
        header = tk.Frame(self, bg=COLOR_PANEL, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="🧾 Gestión de Compras",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 22, "bold")
        ).pack(side="left", padx=30, pady=20)

        # ==================================================
        # CONTENIDO PRINCIPAL (DISTRIBUCIÓN)
        # ==================================================
        contenido = tk.Frame(self, bg=COLOR_FONDO)
        contenido.pack(fill="both", expand=True, padx=25, pady=20)

        # ==================================================
        # PANEL DE LISTADO (IZQUIERDA) con Scrollbar de Seguridad
        # ==================================================
        panel_lista = tk.Frame(
            contenido, bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE, highlightthickness=1
        )
        panel_lista.pack(side="left", fill="both", expand=True, padx=(0, 20))

        tk.Label(
            panel_lista, text="📋 Compras registradas",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        # Contenedor del Canvas
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

        # Evita la pantalla en negro redimensionando proporcionalmente
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window_id, width=e.width))

        # ==================================================
        # PANEL FORMULARIO (DERECHA) - Espaciado e Inputs
        # ==================================================
        panel_form = tk.Frame(
            contenido, bg=COLOR_PANEL, width=360,
            highlightbackground=COLOR_BORDE, highlightthickness=1
        )
        panel_form.pack(side="right", fill="y")
        panel_form.pack_propagate(False)

        tk.Label(
            panel_form, text="➕ Nueva compra",
            bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # --- Campo: Número ---
        tk.Label(panel_form, text="Número de Comprobante / Factura", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_numero = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_numero.pack(fill="x", padx=20, pady=(8, 18), ipady=8)

        # --- Campo: Proveedor ID ---
        tk.Label(panel_form, text="ID del Proveedor", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_proveedor = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_proveedor.pack(fill="x", padx=20, pady=(8, 18), ipady=8)

        # --- Campo: Total ---
        tk.Label(panel_form, text="Total ($)", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_total = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_total.pack(fill="x", padx=20, pady=(8, 18), ipady=8)

        # --- Campo: Observaciones ---
        tk.Label(panel_form, text="Observaciones", bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 10)).pack(anchor="w", padx=20)
        self.entry_obs = tk.Entry(panel_form, bg=COLOR_INPUT, fg="white", insertbackground="white", relief="flat", font=(FUENTE, 11))
        self.entry_obs.pack(fill="x", padx=20, pady=(8, 30), ipady=8)

        # --- Botón Guardar Transacción ---
        btn_crear = tk.Button(
            panel_form, text="➕ Registrar compra", command=self.guardar,
            bg=COLOR_NARANJA, fg="white", activebackground=COLOR_NARANJA_HOVER, activeforeground="white",
            relief="flat", bd=0, cursor="hand2", font=(FUENTE, 11, "bold"), pady=12
        )
        btn_crear.pack(fill="x", padx=20)
        hover(btn_crear, COLOR_NARANJA, COLOR_NARANJA_HOVER)

        # Cargar los datos al iniciar
        self.refrescar()

    # ======================================================
    # REFRESCAR Y RENDERIZAR COMPRAS
    # ======================================================
    def refrescar(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        compras = listar_compras()
        if not compras:
            tk.Label(
                self.frame_lista, text="No hay transacciones de compra registradas", 
                bg=COLOR_PANEL, fg=COLOR_SECUNDARIO, font=(FUENTE, 11)
            ).pack(pady=20)
            return

        for c in compras:
            # Intentar formatear la fecha de forma amigable
            fecha_str = c.fecha.strftime('%d/%m/%Y %H:%M') if hasattr(c, "fecha") and c.fecha else ""
            info = f"🧾 Comprobante: {c.numero}   |   💰 Total: ${c.total:,.2f}\n📅 Fecha: {fecha_str}   |   📝 Obs: {c.observaciones or 'Ninguna'}"

            fila = tk.Frame(self.frame_lista, bg=COLOR_CARD, highlightbackground=COLOR_BORDE, highlightthickness=1)
            fila.pack(fill="x", pady=5, ipady=8, padx=10)

            tk.Label(
                fila, text=info, bg=COLOR_CARD, fg=COLOR_TEXTO, 
                anchor="w", justify="left", font=(FUENTE, 10)
            ).pack(side="left", padx=15, expand=True, fill="x")

            # Botón Eliminar Integrado por Tarjeta
            btn_delete = tk.Button(
                fila, text="Eliminar", command=lambda cid=c.id: self.borrar(cid),
                bg=COLOR_ROJO, fg="white", activebackground=COLOR_ROJO_HOVER, activeforeground="white",
                relief="flat", bd=0, cursor="hand2", font=(FUENTE, 9, "bold"), padx=15, pady=6
            )
            btn_delete.pack(side="right", padx=15)
            hover(btn_delete, COLOR_ROJO, COLOR_ROJO_HOVER)

    # ======================================================
    # GUARDAR PROCESO COMPRA
    # ======================================================
    def guardar(self):
        numero = self.entry_numero.get().strip()
        proveedor_str = self.entry_proveedor.get().strip()
        total_str = self.entry_total.get().strip()
        obs = self.entry_obs.get().strip()

        if not numero or not proveedor_str:
            messagebox.showwarning("Campos vacíos", "El Número de comprobante y el ID del Proveedor son requeridos.")
            return

        try:
            proveedor_id = int(proveedor_str)
        except ValueError:
            messagebox.showerror("Dato Incorrecto", "El ID del Proveedor debe ser un número entero válido.")
            return

        try:
            total = float(total_str) if total_str else 0.0
        except ValueError:
            messagebox.showerror("Dato Incorrecto", "El monto Total debe ser un número decimal válido.")
            return

        ok, msg = crear_compra(numero, proveedor_id, total, obs)
        if ok:
            messagebox.showinfo("Éxito", msg)
            self.entry_numero.delete(0, "end")
            self.entry_proveedor.delete(0, "end")
            self.entry_total.delete(0, "end")
            self.entry_obs.delete(0, "end")
            self.refrescar()
        else:
            messagebox.showerror("Error", msg)

    # ======================================================
    # ACCIÓN BORRAR COMPRA
    # ======================================================
    def borrar(self, id_compra):
        if messagebox.askyesno("Confirmar Acción", "¿Seguro que desea eliminar esta compra del registro activo?"):
            ok, msg = eliminar_compra(id_compra)
            if ok:
                messagebox.showinfo("Información", msg)
                self.refrescar()
            else:
                messagebox.showerror("Error", msg)