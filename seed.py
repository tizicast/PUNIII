from extensiones import SessionLocal
from models import Usuario, Categoria
from werkzeug.security import generate_password_hash


def seed_initial_data():
    db = SessionLocal()

    try:
        # 🔥 LIMPIAR TABLAS
        db.query(Usuario).delete()
        db.query(Categoria).delete()

        # =========================
        # USUARIOS
        # =========================
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
        categorias = [
            Categoria(nombre='Herramientas', activo=True),
            Categoria(nombre='Electricidad', activo=True),
            Categoria(nombre='Plomería', activo=True)
        ]

        db.add_all(categorias)

        db.commit()

    except Exception as e:
        db.rollback()
        print("Error en seed:", e)

    finally:
        db.close()