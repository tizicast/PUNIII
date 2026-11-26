import tkinter as tk
from tkinter import messagebox
from werkzeug.security import generate_password_hash

from extensiones import SessionLocal
from models import Usuario


# =========================
# LISTAR USUARIOS
# =========================
def _es_admin(db, usuario_id):
    if not usuario_id:
        return False
    actor = db.query(Usuario).filter_by(id=usuario_id, activo=True).first()
    return bool(actor and actor.rol == "admin")


def listar_usuarios(usuario_id=None):
    db = SessionLocal()
    try:
        if not _es_admin(db, usuario_id):
            raise PermissionError("Solo un Administrador puede consultar usuarios.")
        return db.query(Usuario).order_by(Usuario.nombre).all()
    finally:
        db.close()


# =========================
# CREAR USUARIO
# =========================
def crear_usuario(nombre, username, email, password, rol="vendedor", creado_por_id=None):
    nombre = str(nombre or "").strip()
    username = str(username or "").strip()
    email = str(email or "").strip() or None
    password = str(password or "")
    rol = str(rol or "").strip().lower()
    if rol == "empleado":
        rol = "vendedor"
    if not nombre or not username or not password:
        return False, "Nombre, usuario y contraseña son obligatorios."
    if rol not in {"admin", "vendedor"}:
        return False, "El rol debe ser Administrador o Vendedor."
    db = SessionLocal()
    try:
        if not _es_admin(db, creado_por_id):
            return False, "Solo un Administrador puede crear usuarios."
        existente = db.query(Usuario).filter_by(username=username).first()
        if existente:
            return False, "El usuario ya existe."
        usuario = Usuario(
            nombre=nombre,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            rol=rol,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        return True, "Usuario creado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo crear el usuario: {error}"
    finally:
        db.close()


# =========================
# DESACTIVAR USUARIO
# =========================
def desactivar_usuario(id, desactivado_por_id=None):
    db = SessionLocal()
    try:
        if not _es_admin(db, desactivado_por_id):
            return False, "Solo un Administrador puede desactivar usuarios."
        user = db.query(Usuario).filter_by(id=id, activo=True).first()
        if not user:
            return False, "Usuario no encontrado o ya inactivo."
        if user.id == desactivado_por_id:
            return False, "No podés desactivar tu propio usuario."
        if user.rol == "admin" and db.query(Usuario).filter_by(
            rol="admin", activo=True
        ).count() <= 1:
            return False, "No se puede desactivar al único administrador activo."
        user.activo = False
        db.commit()
        return True, "Usuario desactivado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo desactivar el usuario: {error}"
    finally:
        db.close()


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

    usuarios = listar_usuarios(usuario.id)

    if not usuarios:
        tk.Label(frame, text="No hay usuarios registrados").pack()
    else:
        for u in usuarios:
            estado = "Activo" if u.activo else "Inactivo"
            texto = f"{u.username} - {u.nombre} - {u.rol} - {estado}"
            tk.Label(frame, text=texto).pack(anchor="w")

    ventana.mainloop()