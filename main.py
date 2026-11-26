import tkinter as tk

from extensiones import Base, engine
from seed import seed_initial_data
from ui.login_ui import ventana_login

# UI
from ui import clientes_ui
from ui import proveedores_ui
from ui import compras_ui
from ui import ventas_ui
from ui import remitos_ui
from ui import reportes_ui
from ui import usuarios_ui
from ui import articulos_ui
from ui import dashboard_ui
from ui.layout import set_compact_scaling


# ======================================================
# COLORES - DARK ORANGE UI
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_SIDEBAR = "#171717"
COLOR_PANEL = "#1f1f1f"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_BORDE = "#2c2c2c"

FUENTE = "Segoe UI"


# ======================================================
# INIT DB
# ======================================================

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


# ======================================================
# HOVER BOTONES
# ======================================================

def hover_boton(btn):

    btn.bind(
        "<Enter>",
        lambda e: btn.config(bg=COLOR_NARANJA_HOVER)
    )

    btn.bind(
        "<Leave>",
        lambda e: btn.config(bg=COLOR_SIDEBAR)
    )


# ======================================================
# CAMBIAR FRAME
# ======================================================

def mostrar_frame(container, frame_class):

    for widget in container.winfo_children():
        widget.destroy()

    frame = frame_class(container)
    frame.pack(fill="both", expand=True)


# ======================================================
# CREAR BOTÓN SIDEBAR
# ======================================================

def crear_boton_sidebar(parent, texto, comando):

    btn = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=COLOR_SIDEBAR,
        fg=COLOR_TEXTO,
        activebackground=COLOR_NARANJA,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",

        # =====================
        # TAMAÑO MÁS CHICO
        # =====================

        anchor="w",
        padx=12,
        pady=5,

        font=(FUENTE, 9, "bold"),

        # altura visual más compacta
        height=1
    )

    hover_boton(btn)

    return btn


# ======================================================
# MAIN MENU
# ======================================================

def main_menu(usuario):

    ventana = tk.Tk()
    set_compact_scaling(ventana)

    ventana.title("Sistema")
    ventana.geometry("1400x800")

