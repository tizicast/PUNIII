from datetime import datetime, time

from sqlalchemy import func

from extensiones import SessionLocal
from models import Articulo, Compra, DetalleVenta, Usuario, Venta


def obtener_reporte(inicio, fin, usuario_id=None):
    inicio_dt = datetime.combine(inicio, time.min)
    fin_dt = datetime.combine(fin, time.max)
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter_by(id=usuario_id, activo=True).first()
        if not user or user.rol != "admin":
            raise PermissionError("Los reportes financieros son exclusivos del Administrador.")
        ventas = db.query(Venta).filter(
            Venta.fecha >= inicio_dt,
            Venta.fecha <= fin_dt,
            Venta.anulada.is_(False),
        )
        compras = db.query(Compra).filter(
            Compra.fecha >= inicio_dt,
            Compra.fecha <= fin_dt,
            Compra.activo.is_(True),
            Compra.anulada.is_(False),
        )
        ingresos = float(ventas.with_entities(
            func.coalesce(func.sum(Venta.total_final), 0)
        ).scalar() or 0)
        cantidad_ventas = int(ventas.count())
        egresos = float(compras.with_entities(
            func.coalesce(func.sum(Compra.total), 0)
        ).scalar() or 0)
        costo_ventas = float(db.query(
            func.coalesce(func.sum(DetalleVenta.cantidad * DetalleVenta.costo_unitario), 0)
        ).join(Venta).filter(
            Venta.fecha >= inicio_dt,
            Venta.fecha <= fin_dt,
            Venta.anulada.is_(False),
        ).scalar() or 0)

        pagos = db.query(
            Venta.metodo_pago,
            func.count(Venta.id),
            func.coalesce(func.sum(Venta.total_final), 0),
        ).filter(
            Venta.fecha >= inicio_dt,
            Venta.fecha <= fin_dt,
            Venta.anulada.is_(False),
        ).group_by(Venta.metodo_pago).order_by(Venta.metodo_pago).all()

        top = db.query(
            Articulo.nombre,
            func.sum(DetalleVenta.cantidad).label("cantidad"),
            func.sum(DetalleVenta.subtotal).label("total"),
        ).join(DetalleVenta, DetalleVenta.articulo_id == Articulo.id).join(
            Venta, Venta.id == DetalleVenta.venta_id
        ).filter(
            Venta.fecha >= inicio_dt,
            Venta.fecha <= fin_dt,
            Venta.anulada.is_(False),
        ).group_by(Articulo.id, Articulo.nombre).order_by(
            func.sum(DetalleVenta.cantidad).desc()
        ).limit(10).all()

        stock_bajo = db.query(Articulo).filter(
            Articulo.activo.is_(True),
            Articulo.stock_actual <= Articulo.stock_minimo,
        ).order_by(Articulo.stock_actual.asc(), Articulo.nombre.asc()).all()
        return {
            "inicio": inicio,
            "fin": fin,
            "ingresos": ingresos,
            "cantidad_ventas": cantidad_ventas,
            "egresos": egresos,
            "ganancia_estimada": ingresos - costo_ventas,
            "costo_ventas": costo_ventas,
            "pagos": [
                {"metodo": method, "cantidad": count, "total": float(total or 0)}
                for method, count, total in pagos
            ],
            "top_articulos": [
                {"nombre": name, "cantidad": float(quantity), "total": float(total or 0)}
                for name, quantity, total in top
            ],
            "stock_bajo": [
                {
                    "codigo": item.codigo or "",
                    "nombre": item.nombre,
                    "stock": float(item.stock_actual or 0),
                    "minimo": float(item.stock_minimo or 0),
                    "unidad": item.unidad,
                }
                for item in stock_bajo
            ],
        }
    finally:
        db.close()
