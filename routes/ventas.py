from datetime import datetime

from sqlalchemy.orm import joinedload

from extensiones import SessionLocal
from models import Articulo, Cliente, DetalleVenta, MovimientoStock, Venta


MEDIOS_PAGO = {
    "Efectivo", "Transferencia", "Tarjeta Débito", "Tarjeta Crédito",
    "Cuenta Corriente",
}


def listar_ventas(incluir_anuladas=False):
    db = SessionLocal()
    try:
        query = db.query(Venta).options(
            joinedload(Venta.cliente),
            joinedload(Venta.detalles).joinedload(DetalleVenta.articulo),
        )
        if not incluir_anuladas:
            query = query.filter(Venta.anulada.is_(False))
        return query.order_by(Venta.fecha.desc()).all()
    finally:
        db.close()


def _normalizar_items(items):
    if not items:
        raise ValueError("Agregá al menos un artículo al carrito.")
    cantidades = {}
    for item in items:
        try:
            articulo_id = int(item["articulo_id"])
            cantidad = float(item["cantidad"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("Hay un artículo con cantidad inválida.")
        if articulo_id <= 0 or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        cantidades[articulo_id] = cantidades.get(articulo_id, 0) + cantidad
    return list(cantidades.items())


def crear_venta(
    numero,
    cliente_id=None,
    total=None,
    descuento=0,
    metodo_pago="Efectivo",
    items=None,
    importe_recibido=0,
    descuento_tipo="porcentaje",
):
    numero = str(numero or "").strip()
    if not numero:
        return False, "El número de venta es obligatorio."
    try:
        descuento = float(descuento)
        recibido = float(importe_recibido or 0)
        lineas = _normalizar_items(items)
    except (ValueError, TypeError) as error:
        return False, str(error)
    if descuento < 0 or descuento_tipo not in {"porcentaje", "monto"}:
        return False, "El descuento debe ser positivo y tener un tipo válido."
    if descuento_tipo == "porcentaje" and descuento > 100:
        return False, "El descuento porcentual debe estar entre 0% y 100%."
    if recibido < 0:
        return False, "El importe recibido no puede ser negativo."
    if metodo_pago not in MEDIOS_PAGO:
        return False, "Seleccioná un método de pago válido."

    db = SessionLocal()
    try:
        if db.query(Venta).filter_by(numero=numero).first():
            return False, "El número de venta ya existe."
        cliente = None
        if cliente_id not in (None, ""):
            cliente = db.query(Cliente).filter_by(id=int(cliente_id), activo=True).first()
            if not cliente:
                return False, "El cliente seleccionado no existe o está inactivo."
        if metodo_pago == "Cuenta Corriente" and cliente is None:
            return False, "Seleccioná un cliente para cargar la venta en cuenta corriente."

        subtotal = 0.0
        articulos = {}
        lineas_con_precio = []
        for articulo_id, cantidad in lineas:
            articulo = db.query(Articulo).filter_by(id=articulo_id, activo=True).first()
            if not articulo:
                return False, f"El artículo seleccionado ({articulo_id}) no existe o está inactivo."
            articulos[articulo_id] = articulo
            precio = float(articulo.precio_venta or 0)
            costo = float(articulo.precio_compra or 0)
            lineas_con_precio.append((articulo_id, cantidad, precio, costo))
            subtotal += cantidad * precio

        if descuento_tipo == "monto" and descuento > subtotal:
            return False, "El descuento no puede superar el subtotal."
        descuento_monto = round(
            subtotal * descuento / 100 if descuento_tipo == "porcentaje" else descuento,
            2,
        )
        descuento_porcentaje = (
            round(descuento_monto / subtotal * 100, 4) if subtotal else 0
        )
        total_final = round(subtotal - descuento_monto, 2)
        if metodo_pago == "Efectivo" and recibido < total_final:
            return False, "El importe recibido no alcanza para cubrir el total."

        venta = Venta(
            numero=numero,
            cliente_id=cliente.id if cliente else None,
            total=round(subtotal, 2),
            descuento=descuento_monto,
            descuento_porcentaje=descuento_porcentaje,
            total_final=total_final,
            metodo_pago=metodo_pago,
            importe_recibido=recibido,
            fecha=datetime.now(),
        )
        db.add(venta)
        db.flush()

        for articulo_id, cantidad, precio, costo in lineas_con_precio:
            changed = db.query(Articulo).filter(
                Articulo.id == articulo_id,
                Articulo.activo.is_(True),
                Articulo.stock_actual >= cantidad,
            ).update(
                {Articulo.stock_actual: Articulo.stock_actual - cantidad},
                synchronize_session=False,
            )
            if changed != 1:
                db.rollback()
                articulo = articulos[articulo_id]
                return False, (
                    f"Stock insuficiente para {articulo.nombre}. "
                    f"Disponible: {articulo.stock_actual:g}."
                )
            db.add(DetalleVenta(
                venta_id=venta.id,
                articulo_id=articulo_id,
                cantidad=cantidad,
                precio_unitario=precio,
                costo_unitario=costo,
                subtotal=round(cantidad * precio, 2),
            ))
            db.add(MovimientoStock(
                articulo_id=articulo_id,
                venta_id=venta.id,
                tipo="venta",
                cantidad=-cantidad,
                fecha=datetime.now(),
                observaciones=f"Venta {numero}",
            ))

        if cliente and metodo_pago == "Cuenta Corriente":
            db.query(Cliente).filter_by(id=cliente.id).update(
                {
                    Cliente.saldo_cuenta_corriente:
                        Cliente.saldo_cuenta_corriente + total_final
                },
                synchronize_session=False,
            )
        db.commit()
        vuelto = round(max(recibido - total_final, 0), 2) if metodo_pago == "Efectivo" else 0
        return True, f"Venta registrada. Total: ${total_final:,.2f}. Vuelto: ${vuelto:,.2f}."
    except (TypeError, ValueError) as error:
        db.rollback()
        return False, f"Datos de venta inválidos: {error}"
    except Exception as error:
        db.rollback()
        return False, f"No se pudo registrar la venta: {error}"
    finally:
        db.close()


def anular_venta(venta_id):
    db = SessionLocal()
    try:
        venta = db.query(Venta).options(
            joinedload(Venta.detalles),
        ).filter_by(id=venta_id).first()
        if not venta:
            return False, "La venta seleccionada no existe."
        if venta.anulada:
            return False, "La venta ya está anulada."
        changed = db.query(Venta).filter(
            Venta.id == venta_id,
            Venta.anulada.is_(False),
        ).update({Venta.anulada: True}, synchronize_session=False)
        if changed != 1:
            db.rollback()
            return False, "La venta ya fue anulada por otra operación."

        for detalle in venta.detalles:
            db.query(Articulo).filter_by(id=detalle.articulo_id).update(
                {Articulo.stock_actual: Articulo.stock_actual + detalle.cantidad},
                synchronize_session=False,
            )
            db.add(MovimientoStock(
                articulo_id=detalle.articulo_id,
                venta_id=venta.id,
                tipo="anulacion_venta",
                cantidad=detalle.cantidad,
                fecha=datetime.now(),
                observaciones=f"Reversión de venta {venta.numero}",
            ))
        if venta.metodo_pago == "Cuenta Corriente" and venta.cliente_id:
            db.query(Cliente).filter_by(id=venta.cliente_id).update(
                {
                    Cliente.saldo_cuenta_corriente:
                        Cliente.saldo_cuenta_corriente - venta.total_final
                },
                synchronize_session=False,
            )
        venta.anulada = True
        db.commit()
        return True, "Venta anulada y stock restituido."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo anular la venta: {error}"
    finally:
        db.close()


def eliminar_venta(venta_id):
    return anular_venta(venta_id)
