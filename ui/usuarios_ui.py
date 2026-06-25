import tkinter as tk
from tkinter import messagebox, ttk

from routes.usuarios import (
    listar_usuarios,
    crear_usuario,
    desactivar_usuario
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
# FRAME USUARIOS
# ======================================================

class UsuariosFrame(tk.Frame):

    def __init__(self, parent, usuario=None):

        # ==================================================
        # VALIDACION ADMIN
        # ==================================================

        if not usuario or getattr(usuario, "rol", None) != "admin":

            tk.Frame.__init__(self, parent, bg=COLOR_FONDO)

            messagebox.showerror(
                "Acceso denegado",
                "Solo el usuario admin puede acceder a Usuarios."
            )

            return

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
            text="👤 Usuarios del Sistema",
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
            text="📋 Usuarios registrados",
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
            width=360,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )

        panel_form.pack(side="right", fill="y")
        panel_form.pack_propagate(False)

        tk.Label(
            panel_form,
            text="➕ Nuevo usuario",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # ==================================================
        # NOMBRE
        # ==================================================

        tk.Label(
            panel_form,
            text="Nombre",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_nombre = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_nombre.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # USERNAME
        # ==================================================

        tk.Label(
            panel_form,
            text="Username",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_username = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_username.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # EMAIL
        # ==================================================

        tk.Label(
            panel_form,
            text="Email",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_email = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_email.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # PASSWORD
        # ==================================================

        tk.Label(
            panel_form,
            text="Contraseña",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_password = tk.Entry(
            panel_form,
            show="*",
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_password.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # ROL
        # ==================================================

        tk.Label(
            panel_form,
            text="Rol",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        style = ttk.Style()

        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=COLOR_INPUT,
            background=COLOR_INPUT,
            foreground="white",
            borderwidth=0,
            arrowsize=15
        )

        self.combo_rol = ttk.Combobox(
            panel_form,
            values=["admin", "empleado"],
            state="readonly",
            font=(FUENTE, 10)
        )

        self.combo_rol.set("empleado")

        self.combo_rol.pack(
            fill="x",
            padx=20,
            pady=(8, 30),
            ipady=6
        )

        # ==================================================
        # BOTON CREAR
        # ==================================================

        btn_crear = tk.Button(
            panel_form,
            text="➕ Crear usuario",
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
        # CARGAR USUARIOS
        # ==================================================

        self.refrescar()

    # ======================================================
    # REFRESCAR
    # ======================================================

    def refrescar(self):

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        usuarios = listar_usuarios()

        if not usuarios:

            tk.Label(
                self.frame_lista,
                text="No hay usuarios registrados",
                bg=COLOR_PANEL,
                fg=COLOR_SECUNDARIO,
                font=(FUENTE, 11)
            ).pack(pady=20)

            return

        # ==================================================
        # LISTADO
        # ==================================================

        for u in usuarios:

            estado = "🟢 Activo" if getattr(u, "activo", True) else "🔴 Inactivo"

            info = (
                f"👤 {u.username}   |   "
                f"{u.nombre}   |   "
                f"{u.rol.upper()}   |   "
                f"{estado}"
            )

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

            btn_delete = tk.Button(
                fila,
                text="Desactivar",
                command=lambda uid=u.id: self.desactivar(uid),
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
    # CREAR
    # ======================================================

    def guardar(self):

        ok, msg = crear_usuario(
            self.entry_nombre.get(),
            self.entry_username.get(),
            self.entry_email.get(),
            self.entry_password.get(),
            self.combo_rol.get() or "empleado"
        )

        messagebox.showinfo(
            "Información",
            msg
        )

        if ok:

            self.entry_nombre.delete(0, "end")
            self.entry_username.delete(0, "end")
            self.entry_email.delete(0, "end")
            self.entry_password.delete(0, "end")

            self.combo_rol.set("empleado")

            self.refrescar()

    # ======================================================
    # DESACTIVAR
    # ======================================================

    def desactivar(self, id):

        ok, msg = desactivar_usuario(id)

        messagebox.showinfo(
            "Información",
            msg
        )

        if ok:
            self.refrescar()