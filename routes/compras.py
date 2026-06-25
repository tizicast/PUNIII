import tkinter as tk
from tkinter import messagebox, ttk
from extensiones import SessionLocal
from models import Compra


def hover_boton(boton, color_normal, color_hover):
    boton.bind("<Enter>", lambda e: boton.config(bg=color_hover))
    boton.bind("<Leave>", lambda e: boton.config(bg=color_normal))

# ─────────────────────────────────────────
#  COLORES Y ESTILO GLOBAL
# ─────────────────────────────────────────
COLOR_FONDO     = "#f0f4f8"
COLOR_ENCABEZADO = "#2c3e50"
COLOR_BTN_VERDE  = "#27ae60"
COLOR_BTN_ROJO   = "#e74c3c"
COLOR_BTN_TEXT   = "white"
FUENTE_TITULO    = ("Segoe UI", 16, "bold")
FUENTE_LABEL     = ("Segoe UI", 10)
FUENTE_BTN       = ("Segoe UI", 10, "bold")


# ─────────────────────────────────────────
#  BASE DE DATOS
# ─────────────────────────────────────────
def listar_compras():
    db = SessionLocal()
    data = db.query(Compra).all()
    db.close()
    return data


def crear_compra(numero, proveedor_id, total=0, observaciones=""):
    db = SessionLocal()
    existente = db.query(Compra).filter_by(numero=numero).first()
    if existente:
        db.close()
        return False, "⚠️ Ese número de compra ya existe."

    compra = Compra(
        numero=numero,
        proveedor_id=proveedor_id,
        total=total,
        observaciones=observaciones
    )
    db.add(compra)
    db.commit()
    db.close()
    return True, "✅ Compra registrada correctamente."

def borrar_compra(numero, proveedor_id, total=0, observaciones=""):
    db = SessionLocal()
    compra = db.query(Compra).filter_by(numero=numero).first()
    if not compra:
        db.close()
        return False, "No se encontró la compra."
    db.delete(compra)
    db.commit()
    db.close()
    return True, "Compra eliminada."    


def eliminar_compra(numero):
    db = SessionLocal()
    compra = db.query(Compra).filter_by(numero=numero).first()
    if not compra:
        db.close()
        return False, "No se encontró la compra."
    db.delete(compra)
    db.commit()
    db.close()
    return True, "🗑️ Compra eliminada."


# ─────────────────────────────────────────
#  VENTANA LISTADO DE COMPRAS
# ─────────────────────────────────────────
def abrir_compras():
    ventana = tk.Toplevel()
    ventana.title("Listado de Compras")
    ventana.geometry("680x440")
    ventana.configure(bg=COLOR_FONDO)
    ventana.resizable(False, False)

    # ── Título ──
    tk.Label(
        ventana,
        text="🧾 Listado de Compras",
        font=FUENTE_TITULO,
        bg=COLOR_ENCABEZADO,
        fg="white",
        pady=12
    ).pack(fill="x")

    # ── Botones superiores ──
    frame_botones = tk.Frame(ventana, bg=COLOR_FONDO, pady=8)
    frame_botones.pack(fill="x", padx=20)

    def actualizar_tabla():
        for row in tabla.get_children():
            tabla.delete(row)
        compras = listar_compras()
        if not compras:
            tabla.insert("", "end", values=("—", "Sin compras", "—", "—"))
        else:
            for c in compras:
                fecha = c.fecha.strftime('%d/%m/%Y') if hasattr(c, "fecha") and c.fecha else "sin fecha"
                total = f"${getattr(c, 'total', 0):,.2f}"
                obs   = getattr(c, "observaciones", "") or ""
                tabla.insert("", "end", values=(c.numero, total, fecha, obs))

    def abrir_nueva():
        abrir_nueva_compra(on_guardado=actualizar_tabla)

    def confirmar_eliminar():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccioná una compra para eliminar.", parent=ventana)
            return
        item   = tabla.item(seleccion[0])
        numero = item["values"][0]
        if numero == "—":
            return
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que querés eliminar la compra #{numero}?",
            parent=ventana
        )
        if confirmar:
            ok, msg = eliminar_compra(numero)
            messagebox.showinfo("Resultado", msg, parent=ventana)
            if ok:
                actualizar_tabla()

    tk.Button(
        frame_botones, text="➕ Nueva Compra",
        font=FUENTE_BTN, bg=COLOR_BTN_VERDE, fg=COLOR_BTN_TEXT,
        relief="flat", padx=12, pady=6, cursor="hand2",
        command=abrir_nueva
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        frame_botones, text="🗑️ Eliminar Seleccionada",
        font=FUENTE_BTN, bg=COLOR_BTN_ROJO, fg=COLOR_BTN_TEXT,
        relief="flat", padx=12, pady=6, cursor="hand2",
        command=confirmar_eliminar
    ).pack(side="left")

    # ── Tabla (Treeview) ──
    frame_tabla = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    columnas = ("numero", "total", "fecha", "observaciones")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=14)

    tabla.heading("numero",        text="# Compra")
    tabla.heading("total",         text="Total")
    tabla.heading("fecha",         text="Fecha")
    tabla.heading("observaciones", text="Observaciones")

    tabla.column("numero",        width=90,  anchor="center")
    tabla.column("total",         width=110, anchor="center")
    tabla.column("fecha",         width=100, anchor="center")
    tabla.column("observaciones", width=300, anchor="w")

    # Estilo de la tabla
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview",
        background="white", fieldbackground="white",
        rowheight=28, font=("Segoe UI", 10)
    )
    estilo.configure("Treeview.Heading",
        background=COLOR_ENCABEZADO, foreground="white",
        font=("Segoe UI", 10, "bold")
    )
    estilo.map("Treeview", background=[("selected", "#3498db")])

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar.set)

    tabla.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    actualizar_tabla()


