from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'ferreteria.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def migrate_schema():
    """Create missing tables and additive columns without replacing existing data."""
    from models import Base as ModelBase

    ModelBase.metadata.create_all(bind=engine)
    additions = {
        "articulos": {
            "unidad": "VARCHAR(30) NOT NULL DEFAULT 'Unidad'",
            "margen_porcentaje": "FLOAT NOT NULL DEFAULT 0",
        },
        "clientes": {
            "direccion": "VARCHAR(250)",
            "condicion_iva": "VARCHAR(50) NOT NULL DEFAULT 'Consumidor Final'",
            "saldo_cuenta_corriente": "FLOAT NOT NULL DEFAULT 0",
        },
        "proveedores": {"rubro": "VARCHAR(100)"},
        "compras": {
            "tipo_comprobante": "VARCHAR(30) NOT NULL DEFAULT 'Factura'",
            "activo": "BOOLEAN NOT NULL DEFAULT 1",
            "anulada": "BOOLEAN NOT NULL DEFAULT 0",
        },
        "ventas": {
            "descuento_porcentaje": "FLOAT NOT NULL DEFAULT 0",
            "importe_recibido": "FLOAT NOT NULL DEFAULT 0",
            "anulada": "BOOLEAN NOT NULL DEFAULT 0",
        },
        "remitos": {
            "destinatario": "VARCHAR(150)",
            "direccion_entrega": "VARCHAR(250)",
            "estado": "VARCHAR(30) NOT NULL DEFAULT 'Pendiente de entrega'",
        },
        "detalle_ventas": {"costo_unitario": "FLOAT NOT NULL DEFAULT 0"},
    }

    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, columns in additions.items():
            if not inspector.has_table(table_name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, definition in columns.items():
                if column_name not in existing:
                    connection.execute(text(
                        f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {definition}'
                    ))


def get_db():
    return SessionLocal()