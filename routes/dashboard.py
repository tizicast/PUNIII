import tkinter as tk
from tkinter import ttk

from routes.articulos import listar_articulos
from routes.ventas import listar_ventas
from routes.compras import listar_compras


# ======================================================
# COLORES - DARK ORANGE THEME
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"
COLOR_CARD = "#202020"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_BORDE = "#2a2a2a"

FUENTE = "Segoe UI"


# ======================================================
# HOVER BOTONES
# ======================================================

def hover_boton(btn, normal, hover):

    btn.bind(
        "<Enter>",
        lambda e: btn.config(bg=hover)
    )

    btn.bind(
        "<Leave>",
        lambda e: btn.config(bg=normal)
    )


# ======================================================
# CARD KPI
# ======================================================

def crear_card(parent, titulo, valor, icono):

    card = tk.Frame(
        parent,
        bg=COLOR_CARD,
        width=250,
        height=140,
        bd=0,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    card.pack_propagate(False)

    # ICONO
    tk.Label(
        card,
        text=icono,
        bg=COLOR_CARD,
        fg=COLOR_NARANJA,
        font=(FUENTE, 26)
    ).pack(anchor="w", padx=20, pady=(18, 5))

    # TITULO
    tk.Label(
        card,
        text=titulo,
        bg=COLOR_CARD,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=20)

    # VALOR
    tk.Label(
        card,
        text=valor,
        bg=COLOR_CARD,
        fg=COLOR_TEXTO,
        font=(FUENTE, 28, "bold")
    ).pack(anchor="w", padx=20, pady=(2, 0))

    return card


# ======================================================
# DASHBOARD
# ======================================================

def abrir_dashboard(usuario):

    # ==================================================
    # DATOS
    # ==================================================

    total_articulos = len(listar_articulos())
    total_ventas = len(listar_ventas())
    total_compras = len(listar_compras())

    # ==================================================
    # VENTANA
    # ==================================================

    ventana = tk.Tk()

    ventana.title("Dashboard")
    ventana.geometry("1200x700")
    ventana.configure(bg=COLOR_FONDO)

    ventana.minsize(1000, 650)

    # ==================================================
    # HEADER
    # ==================================================

    header = tk.Frame(
        ventana,
        bg=COLOR_PANEL,
        height=90
    )

    header.pack(fill="x")

    # LOGO / TITULO
    izquierda = tk.Frame(
        header,
        bg=COLOR_PANEL
    )

    izquierda.pack(side="left", padx=30)

    tk.Label(
        izquierda,
        text="⚡",
        bg=COLOR_PANEL,
        fg=COLOR_NARANJA,
        font=(FUENTE, 28)
    ).pack(side="left", padx=(0, 10), pady=20)

    tk.Label(
        izquierda,
        text="Dashboard",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 24, "bold")
    ).pack(side="left", pady=20)

    # USUARIO
    tk.Label(
        header,
        text=f"👤 {usuario.nombre}",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 12)
    ).pack(side="right", padx=30)

    # ==================================================
    # CONTENIDO
    # ==================================================

    contenido = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    contenido.pack(fill="both", expand=True, padx=35, pady=30)

    # ==================================================
    # TITULO
    # ==================================================

    tk.Label(
        contenido,
        text="Resumen General",
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO,
        font=(FUENTE, 22, "bold")
    ).pack(anchor="w")

    tk.Label(
        contenido,
        text="Visualización rápida del estado del sistema",
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(anchor="w", pady=(5, 30))

    # ==================================================
    # GRID DE TARJETAS
    # ==================================================

    cards = tk.Frame(
        contenido,
        bg=COLOR_FONDO
    )

    cards.pack()

    crear_card(
        cards,
        "Artículos",
        total_articulos,
        "📦"
    ).grid(row=0, column=0, padx=15)

    crear_card(
        cards,
        "Ventas",
        total_ventas,
        "💰"
    ).grid(row=0, column=1, padx=15)

    crear_card(
        cards,
        "Compras",
        total_compras,
        "🧾"
    ).grid(row=0, column=2, padx=15)

    # ==================================================
    # PANEL INFERIOR
    # ==================================================

    panel = tk.Frame(
        contenido,
        bg=COLOR_PANEL,
        height=220,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    panel.pack(fill="x", pady=40)

    panel.pack_propagate(False)

    # TITULO PANEL
    tk.Label(
        panel,
        text="🚀 Estado del sistema",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 16, "bold")
    ).pack(anchor="w", padx=25, pady=(25, 10))

    # TEXTO
    descripcion = (
        "Sistema operativo correctamente.\n\n"
        "Gestioná artículos, ventas y compras desde un panel moderno.\n\n"
        "Diseño minimalista con tema oscuro profesional."
    )

    tk.Label(
        panel,
        text=descripcion,
        justify="left",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=25)

    # ==================================================
    # BOTONES
    # ==================================================

    botones = tk.Frame(
        contenido,
        bg=COLOR_FONDO
    )

    botones.pack(pady=10)

    btn1 = tk.Button(
        botones,
        text="📦 Ver artículos",
        bg=COLOR_NARANJA,
        fg="white",
        activebackground=COLOR_NARANJA_HOVER,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        font=(FUENTE, 11, "bold"),
        padx=25,
        pady=12,
        bd=0
    )

    btn1.grid(row=0, column=0, padx=10)

    hover_boton(
        btn1,
        COLOR_NARANJA,
        COLOR_NARANJA_HOVER
    )

    btn2 = tk.Button(
        botones,
        text="💰 Ver ventas",
        bg="#262626",
        fg=COLOR_TEXTO,
        activebackground="#303030",
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        font=(FUENTE, 11, "bold"),
        padx=25,
        pady=12,
        bd=0
    )

    btn2.grid(row=0, column=1, padx=10)

    hover_boton(
        btn2,
        "#262626",
        "#303030"
    )

    # ==================================================
    # FOOTER
    # ==================================================

    footer = tk.Frame(
        ventana,
        bg=COLOR_PANEL,
        height=40
    )

    footer.pack(fill="x")

    tk.Label(
        footer,
        text="Sistema de Gestión • Punihard System",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 9)
    ).pack(pady=10)

    ventana.mainloop()