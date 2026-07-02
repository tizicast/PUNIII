from extensiones import SessionLocal
from models import Cliente
from sqlalchemy import or_


# ======================================================
# OBTENER SESIÓN
# ======================================================
def get_db():
    return SessionLocal()


# ======================================================
# LISTAR CLIENTES (SOLO ACTIVOS)
# ======================================================
def listar_clientes():
    db = get_db()
    try:
        # Filtramos para traer solo los que tienen activo=True
        return db.query(Cliente).filter_by(activo=True).all()
    except Exception as e:
        print(f"Error al listar clientes: {e}")
        return []
    finally:
        db.close()


# ======================================================
# BUSCAR CLIENTES (SOLO ACTIVOS)
# ======================================================
def buscar_clientes(texto):
    db = get_db()
    try:
        # Busca por coincidencia de texto, pero solo si el cliente está activo
        return db.query(Cliente).filter(
            activo=True
        ).filter(
            or_(
                Cliente.nombre.like(f"%{texto}%"),
                Cliente.apellido.like(f"%{texto}%"),
                Cliente.telefono.like(f"%{texto}%")
            )
        ).all()
    except Exception as e:
        print(f"Error al buscar clientes: {e}")
        return []
    finally:
        db.close()


# ======================================================
# CREAR CLIENTE
# ======================================================
def crear_cliente(nombre, apellido, telefono):
    # Validaciones previas básicas de datos vacíos
    if not nombre.strip() or not apellido.strip() or not telefono.strip():
        return False, "Todos los campos son obligatorios"

    db = get_db()
    try:
        # Verificar si ya existe un cliente con ese mismo teléfono
        existente = db.query(Cliente).filter_by(telefono=telefono).first()
        if existente:
            return False, "El cliente con este teléfono ya existe"

        # Crear nueva instancia
        cliente = Cliente(
            nombre=nombre.strip(),
            apellido=apellido.strip(),
            telefono=telefono.strip(),
            activo=True
        )

        db.add(cliente)
        db.commit()
        return True, "Cliente creado con éxito"
        
    except Exception as e:
        db.rollback() # Revierte los cambios si hay error en Postgres
        print(f"Error al crear cliente: {e}")
        return False, f"Error en la base de datos: {e}"
    finally:
        db.close()


# ======================================================
# EDITAR CLIENTE
# ======================================================
def editar_cliente(id, nombre, apellido, telefono):
    if not nombre.strip() or not apellido.strip() or not telefono.strip():
        return False, "Todos los campos son obligatorios"

    db = get_db()
    try:
        cliente = db.query(Cliente).get(id)

        if not cliente:
            return False, "Cliente no encontrado"

        # Actualizar datos
        cliente.nombre = nombre.strip()
        cliente.apellido = apellido.strip()
        cliente.telefono = telefono.strip()

        db.commit()
        return True, "Cliente actualizado con éxito"
        
    except Exception as e:
        db.rollback()
        print(f"Error al editar cliente: {e}")
        return False, f"Error al actualizar: {e}"
    finally:
        db.close()


# ======================================================
# ELIMINAR (BAJA LÓGICA)
# ======================================================
def eliminar_cliente(id):
    db = get_db()
    try:
        cliente = db.query(Cliente).get(id)

        if not cliente:
            return False, "Cliente no encontrado"

        # Cambiar estado a inactivo para ocultarlo en el sistema
        cliente.activo = False

        db.commit()
        return True, "Cliente eliminado con éxito"
        
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar cliente: {e}")
        return False, f"Error al eliminar: {e}"
    finally:
        db.close()