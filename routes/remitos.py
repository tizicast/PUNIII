import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from extensiones import SessionLocal
from models import Remito, Venta

# Estética local para módulo Remitos (tema oscuro con acento naranja)
FUENTE = "Segoe UI"
COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1f1f1f"
COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"
COLOR_BORDE = "#2c2c2c"
COLOR_ACENTO = "#ff7b00"  # naranja (acento)


# =====================================================================
# LÓGICA DE BASE DE DATOS (CRUD) - SINCRONIZADA CON TU TABLA
# =====================================================================

def listar_remitos():
    """Trae todos los registros de la tabla 'remitos'."""
    db = SessionLocal()
    try:
        return db.query(Remito).all()
    except Exception as e:
        print(f"Error al listar remitos: {e}")
        return []
    finally:
        db.close()


def buscar_remitos(texto):
    """Filtra remitos por número o descripción de observaciones."""
    db = SessionLocal()
    try:
        return db.query(Remito).filter(
            (Remito.numero.like(f"%{texto}%")) | 
            (Remito.observaciones.like(f"%{texto}%"))
        ).all()
    except Exception as e:
        print(f"Error al buscar: {e}")
        return []
    finally:
        db.close()


def crear_remito(numero, venta_id, observaciones=""):
    """Inserta un registro con la estructura exacta de tu esquema."""
    db = SessionLocal()
    try:
        # Validación de duplicados para el campo 'numero'
        existente = db.query(Remito).filter_by(numero=numero).first()
        if existente:
            return False, f"El remito número {numero} ya existe."

        # Validación de clave foránea (FOREIGN KEY(venta_id) REFERENCES ventas(id))
        venta = db.query(Venta).filter_by(id=venta_id).first()
        if not venta:
            return False, f"No existe ninguna venta con el ID {venta_id}."

        # Instancia del modelo mapeada a tus 5 campos de la DB
        nuevo_remito = Remito(
            numero=numero,
            venta_id=venta_id,
            observaciones=observaciones,
            firmado=False  # Inicializa en False según la lógica de tu negocio
        )

        db.add(nuevo_remito)
        db.commit()  # <--- ACÁ SE ESCRIBE EN TU ARCHIVO FERRETERIA.DB
        return True, "Remito guardado exitosamente en la base de datos."

    except Exception as e:
        db.rollback()
        return False, f"Error en la inserción: {str(e)}"
    finally:
        db.close()


def firmar_remito(id_remito):
    """Actualiza el campo 'firmado' a True para el ID correspondiente."""
    db = SessionLocal()
    try:
        remito = db.query(Remito).filter_by(id=id_remito).first()
        if not remito:
            return False, "Remito no encontrado."

        if remito.firmado:
            return False, "Este remito ya está firmado."

        remito.firmado = True  # Modificación del booleano
        db.commit()            # Persistencia en ferreteria.db
        return True, "El remito ha sido firmado en la base de datos."

    except Exception as e:
        db.rollback()
        return False, f"Error al firmar: {str(e)}"
    finally:
        db.close()


# =====================================================================
# INTERFAZ GRÁFICA CONTROLADA (CONECTADA A TU TABLA REMITOS)
# =====================================================================

