from extensiones import engine

try:
    with engine.connect() as conn:
        print("Conexión exitosa a SQLite")
except Exception as e:
    print("Error:", e)