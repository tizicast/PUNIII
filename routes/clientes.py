from extensiones import SessionLocal
from models import Cliente
from sqlalchemy import or_


# =========================
# OBTENER SESIÓN
# =========================
def get_db():
    return SessionLocal()


# =========================
# LISTAR CLIENTES
# =========================
def listar_clientes():
    db = get_db()
    return db.query(Cliente).all()


# =========================
# BUSCAR CLIENTES
# =========================
def buscar_clientes(texto):
    db = get_db()
    return db.query(Cliente).filter(
        or_(
            Cliente.nombre.like(f"%{texto}%"),
            Cliente.apellido.like(f"%{texto}%"),
            Cliente.telefono.like(f"%{texto}%")
        )
    ).all()


# =========================
# CREAR CLIENTE
# =========================
def crear_cliente(nombre, apellido, telefono):

    db = get_db()

    existente = db.query(Cliente).filter_by(telefono=telefono).first()
    if existente:
        db.close()
        return False, "El cliente ya existe"

    cliente = Cliente(
        nombre=nombre,
        apellido=apellido,
        telefono=telefono,
        activo=True
    )

    db.add(cliente)
    db.commit()
    db.close()

    return True, "Cliente creado"


# =========================
# EDITAR CLIENTE
# =========================
def editar_cliente(id, nombre, apellido, telefono):

    db = get_db()
    cliente = db.query(Cliente).get(id)

    if not cliente:
        db.close()
        return False, "Cliente no encontrado"

    cliente.nombre = nombre
    cliente.apellido = apellido
    cliente.telefono = telefono

    db.commit()
    db.close()

    return True, "Cliente actualizado"


# =========================
# ELIMINAR (BAJA LÓGICA)
# =========================
def eliminar_cliente(id):

    db = get_db()
    cliente = db.query(Cliente).get(id)

    if not cliente:
        db.close()
        return False, "Cliente no encontrado"

    cliente.activo = False

    db.commit()
    db.close()

    return True, "Cliente eliminado"