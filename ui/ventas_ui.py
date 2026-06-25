import tkinter as tk
from tkinter import messagebox

from routes.ventas import (
    listar_ventas,
    crear_venta,
    eliminar_venta
)


# ======================================================
# COLORES - DARK ORANGE UI
# ======================================================

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
# FRAME VENTAS
# ======================================================

class VentasFrame(tk.Frame):

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
            text="💰 Gestión de Ventas",
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
            text="📋 Ventas registradas",
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
            text="➕ Nueva venta",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # ==================================================
        # NUMERO
        # ==================================================

        tk.Label(
            panel_form,
            text="Número de venta",
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
            pady=(8, 30),
            ipady=10
        )

        # ==================================================
        # BOTON CREAR
        # ==================================================

        btn_crear = tk.Button(
            panel_form,
            text="➕ Crear venta",
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
        # CARGAR VENTAS
        # ==================================================

        self.refrescar()

    # ======================================================
    # REFRESCAR
    # ======================================================

    def refrescar(self):

        for w in self.frame_lista.winfo_children():
            w.destroy()

        ventas = listar_ventas()

        # ==================================================
        # VACIO
        # ==================================================

        if not ventas:

            tk.Label(
                self.frame_lista,
                text="No hay ventas registradas",
                bg=COLOR_PANEL,
                fg=COLOR_SECUNDARIO,
                font=(FUENTE, 11)
            ).pack(pady=20)

            return

        # ==================================================
        # LISTADO
        # ==================================================

        for v in ventas:

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
                f"💰 Venta #{v.numero}"
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

            # ==================================================
            # ELIMINAR
            # ==================================================

            btn_delete = tk.Button(
                fila,
                text="Eliminar",
                command=lambda vid=v.id: self.eliminar(vid),
                bg=COLOR_ROJO,
                fg="white",
                activebackground=COLOR_ROJO_HOVER,
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=(FUENTE, 9, "bold"),
                padx=15,
                pady=6
            )

            btn_delete.pack(
                side="right",
                padx=10
            )

            hover(
                btn_delete,
                COLOR_ROJO,
                COLOR_ROJO_HOVER
            )

    # ======================================================
    # ELIMINAR
    # ======================================================

    def eliminar(self, id):

        eliminar_venta(id)

        self.refrescar()

        messagebox.showinfo(
            "OK",
            "Venta eliminada"
        )

    # ======================================================
    # CREAR
    # ======================================================

    def guardar(self):

        ok, msg = crear_venta(
            self.entry_numero.get()
        )

        messagebox.showinfo(
            "Información",
            msg
        )

        if ok:

            self.entry_numero.delete(0, "end")

            self.refrescar()