# Pantalla completa/maximizada
    ventana.state("zoomed")
    ventana.configure(bg=COLOR_FONDO)

    ventana.minsize(960, 620)

    try:
        ventana.iconbitmap("punihard.ico")
    except:
        pass

    # ==================================================
    # SIDEBAR
    # ==================================================

    sidebar = tk.Frame(
        ventana,
        width=190,
        bg=COLOR_SIDEBAR
    )

    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    # ==================================================
    # LOGO / TITULO
    # ==================================================

    top_sidebar = tk.Frame(
        sidebar,
        bg=COLOR_SIDEBAR
    )

    top_sidebar.pack(fill="x", pady=(16, 10))

    label_icon = tk.Label(
        top_sidebar,
        text="⚡",
        bg=COLOR_SIDEBAR,
        fg=COLOR_NARANJA,
        font=(FUENTE, 27),
        cursor="hand2"
    )
    label_icon.pack()
    label_icon.bind(
        "<Button-1>",
        lambda e: mostrar_frame(container, dashboard_ui.DashboardFrame)
    )

    label_title = tk.Label(
        top_sidebar,
        text="Punihard",
        bg=COLOR_SIDEBAR,
        fg=COLOR_TEXTO,
        font=(FUENTE, 17, "bold"),
        cursor="hand2"
    )
    label_title.pack()
    label_title.bind(
        "<Button-1>",
        lambda e: mostrar_frame(container, dashboard_ui.DashboardFrame)
    )

    label_sub = tk.Label(
        top_sidebar,
        text="Sistema de Gestión",
        bg=COLOR_SIDEBAR,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 10),
        cursor="hand2"
    )
    label_sub.pack(pady=(0, 10))
    label_sub.bind(
        "<Button-1>",
        lambda e: mostrar_frame(container, dashboard_ui.DashboardFrame)
    )

    # ==================================================
    # USUARIO
    # ==================================================

    usuario_frame = tk.Frame(
        sidebar,
        bg=COLOR_PANEL,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    usuario_frame.pack(fill="x", padx=15, pady=10)

    tk.Label(
        usuario_frame,
        text="👤 Usuario conectado",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 10)
    ).pack(anchor="w", padx=15, pady=(12, 0))

    tk.Label(
        usuario_frame,
        text=usuario.nombre,
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 13, "bold")
    ).pack(anchor="w", padx=15)

    tk.Label(
        usuario_frame,
        text=f"Rol: {usuario.rol}",
        bg=COLOR_PANEL,
        fg=COLOR_NARANJA,
        font=(FUENTE, 10)
    ).pack(anchor="w", padx=15, pady=(0, 12))

    # ==================================================
    # BOTONES MENU
    # ==================================================

    menu = tk.Frame(
        sidebar,
        bg=COLOR_SIDEBAR
    )

    menu.pack(fill="x", pady=15)

    crear_boton_sidebar(
        menu,
        "📦  Artículos",
        lambda: mostrar_frame(
            container, lambda parent: articulos_ui.ArticulosFrame(parent, usuario)
        )
    ).pack(fill="x", pady=1, padx=10)

    crear_boton_sidebar(
        menu,
        "👥  Clientes",
        lambda: mostrar_frame(container, clientes_ui.ClientesFrame)
    ).pack(fill="x", pady=1, padx=10)

    crear_boton_sidebar(
        menu,
        "🏭  Proveedores",
        lambda: mostrar_frame(container, proveedores_ui.ProveedoresFrame)
    ).pack(fill="x", pady=1, padx=10)

    crear_boton_sidebar(
        menu,
        "🛒  Compras",
        lambda: mostrar_frame(container, compras_ui.ComprasFrame)
    ).pack(fill="x", pady=1, padx=10)

    crear_boton_sidebar(
        menu,
        "💰  Ventas",
        lambda: mostrar_frame(container, ventas_ui.VentasFrame)
    ).pack(fill="x", pady=1, padx=10)

    crear_boton_sidebar(
        menu,
        "📄  Remitos",
        lambda: mostrar_frame(container, remitos_ui.RemitosFrame)
    ).pack(fill="x", pady=1, padx=10)

    if usuario.rol == "admin":
        crear_boton_sidebar(
            menu,
            "📊  Reportes",
            lambda: mostrar_frame(
                container, lambda parent: reportes_ui.ReportesFrame(parent, usuario)
            )
        ).pack(fill="x", pady=1, padx=10)

    # ==================================================
    # SOLO ADMIN
    # ==================================================

    if usuario.rol == "admin":

        crear_boton_sidebar(
            menu,
            "⚙️  Usuarios",
            lambda: mostrar_frame(
                container,
                lambda parent: usuarios_ui.UsuariosFrame(parent, usuario)
            )
        ).pack(fill="x", pady=1, padx=10)

    # ==================================================
    # FOOTER SIDEBAR
    # ==================================================

    footer_sidebar = tk.Frame(
        sidebar,
        bg=COLOR_SIDEBAR
    )

    footer_sidebar.pack(side="bottom", fill="x", pady=15)

    tk.Label(
        footer_sidebar,
        text="© 2026 Punihard - Todos los derechos reservados",
        bg=COLOR_SIDEBAR,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 9)
    ).pack()

    # ==================================================
    # CONTENIDO PRINCIPAL
    # ==================================================

    container = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    container.pack(side="right", fill="both", expand=True)
    container.menu_actions = {
        "ventas": lambda: mostrar_frame(container, ventas_ui.VentasFrame),
        "articulos": lambda: mostrar_frame(
            container, lambda parent: articulos_ui.ArticulosFrame(parent, usuario)
        ),
        "compras": lambda: mostrar_frame(container, compras_ui.ComprasFrame),
    }

    dashboard_ui.DashboardFrame(container, usuario).pack(fill="both", expand=True)
    ventana.bind("<F2>", lambda _event: container.menu_actions["ventas"]())

    ventana.mainloop()


# ======================================================
# START
# ======================================================

if __name__ == "__main__":
    init_db()
    ventana_login(on_success=main_menu)