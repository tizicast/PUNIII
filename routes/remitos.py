from datetime import datetime

from sqlalchemy.orm import joinedload

from extensiones import SessionLocal
from models import Articulo, DetalleRemito, DetalleVenta, Remito, Venta


def listar_remitos():
    db = SessionLocal()
    try:
        return db.query(Remito).options(
            joinedload(Remito.venta).joinedload(Venta.cliente),
            joinedload(Remito.detalles),
        ).order_by(Remito.fecha.desc()).all()
    finally:
        db.close()


def buscar_remitos(texto):
    query = str(texto or "").strip().casefold()
    return [
        item for item in listar_remitos()
        if query in item.numero.casefold()
        or query in (item.destinatario or "").casefold()
        or query in (item.observaciones or "").casefold()
    ]


def crear_remito(numero, venta_id=None, observaciones="", destinatario="",
                 direccion_entrega="", items=None):
    numero = str(numero or "").strip()
    if not numero:
        return False, "El número de remito es obligatorio."
    db = SessionLocal()
    try:
        if db.query(Remito).filter_by(numero=numero).first():
            return False, f"El remito {numero} ya existe."
        sale = None
        if venta_id not in (None, ""):
            sale = db.query(Venta).options(
                joinedload(Venta.detalles).joinedload(DetalleVenta.articulo),
                joinedload(Venta.cliente),
            ).filter_by(id=int(venta_id), anulada=False).first()
            if not sale:
                return False, "La venta seleccionada no existe o está anulada."
            if not destinatario and sale.cliente:
                destinatario = sale.cliente.nombre_completo
            if not direccion_entrega and sale.cliente:
                direccion_entrega = sale.cliente.direccion or ""
        else:
            if not str(destinatario or "").strip():
                return False, "Indicá el destinatario del remito independiente."
            if not items:
                return False, "Agregá al menos un artículo al remito independiente."

        remito = Remito(
            numero=numero,
            venta_id=sale.id if sale else None,
            destinatario=str(destinatario or "").strip(),
            direccion_entrega=str(direccion_entrega or "").strip(),
            observaciones=str(observaciones or "").strip(),
            estado="Pendiente de entrega",
            firmado=False,
            fecha=datetime.now(),
        )
        db.add(remito)
        db.flush()
        if sale:
            for detail in sale.detalles:
                db.add(DetalleRemito(
                    remito_id=remito.id,
                    articulo_id=detail.articulo_id,
                    descripcion=detail.articulo.nombre,
                    cantidad=detail.cantidad,
                    unidad=detail.articulo.unidad,
                ))
        else:
            for item in items:
                try:
                    article_id = int(item["articulo_id"])
                    quantity = float(item["cantidad"])
                except (KeyError, TypeError, ValueError):
                    return False, "Hay un artículo con cantidad inválida."
                article = db.query(Articulo).filter_by(id=article_id, activo=True).first()
                if not article:
                    return False, "Uno de los artículos seleccionados no existe o está inactivo."
                if quantity <= 0:
                    return False, "La cantidad debe ser mayor a cero."
                db.add(DetalleRemito(
                    remito_id=remito.id,
                    articulo_id=article.id,
                    descripcion=article.nombre,
                    cantidad=quantity,
                    unidad=article.unidad,
                ))
        db.commit()
        return True, "Remito registrado como pendiente de entrega."
    except (TypeError, ValueError) as error:
        db.rollback()
        return False, f"Datos de remito inválidos: {error}"
    except Exception as error:
        db.rollback()
        return False, f"No se pudo registrar el remito: {error}"
    finally:
        db.close()


def marcar_entregado(remito_id):
    db = SessionLocal()
    try:
        remito = db.query(Remito).filter_by(id=remito_id).first()
        if not remito:
            return False, "Remito no encontrado."
        if remito.estado == "Entregado":
            return False, "El remito ya figura como entregado."
        remito.estado = "Entregado"
        remito.firmado = True
        db.commit()
        return True, "Remito marcado como entregado."
    except Exception as error:
        db.rollback()
        return False, f"No se pudo actualizar el remito: {error}"
    finally:
        db.close()


def firmar_remito(id_remito):
    return marcar_entregado(id_remito)