def mostrar_modulo_remitos(panel_derecho):
    for widget in panel_derecho.winfo_children():
        widget.destroy()
    panel_derecho.configure(bg=COLOR_FONDO)
    id_seleccionado = {"id": None}

    # TÍTULO PRINCIPAL
    tk.Label(
        panel_derecho, text="📄 Panel de Gestión de Remitos",
        font=(FUENTE, 18, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO
    ).pack(pady=15)

    # FORMULARIO DE ENTRADA DE DATOS
    frame_form = tk.LabelFrame(
        panel_derecho, text=" Datos del Nuevo Remito ", 
        font=(FUENTE, 10, "bold"), padx=15, pady=15, 
        bg=COLOR_PANEL, fg=COLOR_TEXTO, relief="flat", highlightbackground=COLOR_BORDE, highlightthickness=1
    )
    frame_form.pack(fill="x", padx=20, pady=5)

    frame_form.columnconfigure(1, weight=1)
    frame_form.columnconfigure(3, weight=1)

    # Campos estructurados según tu diseño de base de datos
    tk.Label(frame_form, text="Número Remito (numero):", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 10)).grid(row=0, column=0, sticky="w", pady=5, padx=5)
    entry_numero = tk.Entry(frame_form, font=(FUENTE, 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, relief="flat")
    entry_numero.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
    tk.Label(frame_form, text="ID Venta (venta_id):", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 10)).grid(row=0, column=2, sticky="w", pady=5, padx=5)
    entry_venta = tk.Entry(frame_form, font=(FUENTE, 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, relief="flat")
    entry_venta.grid(row=0, column=3, sticky="ew", pady=5, padx=5)
    tk.Label(frame_form, text="Observaciones:", bg=COLOR_PANEL, fg=COLOR_TEXTO, font=(FUENTE, 10)).grid(row=1, column=0, sticky="w", pady=5, padx=5)
    entry_obs = tk.Entry(frame_form, font=(FUENTE, 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, relief="flat")
    entry_obs.grid(row=1, column=1, columnspan=3, sticky="ew", pady=5, padx=5)

    # BOTONES DEL FORMULARIO
    frame_botones_form = tk.Frame(frame_form, bg=COLOR_PANEL)
    frame_botones_form.grid(row=2, column=0, columnspan=4, sticky="e", pady=12)

    def guardar_remito_interfaz():
        num = entry_numero.get().strip()
        v_id = entry_venta.get().strip()
        obs = entry_obs.get().strip()

        if not num or not v_id:
            messagebox.showwarning("Campos Vacíos", "El Número de Remito y el ID de Venta son campos obligatorios.")
            return

        if not v_id.isdigit():
            messagebox.showwarning("Tipo Incorrecto", "El ID de Venta debe ser un número entero.")
            return

        # Insertamos usando la función CRUD
        exito, mensaje = crear_remito(numero=num, venta_id=int(v_id), observaciones=obs)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            limpiar_campos()
            refrescar_tabla()
        else:
            messagebox.showerror("Error", mensaje)

    def limpiar_campos():
        id_seleccionado["id"] = None
        entry_numero.delete(0, tk.END)
        entry_venta.delete(0, tk.END)
        entry_obs.delete(0, tk.END)
        btn_firmar.configure(state="disabled", bg="#9E9E9E")
        if tabla.selection():
            tabla.selection_remove(tabla.selection())

    btn_guardar = tk.Button(
        frame_botones_form, text="➕ Registrar Remito", 
        bg=COLOR_ACENTO, fg="white", font=(FUENTE, 10, "bold"), 
        padx=15, pady=4, relief="flat", command=guardar_remito_interfaz, activebackground=COLOR_ACENTO
    )
    btn_guardar.pack(side="right", padx=5)
    
    btn_limpiar = tk.Button(
        frame_botones_form, text="🧹 Limpiar", 
        bg=COLOR_SECUNDARIO, fg="white", font=(FUENTE, 10), 
        padx=10, pady=4, relief="flat", command=limpiar_campos
    )
    btn_limpiar.pack(side="right", padx=5)

    # BÚSQUEDA / FILTRADO
    frame_buscar = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_buscar.pack(fill="x", padx=20, pady=(15, 5))
    tk.Label(frame_buscar, text="🔍 Buscar remito:", font=(FUENTE, 10, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left", padx=5)
    entry_buscar = tk.Entry(frame_buscar, font=(FUENTE, 10), width=35, bg=COLOR_PANEL, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, relief="flat")
    entry_buscar.pack(side="left", padx=5)

    def al_escribir_busqueda(event):
        refrescar_tabla(entry_buscar.get().strip())
        
    entry_buscar.bind("<KeyRelease>", al_escribir_busqueda)

    # TREEVIEW (Muestra de forma organizada los 5 campos de tu tabla SQL)
    frame_tabla = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=5)

    columnas = ("id", "numero", "venta_id", "observaciones", "firmado")
    # Estilizado del Treeview para tema oscuro
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    style.configure("Custom.Treeview", 
                    background=COLOR_PANEL, fieldbackground=COLOR_PANEL, foreground=COLOR_TEXTO, rowheight=26, font=(FUENTE, 10))
    style.configure("Custom.Treeview.Heading", background=COLOR_PANEL, foreground=COLOR_TEXTO, font=(FUENTE, 10, 'bold'))
    style.map('Custom.Treeview', background=[('selected', COLOR_ACENTO)], foreground=[('selected', 'white')])

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse", style="Custom.Treeview")
    
    tabla.heading("id", text="ID (id)")
    tabla.heading("numero", text="N° Remito (numero)")
    tabla.heading("venta_id", text="ID Venta (venta_id)")
    tabla.heading("observaciones", text="Observaciones")
    tabla.heading("firmado", text="Estado (firmado)")

    tabla.column("id", width=60, anchor="center")
    tabla.column("numero", width=130, anchor="center")
    tabla.column("venta_id", width=100, anchor="center")
    tabla.column("observaciones", width=240, anchor="w")
    tabla.column("firmado", width=110, anchor="center")

    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar_y.set)
    
    tabla.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # Selección mediante interacción directa con la grilla
    def al_seleccionar_fila(event):
        item_seleccionado = tabla.selection()
        if not item_seleccionado:
            return
        v = tabla.item(item_seleccionado, "values")
        
        id_seleccionado["id"] = int(v[0])
        estado = v[4]

        # Si el remito ya está firmado en la DB, bloqueamos el botón para evitar redundancias
        if estado == "⏳ Pendiente":
            btn_firmar.configure(state="normal", bg="#0288D1")
        else:
            btn_firmar.configure(state="disabled", bg="#9E9E9E")

    tabla.bind("<<TreeviewSelect>>", al_seleccionar_fila)

    # BOTÓN DE FIRMA FÍSICA EN BASE DE DATOS
    frame_acciones = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_acciones.pack(fill="x", padx=20, pady=15)

    def ejecutar_firma():
        if not id_seleccionado["id"]:
            return

        if messagebox.askyesno("Confirmación", f"¿Marcar el Remito ID {id_seleccionado['id']} como firmado en la DB?"):
            exito, mensaje = firmar_remito(id_seleccionado["id"])
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                limpiar_campos()
                refrescar_tabla()
            else:
                messagebox.showerror("Error", mensaje)

    btn_firmar = tk.Button(
        frame_acciones, text="✍️ Firmar Remito Seleccionado", 
        bg="#9E9E9E", fg="white", font=(FUENTE, 10, "bold"), 
        padx=15, pady=6, relief="flat", state="disabled", command=ejecutar_firma, activebackground=COLOR_ACENTO
    )
    btn_firmar.pack(side="left")

    def refrescar_tabla(filtro_texto=""):
        for item in tabla.get_children():
            tabla.delete(item)
        
        if filtro_texto:
            remitos = buscar_remitos(filtro_texto)
        else:
            remitos = listar_remitos()
        
        for r in remitos:
            # Mapeo visual amigable para el usuario según el booleano guardado
            est_texto = "✅ Firmado" if getattr(r, "firmado", False) else "⏳ Pendiente"
            tabla.insert(
                "", "end", 
                values=(
                    r.id, r.numero, r.venta_id, 
                    r.observaciones if r.observaciones else "-",
                    est_texto
                )
            )

    refrescar_tabla()