from extensiones import SessionLocal
from models import Usuario
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash


# =========================
# LOGIN
# =========================
def login_usuario(username, password):
    db = SessionLocal()



    user = db.query(Usuario).filter_by(
        username=username,
        activo=True
    ).first()

    if not user:
        print("USUARIO NO ENCONTRADO")
        db.close()
        return False, "El usuario no existe"



    if not check_password_hash(user.password_hash, password):
        db.close()
        return False, "Contraseña incorrecta"

    db.close()
    return True, user

# =========================
# LOGOUT (simple estado)
# =========================
def logout_usuario():
    """
    En escritorio no hay sesión real como Flask.
    Esto se usa solo como reset lógico.
    """
    return True


# =========================
# CREAR USUARIO
# =========================
def crear_usuario(nombre, username, email, password, rol="empleado", creado_por_id=None):
    """
    Crea un usuario nuevo con password hasheada.
    """

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
        return False, "Seleccioná Administrador o Vendedor."

    db: Session = SessionLocal()
    try:
        actor = db.query(Usuario).filter_by(id=creado_por_id, activo=True).first()
        if not actor or actor.rol != "admin":
            return False, "Solo un Administrador puede crear usuarios."
        existente = db.query(Usuario).filter_by(username=username).first()
        if existente:
            return False, "El usuario ya existe."
        nuevo = Usuario(
            nombre=nombre,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            rol=rol,
            activo=True,
        )
        db.add(nuevo)
        db.commit()
        return True, "Usuario creado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo crear el usuario: {error}"
    finally:
        db.close()


# =========================
# OBTENER USUARIO
# =========================
def obtener_usuario(username):
    """
    Devuelve un usuario por username.
    """

    db: Session = SessionLocal()

    user = db.query(Usuario).filter_by(username=username).first()

    db.close()
    return user


# =========================
# DESACTIVAR USUARIO
# =========================
def desactivar_usuario(user_id):
    """
    Baja lógica de usuario.
    """

    db: Session = SessionLocal()

    user = db.query(Usuario).get(user_id)

    if not user:
        db.close()
        return False, "Usuario no encontrado"

    user.activo = False
    db.commit()
    db.close()

    return True, "Usuario desactivado"
