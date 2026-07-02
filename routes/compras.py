from extensiones import SessionLocal
from models import Compra, Proveedor
from datetime import datetime

def get_db():
    return SessionLocal()

# ======================================================
# LISTAR COMPRAS ACTIVAS
# ======================================================
def listar_compras():
    db = get_db()
    try:
        # Filtramos solo por compras activas (baja lógica)
        return db.query(Compra).filter_by(activo=True).order_by(Compra.fecha.desc()).all()
    except Exception as e:
        print(f"Error al listar compras: {e}")
        return []
    finally:
        db.close()

# ======================================================
# CREAR COMPRA (CON VALIDACIÓN DE PROVEEDOR EXISTENTE)
# ======================================================
def crear_compra(numero, proveedor_id, total=0.0, observaciones=""):
    num_clean = str(numero).strip()
    if not num_clean:
        return False, "El número de compra es obligatorio."

    db = get_db()
    try:
        # Validar si el proveedor existe en el sistema y está activo
        prov = db.query(Proveedor).filter_by(id=proveedor_id, activo=True).first()
        if not prov:
            return False, f"El ID de proveedor {proveedor_id} no existe o está inactivo."

        # Validar si el número de compra ya está ocupado por otra transacción activa
        existente = db.query(Compra).filter_by(numero=num_clean, activo=True).first()
        if existente:
            return False, f"El número de compra '{num_clean}' ya está registrado."

        nueva_compra = Compra(
            numero=num_clean,
            proveedor_id=proveedor_id,
            total=float(total if total >= 0 else 0.0),
            observaciones=str(observaciones).strip(),
            activo=True
        )
        db.add(nueva_compra)
        db.commit()
        return True, "Compra registrada correctamente."
    except Exception as e:
        db.rollback()
        print(f"Error al crear compra: {e}")
        return False, f"Error en la base de datos: {e}"
    finally:
        db.close()

# ======================================================
# ELIMINAR COMPRA (BAJA LÓGICA / BORRADO)
# ======================================================
def eliminar_compra(id_compra):
    db = get_db()
    try:
        compra = db.query(Compra).get(id_compra)
        if not compra:
            return False, "La compra seleccionada no existe."

        # Aplicamos cambio de estado para mantener el historial intacto
        compra.activo = False
        db.commit()
        return True, "Compra eliminada del listado activo con éxito."
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar compra: {e}")
        return False, f"Error de base de datos al eliminar: {e}"
    finally:
        db.close()