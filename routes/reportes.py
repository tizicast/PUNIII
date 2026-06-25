import tkinter as tk
from tkinter import messagebox

from extensiones import SessionLocal
from models import Venta, Compra, Cliente, Articulo


# =========================
# DATOS PARA DASHBOARD
# =========================
def listar_reportes():

    db = SessionLocal()

    data = {
        "ventas": db.query(Venta).count(),
        "compras": db.query(Compra).count(),
        "clientes": db.query(Cliente).count(),
        "articulos": db.query(Articulo).count(),
    }

    db.close()
    return data


# =========================
# VENTANA REPORTES
# =========================
def abrir_reportes():

    ventana = tk.Toplevel()
    ventana.title("Reportes")
    ventana.geometry("500x400")

    tk.Label(
        ventana,
        text="📊 Reportes del Sistema",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    data = listar_reportes()

    frame = tk.Frame(ventana)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text=f"Ventas: {data['ventas']}").pack(anchor="w")
    tk.Label(frame, text=f"Compras: {data['compras']}").pack(anchor="w")
    tk.Label(frame, text=f"Clientes: {data['clientes']}").pack(anchor="w")
    tk.Label(frame, text=f"Artículos: {data['articulos']}").pack(anchor="w")

    def ventas_report():
        messagebox.showinfo("Ventas", f"Total ventas: {data['ventas']}")

    tk.Button(frame, text="📈 Reporte Ventas", command=ventas_report).pack(pady=10)