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
    Base.metadata.drop_all(bind=engine)
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


def mostrar_home(container):

    for widget in container.winfo_children():
        widget.destroy()

    # HEADER
    header = tk.Frame(
        container,
        bg=COLOR_PANEL,
        height=80
    )

    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="📊 Panel Principal",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 22, "bold")
    ).pack(side="left", padx=30, pady=20)

    tk.Label(
        header,
        text="Sistema de gestión ferretería",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(side="right", padx=30)

    # HOME
    home = tk.Frame(
        container,
        bg=COLOR_FONDO
    )

    home.pack(fill="both", expand=True)

    tk.Label(
        home,
        text="⚡ Bienvenido al sistema",
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO,
        font=(FUENTE, 28, "bold")
    ).pack(pady=(120, 10))

    tk.Label(
        home,
        text="Seleccioná una opción del menú lateral",
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 13)
    ).pack()


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
        padx=16,
        pady=8,

        font=(FUENTE, 10, "bold"),

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

    ventana.title("Sistema")
    ventana.geometry("1400x800")

# Pantalla completa/maximizada
    ventana.state("zoomed")
    ventana.configure(bg=COLOR_FONDO)

    ventana.minsize(1200, 700)

    try:
        ventana.iconbitmap("punihard.ico")
    except:
        pass

    # ==================================================
    # SIDEBAR
    # ==================================================

    sidebar = tk.Frame(
        ventana,
        width=220,
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

    top_sidebar.pack(fill="x", pady=(25, 15))

    label_icon = tk.Label(
        top_sidebar,
        text="⚡",
        bg=COLOR_SIDEBAR,
        fg=COLOR_NARANJA,
        font=(FUENTE, 32),
        cursor="hand2"
    )
    label_icon.pack()
    label_icon.bind(
        "<Button-1>",
        lambda e: mostrar_frame(container, dashboard_ui.DashboardFrame)
    )
    label_icon.bind(
        "<Double-1>",
        lambda e: mostrar_home(container)
    )

    label_title = tk.Label(
        top_sidebar,
        text="Punihard",
        bg=COLOR_SIDEBAR,
        fg=COLOR_TEXTO,
        font=(FUENTE, 20, "bold"),
        cursor="hand2"
    )
    label_title.pack()
    label_title.bind(
        "<Button-1>",
        lambda e: mostrar_frame(container, dashboard_ui.DashboardFrame)
    )
    label_title.bind(
        "<Double-1>",
        lambda e: mostrar_home(container)
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
    label_sub.bind(
        "<Double-1>",
        lambda e: mostrar_home(container)
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
        lambda: mostrar_frame(container, articulos_ui.ArticulosFrame)
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

    crear_boton_sidebar(
        menu,
        "📊  Reportes",
        lambda: mostrar_frame(container, reportes_ui.ReportesFrame)
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

    # ==================================================
    # HEADER CONTENIDO
    # ==================================================

    header = tk.Frame(
        container,
        bg=COLOR_PANEL,
        height=80
    )

    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="📊 Panel Principal",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 22, "bold")
    ).pack(side="left", padx=30, pady=20)

    tk.Label(
        header,
        text="Sistema de gestión ferretería",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(side="right", padx=30)

    # ==================================================
    # PANTALLA INICIAL
    # ==================================================

    home = tk.Frame(
        container,
        bg=COLOR_FONDO
    )

    home.pack(fill="both", expand=True)

    tk.Label(
        home,
        text="⚡ Bienvenido al sistema",
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO,
        font=(FUENTE, 28, "bold")
    ).pack(pady=(120, 10))

    tk.Label(
        home,
        text="Seleccioná una opción del menú lateral",
        bg=COLOR_FONDO,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 13)
    ).pack()

    ventana.mainloop()


# ======================================================
# START
# ======================================================

if __name__ == "__main__":
    init_db()
    ventana_login(on_success=main_menu)