import tkinter as tk
from tkinter import ttk

from routes.articulos import listar_articulos
from routes.ventas import listar_ventas
from routes.compras import listar_compras


# =========================================
# COLORES Y ESTILOS
# =========================================

COLOR_FONDO = "#0f172a"
COLOR_PANEL = "#1e293b"
COLOR_CARD = "#334155"

COLOR_TEXTO = "#f8fafc"
COLOR_SECUNDARIO = "#94a3b8"

COLOR_AZUL = "#3b82f6"
COLOR_VERDE = "#22c55e"
COLOR_NARANJA = "#f59e0b"

FUENTE = "Segoe UI"


# =========================================
# EFECTO HOVER
# =========================================

def hover_boton(btn, color_normal, color_hover):
    btn.bind("<Enter>", lambda e: btn.config(bg=color_hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=color_normal))


# =========================================
# TARJETAS KPI
# =========================================

def crear_card(parent, titulo, valor, color):

    card = tk.Frame(
        parent,
        bg=COLOR_CARD,
        width=220,
        height=120,
        bd=0,
        highlightthickness=0
    )

    card.pack_propagate(False)

    tk.Label(
        card,
        text=titulo,
        bg=COLOR_CARD,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=18, pady=(18, 5))

    tk.Label(
        card,
        text=valor,
        bg=COLOR_CARD,
        fg=color,
        font=(FUENTE, 24, "bold")
    ).pack(anchor="w", padx=18)

    return card


# =========================================
# DASHBOARD
# =========================================

def abrir_dashboard(usuario):

    # =========================
    # DATOS
    # =========================

    total_articulos = len(listar_articulos())
    total_ventas = len(listar_ventas())
    total_compras = len(listar_compras())

    # =========================
    # VENTANA
    # =========================

    ventana = tk.Tk()

    ventana.title("Dashboard")
    ventana.geometry("1000x600")
    ventana.configure(bg=COLOR_FONDO)

    # Evita que se pueda hacer demasiado pequeña
    ventana.minsize(900, 550)

    # =========================
    # HEADER
    # =========================

    header = tk.Frame(
        ventana,
        bg=COLOR_PANEL,
        height=90
    )

    header.pack(fill="x")

    tk.Label(
        header,
        text="📊 Dashboard",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 24, "bold")
    ).pack(side="left", padx=30, pady=20)

    tk.Label(
        header,
        text=f"Bienvenido, {usuario.nombre}",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 12)
    ).pack(side="right", padx=30)

    # =========================
    # CONTENEDOR PRINCIPAL
    # =========================

    contenido = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    contenido.pack(fill="both", expand=True, padx=30, pady=30)

    # =========================
    # TITULO SECCION
    # =========================

    tk.Label(
        contenido,
        text="Resumen general del sistema",
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO,
        font=(FUENTE, 18, "bold")
    ).pack(anchor="w", pady=(0, 20))

    # =========================
    # GRID DE TARJETAS
    # =========================

    grid = tk.Frame(
        contenido,
        bg=COLOR_FONDO
    )

    grid.pack()

    crear_card(
        grid,
        "📦 Artículos",
        total_articulos,
        COLOR_AZUL
    ).grid(row=0, column=0, padx=15, pady=15)

    crear_card(
        grid,
        "💰 Ventas",
        total_ventas,
        COLOR_VERDE
    ).grid(row=0, column=1, padx=15, pady=15)

    crear_card(
        grid,
        "🧾 Compras",
        total_compras,
        COLOR_NARANJA
    ).grid(row=0, column=2, padx=15, pady=15)

    # =========================
    # PANEL INFERIOR
    # =========================

    panel_info = tk.Frame(
        contenido,
        bg=COLOR_PANEL,
        height=180
    )

    panel_info.pack(fill="x", pady=40)

    tk.Label(
        panel_info,
        text="📌 Información del sistema",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 14, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))

    info_texto = (
        "• Gestioná artículos, ventas y compras desde un solo lugar.\n\n"
        "• Visualizá estadísticas rápidas del negocio.\n\n"
        "• Sistema moderno desarrollado con Python + Tkinter."
    )

    tk.Label(
        panel_info,
        text=info_texto,
        justify="left",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=20)

    # =========================
    # FOOTER
    # =========================

    footer = tk.Frame(
        ventana,
        bg=COLOR_PANEL,
        height=40
    )

    footer.pack(fill="x")

    tk.Label(
        footer,
        text="Sistema de Gestión • Python",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 9)
    ).pack(pady=10)

    ventana.mainloop()