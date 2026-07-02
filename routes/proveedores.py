from extensiones import SessionLocal
from models import Proveedor
from sqlalchemy import or_

def get_db():
    return SessionLocal()

# ======================================================
# LISTAR PROVEEDORES (SOLO ACTIVOS)
# ======================================================
def listar_proveedores():
    db = get_db()
    try:
        return db.query(Proveedor).filter_by(activo=True).all()
    except Exception as e:
        print(f"Error al listar proveedores: {e}")
        return []
    finally:
        db.close()

# ======================================================
# BUSCAR PROVEEDORES (CORREGIDO)
# ======================================================
def buscar_proveedores(texto):
    db = get_db()
    try:
        # CORREGIDO: Se usa filter_by o Proveedor.activo == True
        return db.query(Proveedor).filter_by(activo=True).filter(
            or_(
                Proveedor.nombre.like(f"%{texto}%"),
                Proveedor.contacto.like(f"%{texto}%"),
                Proveedor.telefono.like(f"%{texto}%")
            )
        ).all()
    except Exception as e:
        print(f"Error al buscar proveedores: {e}")
        return []
    finally:
        db.close()

# ======================================================
# CREAR PROVEEDOR
# ======================================================
def crear_proveedor(nombre, contacto, telefono):
    if not nombre.strip():
        return False, "El campo Nombre es obligatorio"

    db = get_db()
    try:
        proveedor = Proveedor(
            nombre=nombre.strip(),
            contacto=contacto.strip(),
            telefono=telefono.strip(),
            activo=True
        )
        db.add(proveedor)
        db.commit()
        return True, "Proveedor creado con éxito"
    except Exception as e:
        db.rollback()
        print(f"Error al crear proveedor: {e}")
        return False, f"Error en la base de datos: {e}"
    finally:
        db.close()

# ======================================================
# ELIMINAR PROVEEDOR (BAJA LÓGICA)
# ======================================================
def eliminar_proveedor(id):
    db = get_db()
    try:
        # SQLAlchemy get() tradicional
        proveedor = db.query(Proveedor).get(id)
        if not proveedor:
            return False, "Proveedor no encontrado"

        proveedor.activo = False
        db.commit()
        return True, "Proveedor eliminado con éxito"
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar proveedor: {e}")
        return False, f"Error al eliminar: {e}"
    finally:
        db.close()