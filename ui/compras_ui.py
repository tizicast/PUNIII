import tkinter as tk
from tkinter import messagebox

from routes.compras import (
    listar_compras,
    crear_compra
)


# ======================================================
# COLORES - DARK ORANGE UI
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"
COLOR_CARD = "#202020"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_INPUT = "#262626"
COLOR_BORDE = "#2f2f2f"

FUENTE = "Segoe UI"


# ======================================================
# HOVER
# ======================================================

def hover(btn, normal, hover_color):

    btn.bind(
        "<Enter>",
        lambda e: btn.config(bg=hover_color)
    )

    btn.bind(
        "<Leave>",
        lambda e: btn.config(bg=normal)
    )


# ======================================================
# FRAME COMPRAS
# ======================================================

class ComprasFrame(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent, bg=COLOR_FONDO)

        # ==================================================
        # HEADER
        # ==================================================

        header = tk.Frame(
            self,
            bg=COLOR_PANEL,
            height=90
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🧾 Gestión de Compras",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 22, "bold")
        ).pack(side="left", padx=30, pady=25)

        # ==================================================
        # CONTENIDO
        # ==================================================

        contenido = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        contenido.pack(fill="both", expand=True, padx=25, pady=25)

        # ==================================================
        # PANEL LISTA
        # ==================================================

        panel_lista = tk.Frame(
            contenido,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )

        panel_lista.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        tk.Label(
            panel_lista,
            text="📋 Compras registradas",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        self.frame_lista = tk.Frame(
            panel_lista,
            bg=COLOR_PANEL
        )

        self.frame_lista.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # ==================================================
        # PANEL FORMULARIO
        # ==================================================

        panel_form = tk.Frame(
            contenido,
            bg=COLOR_PANEL,
            width=350,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )

        panel_form.pack(side="right", fill="y")
        panel_form.pack_propagate(False)

        tk.Label(
            panel_form,
            text="➕ Nueva compra",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # ==================================================
        # NUMERO
        # ==================================================

        tk.Label(
            panel_form,
            text="Número",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_numero = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_numero.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # PROVEEDOR
        # ==================================================

        tk.Label(
            panel_form,
            text="Proveedor ID",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_proveedor = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_proveedor.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # TOTAL
        # ==================================================

        tk.Label(
            panel_form,
            text="Total",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_total = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_total.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # OBSERVACIONES
        # ==================================================

        tk.Label(
            panel_form,
            text="Observaciones",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_obs = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_obs.pack(
            fill="x",
            padx=20,
            pady=(8, 30),
            ipady=10
        )

        # ==================================================
        # BOTON CREAR
        # ==================================================

        btn_crear = tk.Button(
            panel_form,
            text="➕ Crear compra",
            command=self.guardar,
            bg=COLOR_NARANJA,
            fg="white",
            activebackground=COLOR_NARANJA_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FUENTE, 11, "bold"),
            pady=12
        )

        btn_crear.pack(
            fill="x",
            padx=20
        )

        hover(
            btn_crear,
            COLOR_NARANJA,
            COLOR_NARANJA_HOVER
        )

        # ==================================================
        # CARGAR COMPRAS
        # ==================================================

        self.refrescar()

    # ======================================================
    # REFRESCAR
    # ======================================================

    def refrescar(self):

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        compras = listar_compras()

        # ==================================================
        # VACIO
        # ==================================================

        if not compras:

            tk.Label(
                self.frame_lista,
                text="No hay compras registradas",
                bg=COLOR_PANEL,
                fg=COLOR_SECUNDARIO,
                font=(FUENTE, 11)
            ).pack(pady=20)

            return

        # ==================================================
        # LISTADO
        # ==================================================

        for c in compras:

            fila = tk.Frame(
                self.frame_lista,
                bg=COLOR_CARD,
                highlightbackground=COLOR_BORDE,
                highlightthickness=1
            )

            fila.pack(
                fill="x",
                pady=6,
                ipady=10
            )

            info = (
                f"🧾 Compra #{c.numero}   |   "
                f"💰 Total: ${c.total}"
            )

            tk.Label(
                fila,
                text=info,
                bg=COLOR_CARD,
                fg=COLOR_TEXTO,
                anchor="w",
                font=(FUENTE, 10)
            ).pack(
                side="left",
                padx=15,
                expand=True,
                fill="x"
            )

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(self):

        ok, msg = crear_compra(
            self.entry_numero.get(),
            int(self.entry_proveedor.get() or 0),
            float(self.entry_total.get() or 0),
            self.entry_obs.get()
        )

        messagebox.showinfo(
            "Información",
            msg
        )

        if ok:

            self.entry_numero.delete(0, "end")
            self.entry_proveedor.delete(0, "end")
            self.entry_total.delete(0, "end")
            self.entry_obs.delete(0, "end")

            self.refrescar()