from extensiones import engine

try:
    with engine.connect() as conn:
        print("Conexión exitosa a PostgreSQL")
except Exception as e:
    print("Error:", e)