from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from extensiones import Base


class BaseModel:
    id = Column(Integer, primary_key=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)


class Usuario(Base, BaseModel):
    __tablename__ = "usuarios"

    nombre = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), default="vendedor", nullable=False)


class Cliente(Base, BaseModel):
    __tablename__ = "clientes"

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100))
    dni_cuit = Column(String(20), unique=True)
    telefono = Column(String(30))
    email = Column(String(120))
    direccion = Column(String(250))
    condicion_iva = Column(String(50), default="Consumidor Final", nullable=False)
    saldo_cuenta_corriente = Column(Float, default=0, nullable=False)
    ventas = relationship("Venta", back_populates="cliente")

    @property
    def nombre_completo(self):
        return " ".join(filter(None, (self.nombre, self.apellido)))


class Proveedor(Base, BaseModel):
    __tablename__ = "proveedores"

    nombre = Column(String(150), nullable=False)
    cuit = Column(String(20), unique=True)
    telefono = Column(String(30))
    email = Column(String(120))
    direccion = Column(String(200))
    contacto = Column(String(100))
    rubro = Column(String(100))
    compras = relationship("Compra", back_populates="proveedor")


class Categoria(Base, BaseModel):
    __tablename__ = "categorias"

    nombre = Column(String(100), unique=True, nullable=False)
    articulos = relationship("Articulo", back_populates="categoria")


class Articulo(Base, BaseModel):
    __tablename__ = "articulos"

    codigo = Column(String(50), unique=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    unidad = Column(String(30), default="Unidad", nullable=False)
    precio_compra = Column(Float, default=0, nullable=False)
    margen_porcentaje = Column(Float, default=0, nullable=False)
    precio_venta = Column(Float, default=0, nullable=False)
    stock_actual = Column(Float, default=0, nullable=False)
    stock_minimo = Column(Float, default=0, nullable=False)

    categoria = relationship("Categoria", back_populates="articulos")
    detalles_venta = relationship("DetalleVenta", back_populates="articulo")
    detalles_compra = relationship("DetalleCompra", back_populates="articulo")


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True)
    numero = Column(String(50), unique=True, nullable=False)
    tipo_comprobante = Column(String(30), default="Factura", nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    total = Column(Float, default=0, nullable=False)
    observaciones = Column(Text)
    activo = Column(Boolean, default=True, nullable=False)
    anulada = Column(Boolean, default=False, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    proveedor = relationship("Proveedor", back_populates="compras")
    detalles = relationship("DetalleCompra", back_populates="compra", cascade="all, delete-orphan")


class DetalleCompra(Base):
    __tablename__ = "detalle_compras"

    id = Column(Integer, primary_key=True)
    compra_id = Column(Integer, ForeignKey("compras.id"), nullable=False)
    articulo_id = Column(Integer, ForeignKey("articulos.id"), nullable=False)
    cantidad = Column(Float, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    compra = relationship("Compra", back_populates="detalles")
    articulo = relationship("Articulo", back_populates="detalles_compra")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    numero = Column(String(50), unique=True, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    total = Column(Float, default=0, nullable=False)
    descuento = Column(Float, default=0, nullable=False)
    descuento_porcentaje = Column(Float, default=0, nullable=False)
    total_final = Column(Float, default=0, nullable=False)
    metodo_pago = Column(String(50), nullable=False)
    importe_recibido = Column(Float, default=0, nullable=False)
    anulada = Column(Boolean, default=False, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    remitos = relationship("Remito", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    articulo_id = Column(Integer, ForeignKey("articulos.id"), nullable=False)
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    costo_unitario = Column(Float, default=0, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    articulo = relationship("Articulo", back_populates="detalles_venta")


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id = Column(Integer, primary_key=True)
    articulo_id = Column(Integer, ForeignKey("articulos.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"))
    compra_id = Column(Integer, ForeignKey("compras.id"))
    tipo = Column(String(30), nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    observaciones = Column(Text)

    articulo = relationship("Articulo")


class Remito(Base):
    __tablename__ = "remitos"

    id = Column(Integer, primary_key=True)
    numero = Column(String(50), unique=True, nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"))
    destinatario = Column(String(150))
    direccion_entrega = Column(String(250))
    observaciones = Column(Text)
    estado = Column(String(30), default="Pendiente de entrega", nullable=False)
    firmado = Column(Boolean, default=False, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)

    venta = relationship("Venta", back_populates="remitos")
    detalles = relationship("DetalleRemito", back_populates="remito", cascade="all, delete-orphan")


class DetalleRemito(Base):
    __tablename__ = "detalle_remitos"

    id = Column(Integer, primary_key=True)
    remito_id = Column(Integer, ForeignKey("remitos.id"), nullable=False)
    articulo_id = Column(Integer, ForeignKey("articulos.id"))
    descripcion = Column(String(200), nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String(30), default="Unidad", nullable=False)

    remito = relationship("Remito", back_populates="detalles")
    articulo = relationship("Articulo")
