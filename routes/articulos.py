from extensiones import SessionLocal
from models import Articulo, Categoria


# =========================
# CONSULTAS BASE
# =========================
def listar_articulos():
    db = SessionLocal()
    data = db.query(Articulo).filter_by(activo=True).all()
    db.close()
    return data


def buscar_articulos(texto):
    db = SessionLocal()
    data = db.query(Articulo).filter(
        (Articulo.nombre.like(f"%{texto}%")) |
        (Articulo.codigo.like(f"%{texto}%"))
    ).all()
    db.close()
    return data


def listar_categorias():
    db = SessionLocal()
    data = db.query(Categoria).all()
    db.close()
    return data


# =========================
# CRUD
# =========================
def crear_articulo(codigo, nombre, descripcion, categoria_id,
                   precio_compra, precio_venta,
                   stock_actual, stock_minimo):

    db = SessionLocal()

    existe = db.query(Articulo).filter_by(codigo=codigo).first()
    if existe:
        db.close()
        return False, "El código ya existe"

    art = Articulo(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        categoria_id=categoria_id,
        precio_compra=precio_compra,
        precio_venta=precio_venta,
        stock_actual=stock_actual,
        stock_minimo=stock_minimo,
        activo=True
    )

    db.add(art)
    db.commit()
    db.close()

    return True, "Artículo creado"


def editar_articulo(id, nombre, descripcion,
                    categoria_id, precio_compra,
                    precio_venta, stock_minimo):

    db = SessionLocal()

    art = db.query(Articulo).get(id)

    if not art:
        db.close()
        return False, "No existe"

    art.nombre = nombre
    art.descripcion = descripcion
    art.categoria_id = categoria_id
    art.precio_compra = precio_compra
    art.precio_venta = precio_venta
    art.stock_minimo = stock_minimo

    db.commit()
    db.close()

    return True, "Actualizado"


def eliminar_articulo(id):

    db = SessionLocal()

    art = db.query(Articulo).get(id)

    if not art:
        db.close()
        return False, "No existe"

    art.activo = False
    db.commit()
    db.close()

    return True, "Eliminado"