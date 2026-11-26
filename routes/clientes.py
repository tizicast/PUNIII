from sqlalchemy import or_

from extensiones import SessionLocal
from models import Cliente


def listar_clientes():
    db = SessionLocal()
    try:
        return db.query(Cliente).filter_by(activo=True).order_by(Cliente.nombre, Cliente.apellido).all()
    finally:
        db.close()


def buscar_clientes(texto):
    db = SessionLocal()
    try:
        like = f"%{str(texto or '').strip()}%"
        return db.query(Cliente).filter(
            Cliente.activo.is_(True),
            or_(
                Cliente.nombre.ilike(like),
                Cliente.apellido.ilike(like),
                Cliente.dni_cuit.ilike(like),
                Cliente.telefono.ilike(like),
                Cliente.email.ilike(like),
            ),
        ).order_by(Cliente.nombre, Cliente.apellido).all()
    finally:
        db.close()


def crear_cliente(nombre, apellido="", telefono="", dni_cuit="", email="", direccion="",
                  condicion_iva="Consumidor Final"):
    nombre = str(nombre or "").strip()
    if not nombre:
        return False, "El nombre o razón social es obligatorio."
    db = SessionLocal()
    try:
        dni_cuit = str(dni_cuit or "").strip() or None
        if dni_cuit and db.query(Cliente).filter_by(dni_cuit=dni_cuit).first():
            return False, "Ya existe un cliente con ese DNI/CUIT."
        cliente = Cliente(
            nombre=nombre,
            apellido=str(apellido or "").strip(),
            dni_cuit=dni_cuit,
            telefono=str(telefono or "").strip(),
            email=str(email or "").strip(),
            direccion=str(direccion or "").strip(),
            condicion_iva=str(condicion_iva or "Consumidor Final").strip(),
            activo=True,
        )
        db.add(cliente)
        db.commit()
        return True, "Cliente creado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo crear el cliente: {error}"
    finally:
        db.close()


def editar_cliente(id, nombre, apellido="", telefono="", dni_cuit="", email="",
                   direccion="", condicion_iva="Consumidor Final"):
    nombre = str(nombre or "").strip()
    if not nombre:
        return False, "El nombre o razón social es obligatorio."
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter_by(id=id, activo=True).first()
        if not cliente:
            return False, "Cliente no encontrado o inactivo."
        dni_cuit = str(dni_cuit or "").strip() or None
        if dni_cuit and db.query(Cliente).filter(
            Cliente.dni_cuit == dni_cuit, Cliente.id != id
        ).first():
            return False, "Ese DNI/CUIT ya pertenece a otro cliente."
        cliente.nombre = nombre
        cliente.apellido = str(apellido or "").strip()
        cliente.dni_cuit = dni_cuit
        cliente.telefono = str(telefono or "").strip()
        cliente.email = str(email or "").strip()
        cliente.direccion = str(direccion or "").strip()
        cliente.condicion_iva = str(condicion_iva or "Consumidor Final").strip()
        db.commit()
        return True, "Cliente actualizado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo actualizar el cliente: {error}"
    finally:
        db.close()


def eliminar_cliente(id):
    db = SessionLocal()
    try:
        cliente = db.query(Cliente).filter_by(id=id, activo=True).first()
        if not cliente:
            return False, "Cliente no encontrado o inactivo."
        cliente.activo = False
        db.commit()
        return True, "Cliente desactivado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo desactivar el cliente: {error}"
    finally:
        db.close()
