from datetime import datetime

from sqlalchemy.orm import joinedload

from extensiones import SessionLocal
from models import Articulo, Compra, DetalleCompra, MovimientoStock, Proveedor


def listar_compras(incluir_anuladas=False):
    db = SessionLocal()
    try:
        query = db.query(Compra).options(
            joinedload(Compra.proveedor),
            joinedload(Compra.detalles).joinedload(DetalleCompra.articulo),
        ).filter(Compra.activo.is_(True))
        if not incluir_anuladas:
            query = query.filter(Compra.anulada.is_(False))
        return query.order_by(Compra.fecha.desc()).all()
    finally:
        db.close()


def _normalizar_items(items):
    if not items:
        raise ValueError("Agregá al menos un artículo a la compra.")
    lineas = []
    for item in items:
        try:
            articulo_id = int(item["articulo_id"])
            cantidad = float(item["cantidad"])
            costo = float(item["costo_unitario"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Hay un artículo con cantidad o costo inválido.")
        if articulo_id <= 0 or cantidad <= 0 or costo < 0:
            raise ValueError("La cantidad debe ser mayor a cero y el costo no puede ser negativo.")
        lineas.append((articulo_id, cantidad, costo))
    return lineas


def crear_compra(numero, proveedor_id, total=None, observaciones="", items=None,
                 tipo_comprobante="Factura", fecha=None):
    numero = str(numero or "").strip()
    tipo_comprobante = str(tipo_comprobante or "").strip()
    if not numero or not tipo_comprobante:
        return False, "El número y tipo de comprobante son obligatorios."
    try:
        lineas = _normalizar_items(items)
    except ValueError as error:
        return False, str(error)

    db = SessionLocal()
    try:
        proveedor = db.query(Proveedor).filter_by(id=int(proveedor_id), activo=True).first()
        if not proveedor:
            return False, "El proveedor seleccionado no existe o está inactivo."
        if db.query(Compra).filter_by(numero=numero).first():
            return False, f"El comprobante '{numero}' ya está registrado."

        articulos = {}
        total_calculado = 0.0
        for articulo_id, cantidad, costo in lineas:
            articulo = db.query(Articulo).filter_by(id=articulo_id, activo=True).first()
            if not articulo:
                return False, f"El artículo seleccionado ({articulo_id}) no existe o está inactivo."
            articulos[articulo_id] = articulo
            total_calculado += cantidad * costo

        compra = Compra(
            numero=numero,
            tipo_comprobante=tipo_comprobante,
            proveedor_id=proveedor.id,
            total=round(total_calculado, 2),
            observaciones=str(observaciones or "").strip(),
            fecha=fecha or datetime.now(),
        )
        db.add(compra)
        db.flush()

        for articulo_id, cantidad, costo in lineas:
            articulo = articulos[articulo_id]
            updates = {
                Articulo.stock_actual: Articulo.stock_actual + cantidad,
                Articulo.precio_compra: costo,
            }
            if articulo.margen_porcentaje > 0:
                updates[Articulo.precio_venta] = round(
                    costo * (1 + articulo.margen_porcentaje / 100), 2
                )
            db.query(Articulo).filter_by(id=articulo_id, activo=True).update(
                updates, synchronize_session=False
            )
            db.add(DetalleCompra(
                compra_id=compra.id,
                articulo_id=articulo_id,
                cantidad=cantidad,
                costo_unitario=costo,
                subtotal=round(cantidad * costo, 2),
            ))
            db.add(MovimientoStock(
                articulo_id=articulo_id,
                compra_id=compra.id,
                tipo="compra",
                cantidad=cantidad,
                fecha=datetime.now(),
                observaciones=f"{tipo_comprobante} {numero}",
            ))
        db.commit()
        return True, f"Compra registrada por ${total_calculado:,.2f}; stock y costos actualizados."
    except (TypeError, ValueError) as error:
        db.rollback()
        return False, f"Datos de compra inválidos: {error}"
    except Exception as error:
        db.rollback()
        return False, f"No se pudo registrar la compra: {error}"
    finally:
        db.close()


def anular_compra(compra_id):
    db = SessionLocal()
    try:
        compra = db.query(Compra).options(
            joinedload(Compra.detalles),
        ).filter_by(id=compra_id).first()
        if not compra or not compra.activo:
            return False, "La compra seleccionada no existe."
        if compra.anulada:
            return False, "La compra ya está anulada."
        changed = db.query(Compra).filter(
            Compra.id == compra_id,
            Compra.anulada.is_(False),
            Compra.activo.is_(True),
        ).update({Compra.anulada: True}, synchronize_session=False)
        if changed != 1:
            db.rollback()
            return False, "La compra ya fue anulada por otra operación."

        for detalle in compra.detalles:
            changed = db.query(Articulo).filter(
                Articulo.id == detalle.articulo_id,
                Articulo.stock_actual >= detalle.cantidad,
            ).update(
                {Articulo.stock_actual: Articulo.stock_actual - detalle.cantidad},
                synchronize_session=False,
            )
            if changed != 1:
                db.rollback()
                articulo = db.query(Articulo).filter_by(id=detalle.articulo_id).first()
                nombre = articulo.nombre if articulo else str(detalle.articulo_id)
                return False, (
                    f"No se puede anular: el stock disponible de {nombre} es menor "
                    "que la cantidad ingresada en esta compra."
                )
            db.add(MovimientoStock(
                articulo_id=detalle.articulo_id,
                compra_id=compra.id,
                tipo="anulacion_compra",
                cantidad=-detalle.cantidad,
                fecha=datetime.now(),
                observaciones=f"Reversión de compra {compra.numero}",
            ))
        compra.anulada = True
        db.commit()
        return True, "Compra anulada y stock revertido."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo anular la compra: {error}"
    finally:
        db.close()


def eliminar_compra(id_compra):
    return anular_compra(id_compra)
