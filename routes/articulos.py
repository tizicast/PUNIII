from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from extensiones import SessionLocal
from models import Articulo, Categoria, MovimientoStock, Usuario


def _es_admin(db, usuario_id):
    if not usuario_id:
        return False
    user = db.query(Usuario).filter_by(id=usuario_id, activo=True).first()
    return bool(user and user.rol == "admin")


def listar_articulos(texto="", categoria_id=None, bajo_stock=False):
    db = SessionLocal()
    try:
        query = db.query(Articulo).options(
            joinedload(Articulo.categoria)
        ).filter(Articulo.activo.is_(True))
        if texto.strip():
            like = f"%{texto.strip()}%"
            query = query.filter(or_(Articulo.nombre.ilike(like), Articulo.codigo.ilike(like)))
        if categoria_id:
            query = query.filter(Articulo.categoria_id == categoria_id)
        if bajo_stock:
            query = query.filter(Articulo.stock_actual <= Articulo.stock_minimo)
        return query.order_by(Articulo.nombre).all()
    finally:
        db.close()


def buscar_articulos(texto):
    return listar_articulos(texto=texto)


def listar_categorias():
    db = SessionLocal()
    try:
        return db.query(Categoria).filter(Categoria.activo.is_(True)).order_by(Categoria.nombre).all()
    finally:
        db.close()


def crear_articulo(codigo, nombre, descripcion, categoria_id,
                   precio_compra, precio_venta, stock_actual, stock_minimo,
                   unidad="Unidad", margen_porcentaje=0, usuario_id=None):
    codigo = str(codigo or "").strip() or None
    nombre = str(nombre or "").strip()
    unidad = str(unidad or "").strip()
    try:
        costo = float(precio_compra)
        precio = float(precio_venta)
        stock = float(stock_actual)
        minimo = float(stock_minimo)
        margen = float(margen_porcentaje)
        categoria_id = int(categoria_id) if categoria_id else None
    except (TypeError, ValueError):
        return False, "Revisá categoría, precios y cantidades."
    if not nombre or not unidad:
        return False, "El nombre y la unidad de medida son obligatorios."
    if min(costo, precio, stock, minimo, margen) < 0:
        return False, "Los precios, el margen y el stock no pueden ser negativos."
    if categoria_id is not None and categoria_id <= 0:
        return False, "Seleccioná una categoría válida."

    db = SessionLocal()
    try:
        if not _es_admin(db, usuario_id) and (costo != 0 or margen != 0):
            return False, "Solo un Administrador puede ingresar costos o márgenes."
        if codigo and db.query(Articulo).filter_by(codigo=codigo).first():
            return False, "El código/SKU ya existe."
        if categoria_id and not db.query(Categoria).filter_by(id=categoria_id, activo=True).first():
            return False, "La categoría seleccionada no existe o está inactiva."
        if precio == 0 and costo and margen:
            precio = round(costo * (1 + margen / 100), 2)
        article = Articulo(
            codigo=codigo,
            nombre=nombre,
            descripcion=str(descripcion or "").strip(),
            categoria_id=categoria_id,
            unidad=unidad,
            precio_compra=costo,
            margen_porcentaje=margen,
            precio_venta=precio,
            stock_actual=stock,
            stock_minimo=minimo,
            activo=True,
        )
        db.add(article)
        db.flush()
        if stock:
            db.add(MovimientoStock(
                articulo_id=article.id,
                tipo="stock_inicial",
                cantidad=stock,
                fecha=datetime.now(),
                observaciones="Stock inicial",
            ))
        db.commit()
        return True, "Artículo creado correctamente."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo crear el artículo: {error}"
    finally:
        db.close()


def editar_articulo(id, nombre, descripcion, categoria_id, precio_compra,
                    precio_venta, stock_minimo, codigo=None, unidad="Unidad",
                    margen_porcentaje=0, usuario_id=None):
    try:
        costo = float(precio_compra)
        precio = float(precio_venta)
        minimo = float(stock_minimo)
        margen = float(margen_porcentaje)
        categoria_id = int(categoria_id) if categoria_id else None
    except (TypeError, ValueError):
        return False, "Revisá categoría, precios y stock mínimo."
    nombre = str(nombre or "").strip()
    codigo = str(codigo or "").strip() or None
    unidad = str(unidad or "").strip()
    if not nombre or not unidad:
        return False, "El nombre y la unidad de medida son obligatorios."
    if min(costo, precio, minimo, margen) < 0:
        return False, "Los precios, el margen y el stock mínimo no pueden ser negativos."

    db = SessionLocal()
    try:
        article = db.query(Articulo).filter_by(id=id, activo=True).first()
        if not article:
            return False, "El artículo no existe o está inactivo."
        admin = _es_admin(db, usuario_id)
        if not admin and (
            costo != article.precio_compra
            or margen != article.margen_porcentaje
        ):
            return False, "Solo un Administrador puede modificar costos o márgenes."
        if codigo and db.query(Articulo).filter(
            Articulo.codigo == codigo, Articulo.id != id
        ).first():
            return False, "El código/SKU ya está asignado a otro artículo."
        if categoria_id and not db.query(Categoria).filter_by(id=categoria_id, activo=True).first():
            return False, "La categoría seleccionada no existe o está inactiva."
        article.codigo = codigo
        article.nombre = nombre
        article.descripcion = str(descripcion or "").strip()
        article.categoria_id = categoria_id
        article.unidad = unidad
        if admin:
            article.precio_compra = costo
            article.margen_porcentaje = margen
        article.precio_venta = precio
        article.stock_minimo = minimo
        db.commit()
        return True, "Artículo actualizado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo actualizar el artículo: {error}"
    finally:
        db.close()


def eliminar_articulo(id):
    db = SessionLocal()
    try:
        article = db.query(Articulo).filter_by(id=id, activo=True).first()
        if not article:
            return False, "El artículo no existe o ya está inactivo."
        article.activo = False
        db.commit()
        return True, "Artículo desactivado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo desactivar el artículo: {error}"
    finally:
        db.close()
