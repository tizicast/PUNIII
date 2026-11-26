from sqlalchemy import or_

from extensiones import SessionLocal
from models import Proveedor


def listar_proveedores():
    db = SessionLocal()
    try:
        return db.query(Proveedor).filter_by(activo=True).order_by(Proveedor.nombre).all()
    finally:
        db.close()


def buscar_proveedores(texto):
    db = SessionLocal()
    try:
        like = f"%{str(texto or '').strip()}%"
        return db.query(Proveedor).filter(
            Proveedor.activo.is_(True),
            or_(
                Proveedor.nombre.ilike(like),
                Proveedor.contacto.ilike(like),
                Proveedor.cuit.ilike(like),
                Proveedor.telefono.ilike(like),
                Proveedor.email.ilike(like),
                Proveedor.rubro.ilike(like),
            ),
        ).order_by(Proveedor.nombre).all()
    finally:
        db.close()


def crear_proveedor(nombre, contacto="", telefono="", cuit="", email="", rubro="", direccion=""):
    nombre = str(nombre or "").strip()
    if not nombre:
        return False, "La razón social es obligatoria."
    db = SessionLocal()
    try:
        cuit = str(cuit or "").strip() or None
        if cuit and db.query(Proveedor).filter_by(cuit=cuit).first():
            return False, "Ya existe un proveedor con ese CUIT."
        db.add(Proveedor(
            nombre=nombre,
            cuit=cuit,
            contacto=str(contacto or "").strip(),
            telefono=str(telefono or "").strip(),
            email=str(email or "").strip(),
            rubro=str(rubro or "").strip(),
            direccion=str(direccion or "").strip(),
            activo=True,
        ))
        db.commit()
        return True, "Proveedor creado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo crear el proveedor: {error}"
    finally:
        db.close()


def editar_proveedor(id, nombre, contacto="", telefono="", cuit="", email="", rubro="", direccion=""):
    nombre = str(nombre or "").strip()
    if not nombre:
        return False, "La razón social es obligatoria."
    db = SessionLocal()
    try:
        provider = db.query(Proveedor).filter_by(id=id, activo=True).first()
        if not provider:
            return False, "Proveedor no encontrado o inactivo."
        cuit = str(cuit or "").strip() or None
        if cuit and db.query(Proveedor).filter(
            Proveedor.cuit == cuit, Proveedor.id != id
        ).first():
            return False, "Ese CUIT ya pertenece a otro proveedor."
        provider.nombre = nombre
        provider.cuit = cuit
        provider.contacto = str(contacto or "").strip()
        provider.telefono = str(telefono or "").strip()
        provider.email = str(email or "").strip()
        provider.rubro = str(rubro or "").strip()
        provider.direccion = str(direccion or "").strip()
        db.commit()
        return True, "Proveedor actualizado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo actualizar el proveedor: {error}"
    finally:
        db.close()


def eliminar_proveedor(id):
    db = SessionLocal()
    try:
        provider = db.query(Proveedor).filter_by(id=id, activo=True).first()
        if not provider:
            return False, "Proveedor no encontrado o inactivo."
        provider.activo = False
        db.commit()
        return True, "Proveedor desactivado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo desactivar el proveedor: {error}"
    finally:
        db.close()
