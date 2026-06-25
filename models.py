from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import relationship

from extensiones import Base


# ======================================================
# MIXIN BASE
# ======================================================

class BaseModel:

    id = Column(Integer, primary_key=True)

    activo = Column(
        Boolean,
        default=True
    )

    fecha_creacion = Column(
        DateTime,
        default=datetime.utcnow
    )


# ======================================================
# USUARIOS
# ======================================================

class Usuario(Base, BaseModel):

    __tablename__ = "usuarios"

    nombre = Column(
        String(100),
        nullable=False
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    email = Column(
        String(120),
        unique=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(20),
        default="empleado"
    )


# ======================================================
# CLIENTES
# ======================================================

class Cliente(Base, BaseModel):

    __tablename__ = "clientes"

    nombre = Column(
        String(100),
        nullable=False
    )

    apellido = Column(
        String(100)
    )

    dni_cuit = Column(
        String(20),
        unique=True
    )

    telefono = Column(
        String(30)
    )

    email = Column(
        String(120)
    )

    # RELACIONES
    ventas = relationship(
        "Venta",
        back_populates="cliente"
    )


# ======================================================
# PROVEEDORES
# ======================================================

class Proveedor(Base, BaseModel):

    __tablename__ = "proveedores"

    nombre = Column(
        String(150),
        nullable=False
    )

    cuit = Column(
        String(20),
        unique=True
    )

    telefono = Column(
        String(30)
    )

    email = Column(
        String(120)
    )

    direccion = Column(
        String(200)
    )

    contacto = Column(
        String(100)
    )

    # RELACIONES
    compras = relationship(
        "Compra",
        back_populates="proveedor"
    )


# ======================================================
# CATEGORIAS
# ======================================================

class Categoria(Base, BaseModel):

    __tablename__ = "categorias"

    nombre = Column(
        String(100),
        unique=True,
        nullable=False
    )

    # RELACIONES
    articulos = relationship(
        "Articulo",
        back_populates="categoria"
    )


# ======================================================
# ARTICULOS
# ======================================================

class Articulo(Base, BaseModel):

    __tablename__ = "articulos"

    codigo = Column(
        String(50),
        unique=True
    )

    nombre = Column(
        String(150),
        nullable=False
    )

    descripcion = Column(
        Text
    )

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id")
    )

    precio_compra = Column(
        Float,
        default=0
    )

    precio_venta = Column(
        Float,
        default=0
    )

    stock_actual = Column(
        Integer,
        default=0
    )

    stock_minimo = Column(
        Integer,
        default=0
    )

    # RELACIONES
    categoria = relationship(
        "Categoria",
        back_populates="articulos"
    )


# ======================================================
# COMPRAS
# ======================================================

class Compra(Base):

    __tablename__ = "compras"

    id = Column(
        Integer,
        primary_key=True
    )

    numero = Column(
        String(20),
        unique=True
    )

    proveedor_id = Column(
        Integer,
        ForeignKey("proveedores.id")
    )

    total = Column(
        Float,
        default=0
    )

    observaciones = Column(
        Text
    )

    fecha = Column(
        DateTime,
        default=datetime.utcnow
    )

    # RELACIONES
    proveedor = relationship(
        "Proveedor",
        back_populates="compras"
    )


# ======================================================
# VENTAS
# ======================================================

class Venta(Base):

    __tablename__ = "ventas"

    id = Column(
        Integer,
        primary_key=True
    )

    numero = Column(
        String(20),
        unique=True
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id")
    )

    total = Column(
        Float,
        default=0
    )

    descuento = Column(
        Float,
        default=0
    )

    total_final = Column(
        Float,
        default=0
    )

    metodo_pago = Column(
        String(50)
    )

    fecha = Column(
        DateTime,
        default=datetime.utcnow
    )

    # RELACIONES
    cliente = relationship(
        "Cliente",
        back_populates="ventas"
    )

    remitos = relationship(
        "Remito",
        back_populates="venta"
    )


# ======================================================
# REMITOS
# ======================================================

class Remito(Base):

    __tablename__ = "remitos"

    id = Column(
        Integer,
        primary_key=True
    )

    numero = Column(
        String(20),
        unique=True
    )

    venta_id = Column(
        Integer,
        ForeignKey("ventas.id")
    )

    observaciones = Column(
        Text
    )

    firmado = Column(
        Boolean,
        default=False
    )

    fecha = Column(
        DateTime,
        default=datetime.utcnow
    )

    # RELACIONES
    venta = relationship(
        "Venta",
        back_populates="remitos"
    )