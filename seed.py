from extensiones import SessionLocal, migrate_schema
from models import Usuario, Categoria
from werkzeug.security import generate_password_hash


def seed_initial_data():
    print("Verificando esquema de la base de datos...")
    migrate_schema()

    db = SessionLocal()

    try:
        if not db.query(Usuario).filter_by(username="admin").first():
            db.add(Usuario(
                nombre="Administrador",
                username="admin",
                email="admin@ferreteria.com",
                password_hash=generate_password_hash("admin123"),
                rol="admin",
                activo=True,
            ))
        if not db.query(Usuario).filter_by(username="empleado").first():
            db.add(Usuario(
                nombre="Vendedor",
                username="empleado",
                email="vendedor@ferreteria.com",
                password_hash=generate_password_hash("emp123"),
                rol="vendedor",
                activo=True,
            ))

        categorias = (
            "Tornillería", "Herramientas", "Electricidad", "Plomería",
            "Pinturería", "Construcción", "Jardín", "Otros",
        )
        for nombre in categorias:
            if not db.query(Categoria).filter_by(nombre=nombre).first():
                db.add(Categoria(nombre=nombre, activo=True))
        db.query(Usuario).filter_by(rol="empleado").update(
            {Usuario.rol: "vendedor"}, synchronize_session=False
        )

        db.commit()
        print("Datos iniciales verificados.")

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"No se pudieron preparar los datos iniciales: {e}") from e

    finally:
        db.close()

# Esto asegura que si corres 'python seed.py' desde la terminal, la función se ejecute sola
if __name__ == "__main__":
    seed_initial_data()