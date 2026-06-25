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
def crear_usuario(nombre, username, email, password, rol="empleado"):
    """
    Crea un usuario nuevo con password hasheada.
    """

    db: Session = SessionLocal()

    existente = db.query(Usuario).filter_by(username=username).first()
    if existente:
        db.close()
        return False, "El usuario ya existe"

    nuevo = Usuario(
        nombre=nombre,
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        rol=rol,
        activo=True
    )

    db.add(nuevo)
    db.commit()
    db.close()

    return True, "Usuario creado correctamente"


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
