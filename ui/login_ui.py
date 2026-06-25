import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from routes.auth import login_usuario


# ======================================================
# COLORES - DARK ORANGE UI
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_INPUT = "#262626"
COLOR_BORDE = "#2f2f2f"

FUENTE = "Segoe UI"


# ======================================================
# HOVER BOTON
# ======================================================

def hover_boton(btn):

    btn.bind(
        "<Enter>",
        lambda e: btn.config(bg=COLOR_NARANJA_HOVER)
    )

    btn.bind(
        "<Leave>",
        lambda e: btn.config(bg=COLOR_NARANJA)
    )


# ======================================================
# LOGIN
# ======================================================

def ventana_login(on_success):

    # ==================================================
    # VENTANA
    # ==================================================

    win = tk.Tk()

    win.title("Punihard - Login")
    win.state("zoomed")
    win.configure(bg=COLOR_FONDO)

    win.resizable(False, False)



    # ==================================================
    # PANEL IZQUIERDO
    # ==================================================

    left = tk.Frame(
        win,
        bg=COLOR_PANEL,
        width=450
    )

    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    # ==================================================
    # LOGO
    # ==================================================

    try:

        imagen_logo = Image.open("punihard.png")
        imagen_logo = imagen_logo.resize((140, 140))

        logo = ImageTk.PhotoImage(imagen_logo)

        label_logo = tk.Label(
            left,
            image=logo,
            bg=COLOR_PANEL
        )

        label_logo.image = logo
        label_logo.pack(pady=(80, 20))

    except:

        tk.Label(
            left,
            text="⚡",
            bg=COLOR_PANEL,
            fg=COLOR_NARANJA,
            font=(FUENTE, 70)
        ).pack(pady=(80, 20))

    # ==================================================
    # TITULOS
    # ==================================================

    tk.Label(
        left,
        text="Punihard",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 28, "bold")
    ).pack()

    tk.Label(
        left,
        text="Sistema de Gestión",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 13)
    ).pack(pady=(5, 0))

    tk.Label(
        left,
        text="© 2026 Punihard - Todos los derechos reservados",
        bg=COLOR_PANEL,
        fg=COLOR_NARANJA,
        font=(FUENTE, 11, "bold")
    ).pack(pady=(20, 0))

    # ==================================================
    # PANEL DERECHO
    # ==================================================

    right = tk.Frame(
        win,
        bg=COLOR_FONDO
    )

    right.pack(side="right", fill="both", expand=True)

    # ==================================================
    # LOGIN BOX
    # ==================================================

    login_box = tk.Frame(
        right,
        bg=COLOR_PANEL,
        width=420,
        height=420,
        highlightbackground=COLOR_BORDE,
        highlightthickness=1
    )

    login_box.place(relx=0.5, rely=0.5, anchor="center")
    login_box.pack_propagate(False)

    # ==================================================
    # TITULO LOGIN
    # ==================================================

    tk.Label(
        login_box,
        text="Iniciar Sesión",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 24, "bold")
    ).pack(pady=(40, 10))

    tk.Label(
        login_box,
        text="Ingresá tus credenciales",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 11)
    ).pack(pady=(0, 30))

    # ==================================================
    # USER
    # ==================================================

    tk.Label(
        login_box,
        text="Usuario",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=45)

    entry_user = tk.Entry(
        login_box,
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        font=(FUENTE, 12),
        width=28
    )

    entry_user.pack(ipady=10, pady=(8, 20))

    # ==================================================
    # PASSWORD
    # ==================================================

    tk.Label(
        login_box,
        text="Contraseña",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 11)
    ).pack(anchor="w", padx=45)

    entry_pass = tk.Entry(
        login_box,
        show="*",
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        font=(FUENTE, 12),
        width=28
    )

    entry_pass.pack(ipady=10, pady=(8, 30))

    # ==================================================
    # VALIDAR LOGIN
    # ==================================================

    def validar():

        ok, result = login_usuario(
            entry_user.get(),
            entry_pass.get()
        )

        if ok:

            win.destroy()
            on_success(result)

        else:

            messagebox.showerror(
                "Error",
                result
            )

    # ==================================================
    # BOTON LOGIN
    # ==================================================

    btn_login = tk.Button(
        login_box,
        text="Ingresar",
        command=validar,
        bg=COLOR_NARANJA,
        fg="white",
        activebackground=COLOR_NARANJA_HOVER,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        font=(FUENTE, 12, "bold"),
        padx=30,
        pady=12
    )

    btn_login.pack()

    hover_boton(btn_login)

    # ==================================================
    # FOOTER
    # ==================================================

    tk.Label(
        login_box,
        text="© Punihard System",
        bg=COLOR_PANEL,
        fg=COLOR_SECUNDARIO,
        font=(FUENTE, 9)
    ).pack(side="bottom", pady=20)

    # ==================================================
    # ENTER = LOGIN
    # ==================================================

    win.bind(
        "<Return>",
        lambda e: validar()
    )

    win.mainloop()