# ─────────────────────────────────────────
#  VENTANA NUEVA COMPRA
# ─────────────────────────────────────────
def abrir_nueva_compra(on_guardado=None):
    ventana = tk.Toplevel()
    ventana.title("Nueva Compra")
    ventana.geometry("400x360")
    ventana.configure(bg=COLOR_FONDO)
    ventana.resizable(False, False)

    # ── Título ──
    tk.Label(
        ventana,
        text="🆕 Nueva Compra",
        font=FUENTE_TITULO,
        bg=COLOR_ENCABEZADO,
        fg="white",
        pady=12
    ).pack(fill="x")

    form = tk.Frame(ventana, bg=COLOR_FONDO, padx=30, pady=20)
    form.pack(fill="both", expand=True)

    def campo(label_texto):
        tk.Label(form, text=label_texto, font=FUENTE_LABEL, bg=COLOR_FONDO, anchor="w").pack(fill="x", pady=(8, 2))
        entry = tk.Entry(form, font=FUENTE_LABEL, relief="solid", bd=1)
        entry.pack(fill="x", ipady=5)
        return entry

    entry_numero   = campo("Número de compra *")
    entry_proveedor = campo("ID Proveedor *")
    entry_total    = campo("Total ($)")
    entry_obs      = campo("Observaciones")

    def guardar():
        numero_val    = entry_numero.get().strip()
        proveedor_val = entry_proveedor.get().strip()
        total_val     = entry_total.get().strip()
        obs_val       = entry_obs.get().strip()

        # ── Validaciones ──
        if not numero_val:
            messagebox.showwarning("Campo requerido", "⚠️ El número de compra es obligatorio.", parent=ventana)
            entry_numero.focus()
            return

        if not proveedor_val:
            messagebox.showwarning("Campo requerido", "⚠️ El ID de proveedor es obligatorio.", parent=ventana)
            entry_proveedor.focus()
            return

        try:
            proveedor_id = int(proveedor_val)
        except ValueError:
            messagebox.showerror("Valor inválido", "❌ El ID de proveedor debe ser un número entero.", parent=ventana)
            entry_proveedor.focus()
            return

        try:
            total = float(total_val) if total_val else 0.0
            if total < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor inválido", "❌ El total debe ser un número mayor o igual a 0.", parent=ventana)
            entry_total.focus()
            return

        ok, msg = crear_compra(numero_val, proveedor_id, total, obs_val)

        if ok:
            messagebox.showinfo("Éxito", msg, parent=ventana)
            if on_guardado:
                on_guardado()
            ventana.destroy()
        else:
            messagebox.showerror("Error", msg, parent=ventana)

    tk.Button(
        form,
        text="💾 Guardar Compra",
        font=FUENTE_BTN,
        bg=COLOR_BTN_VERDE,
        fg=COLOR_BTN_TEXT,
        relief="flat",
        padx=14, pady=8,
        cursor="hand2",
        command=guardar
    ).pack(pady=(18, 0), fill="x")