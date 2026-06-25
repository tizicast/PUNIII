from extensiones import SessionLocal, engine  # ← Sumamos 'engine' aquí
from models import Base, Usuario, Categoria  # ← Sumamos 'Base' aquí
from werkzeug.security import generate_password_hash


def seed_initial_data():
    # 🚀 CREAR TABLAS EN POSTGRESQL AUTOMÁTICAMENTE SI NO EXISTEN
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 🔥 LIMPIAR TABLAS
        db.query(Usuario).delete()
        db.query(Categoria).delete()

        # =========================
        # USUARIOS
        # =========================
        print("Insertando usuarios de prueba...")
        admin = Usuario(
            nombre='Administrador',
            username='admin',
            email='admin@ferreteria.com',
            password_hash=generate_password_hash('admin123'),
            rol='admin',
            activo=True
        )

        empleado = Usuario(
            nombre='Empleado',
            username='empleado',
            email='empleado@ferreteria.com',
            password_hash=generate_password_hash('emp123'),
            rol='empleado',
            activo=True
        )

        db.add_all([admin, empleado])

        # =========================
        # CATEGORIAS
        # =========================
        print("Insertando categorías de prueba...")
        categorias = [
            Categoria(nombre='Herramientas', activo=True),
            Categoria(nombre='Electricidad', activo=True),
            Categoria(nombre='Plomería', activo=True)
        ]

        db.add_all(categorias)

        db.commit()
        print("¡Base de datos sembrada con éxito!")

    except Exception as e:
        db.rollback()
        print("Error en seed:", e)

    finally:
        db.close()

# Esto asegura que si corres 'python seed.py' desde la terminal, la función se ejecute sola
if __name__ == "__main__":
    seed_initial_data()