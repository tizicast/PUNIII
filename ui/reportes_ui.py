import tkinter as tk
from tkinter import messagebox

from extensiones import get_db
from models import Venta, Compra, Cliente, Articulo

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


class ReportesFrame(tk.Frame):

    def __init__(self, parent):

        super().__init__(
            parent,
            bg=COLOR_FONDO
        )

        # =====================================
        # HEADER
        # =====================================

        header = tk.Frame(
            self,
            bg=COLOR_PANEL,
            height=80
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📊 Reportes del Sistema",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 22, "bold")
        ).pack(
            side="left",
            padx=25,
            pady=20
        )

        # =====================================
        # CONTENIDO
        # =====================================

        self.frame = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        self.frame.pack(
            fill="both",
            expand=True
        )

        self.refrescar()

    # =====================================
    # CARGAR DATOS
    # =====================================

    def refrescar(self):

        for widget in self.frame.winfo_children():
            widget.destroy()

        db = get_db()

        total_ventas = db.query(Venta).count()
        total_compras = db.query(Compra).count()
        total_clientes = db.query(Cliente).count()
        total_articulos = db.query(Articulo).count()

        stock_bajo = db.query(
            Articulo
        ).filter(
            Articulo.stock_actual <= 5
        ).count()

        # =====================================
        # KPIs
        # =====================================

        kpi_frame = tk.Frame(
            self.frame,
            bg=COLOR_FONDO
        )

        kpi_frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        datos = [
            ("📈 Ventas", total_ventas),
            ("🧾 Compras", total_compras),
            ("👥 Clientes", total_clientes),
            ("📦 Artículos", total_articulos)
        ]

        for titulo, valor in datos:

            card = tk.Frame(
                kpi_frame,
                bg=COLOR_CARD,
                width=220,
                height=120
            )

            card.pack(
                side="left",
                padx=10
            )

            card.pack_propagate(False)

            tk.Label(
                card,
                text=titulo,
                bg=COLOR_CARD,
                fg=COLOR_SECUNDARIO,
                font=(FUENTE, 11)
            ).pack(
                pady=(20, 5)
            )

            tk.Label(
                card,
                text=str(valor),
                bg=COLOR_CARD,
                fg=COLOR_NARANJA,
                font=(FUENTE, 24, "bold")
            ).pack()

        # =====================================
        # PANEL DE REPORTES
        # =====================================

        panel = tk.Frame(
            self.frame,
            bg=COLOR_PANEL
        )

        panel.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            panel,
            text="Acciones y Reportes",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(
            pady=(15, 20)
        )

        # =====================================
        # BOTÓN VENTAS
        # =====================================

        btn_ventas = tk.Button(
            panel,
            text="📈 Reporte de Ventas",
            bg=COLOR_NARANJA,
            fg="white",
            font=(FUENTE, 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=lambda: messagebox.showinfo(
                "Ventas",
                f"Total de ventas registradas: {total_ventas}"
            )
        )

        btn_ventas.pack(pady=8)

        hover(
            btn_ventas,
            COLOR_NARANJA,
            COLOR_NARANJA_HOVER
        )

        # =====================================
        # BOTÓN COMPRAS
        # =====================================

        btn_compras = tk.Button(
            panel,
            text="🧾 Reporte de Compras",
            bg=COLOR_NARANJA,
            fg="white",
            font=(FUENTE, 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=lambda: messagebox.showinfo(
                "Compras",
                f"Total de compras registradas: {total_compras}"
            )
        )

        btn_compras.pack(pady=8)

        hover(
            btn_compras,
            COLOR_NARANJA,
            COLOR_NARANJA_HOVER
        )

        # =====================================
        # BOTÓN STOCK BAJO
        # =====================================

        btn_stock = tk.Button(
            panel,
            text="📦 Artículos con Stock Bajo",
            bg=COLOR_ROJO,
            fg="white",
            font=(FUENTE, 11, "bold"),
            relief="flat",
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2",
            command=lambda: messagebox.showinfo(
                "Stock Bajo",
                f"Artículos con stock menor o igual a 5: {stock_bajo}"
            )
        )

        btn_stock.pack(
            pady=(8, 20)
        )

        hover(
            btn_stock,
            COLOR_ROJO,
            COLOR_ROJO_HOVER
        )