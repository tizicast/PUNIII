import tkinter as tk
from tkinter import messagebox

from extensiones import SessionLocal
from models import Usuario


# =========================
# LISTAR USUARIOS
# =========================
def listar_usuarios():
    db = SessionLocal()
    data = db.query(Usuario).all()
    db.close()
    return data


# =========================
# CREAR USUARIO
# =========================
def crear_usuario(nombre, username, email, password, rol="empleado"):

    db = SessionLocal()

    existente = db.query(Usuario).filter_by(username=username).first()

    if existente:
        db.close()
        return False, "El usuario ya existe"

    usuario = Usuario(
        nombre=nombre,
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        rol=rol,
        activo=True
    )

    db.add(usuario)
    db.commit()
    db.close()

    return True, "Usuario creado"


# =========================
# DESACTIVAR USUARIO
# =========================
def desactivar_usuario(id):

    db = SessionLocal()

    user = db.query(Usuario).get(id)

    if not user:
        db.close()
        return False, "Usuario no encontrado"

    user.activo = False
    db.commit()
    db.close()

    return True, "Usuario desactivado"


# =========================
# VENTANA USUARIOS
# =========================
def abrir_usuarios(usuario=None):

    
    if not usuario or getattr(usuario, "rol", None) != "admin":
        messagebox.showerror("Acceso denegado", "Solo el usuario admin puede acceder a Usuarios.")
        return

    ventana = tk.Tk()
    ventana.title("Usuarios")
    ventana.geometry("600x400")

    tk.Label(
        ventana,
        text="👤 Usuarios del Sistema",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    frame = tk.Frame(ventana)
    frame.pack(fill="both", expand=True)

    usuarios = listar_usuarios()

    if not usuarios:
        tk.Label(frame, text="No hay usuarios registrados").pack()
    else:
        for u in usuarios:
            estado = "Activo" if u.activo else "Inactivo"
            texto = f"{u.username} - {u.nombre} - {u.rol} - {estado}"
            tk.Label(frame, text=texto).pack(anchor="w")

    ventana.mainloop()