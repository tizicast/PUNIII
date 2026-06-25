import tkinter as tk
from tkinter import messagebox

from extensiones import SessionLocal
from models import Venta


# =========================
# LISTAR VENTAS
# =========================
def listar_ventas():
    db = SessionLocal()
    data = db.query(Venta).all()
    db.close()
    return data


# =========================
# CREAR VENTA
# =========================
def crear_venta(numero, cliente_id, total=0, descuento=0, metodo_pago="efectivo"):

    db = SessionLocal()

    existente = db.query(Venta).filter_by(numero=numero).first()
    if existente:
        db.close()
        return False, "El número de venta ya existe"

    total_final = total - (total * descuento / 100)

    venta = Venta(
        numero=numero,
        cliente_id=cliente_id,
        total=total,
        descuento=descuento,
        total_final=total_final,
        metodo_pago=metodo_pago
    )

    db.add(venta)
    db.commit()
    db.close()

    return True, "Venta creada"


# =========================
# VENTANA LISTADO
# =========================
def abrir_ventas():

    ventana = tk.Toplevel()
    ventana.title("Ventas")
    ventana.geometry("600x400")

    tk.Label(
        ventana,
        text="💰 Ventas",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    frame = tk.Frame(ventana)
    frame.pack(fill="both", expand=True)

    ventas = listar_ventas()

    if not ventas:
        tk.Label(frame, text="No hay ventas registradas").pack()
    else:
        for v in ventas:
            total_final = getattr(v, "total_final", 0)
            metodo = getattr(v, "metodo_pago", "N/A")

            texto = f"#{v.numero} - Total: {total_final} - {metodo}"
            tk.Label(frame, text=texto).pack(anchor="w")

def eliminar_venta(id):
    db = SessionLocal()
    venta = db.query(Venta).filter(Venta.id == id).first()

    if venta:
        db.delete(venta)
        db.commit()

    db.close()
# =========================
# VENTANA NUEVA VENTA
# =========================
def abrir_nueva_venta():

    ventana = tk.Toplevel()
    ventana.title("Nueva Venta")
    ventana.geometry("400x300")

    tk.Label(
        ventana,
        text="🧾 Nueva Venta",
        font=("Arial", 14, "bold")
    ).pack(pady=10)

    tk.Label(ventana, text="Número").pack()
    numero = tk.Entry(ventana)
    numero.pack()

    tk.Label(ventana, text="ID Cliente").pack()
    cliente = tk.Entry(ventana)
    cliente.pack()

    tk.Label(ventana, text="Total").pack()
    total = tk.Entry(ventana)
    total.pack()

    tk.Label(ventana, text="Descuento %").pack()
    descuento = tk.Entry(ventana)
    descuento.pack()

    def guardar():

        ok, msg = crear_venta(
            numero.get(),
            int(cliente.get() or 0),
            float(total.get() or 0),
            float(descuento.get() or 0)
        )

        messagebox.showinfo("Info", msg)

        if ok:
            ventana.destroy()

    tk.Button(
        ventana,
        text="Guardar",
        command=guardar
    ).pack(pady=10)