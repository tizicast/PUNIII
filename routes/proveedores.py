import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from extensiones import SessionLocal
from models import Proveedor

# ======================================================
# TEMA OSCURO NARANJA
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"
COLOR_CARD = "#202020"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_ROJO = "#ef4444"
COLOR_AZUL = "#0288D1"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_INPUT = "#262626"
COLOR_BORDE = "#2f2f2f"

FUENTE = "Segoe UI"

# =====================================================================
# LÓGICA DE BASE DE DATOS (CRUD)
# =====================================================================

def listar_proveedores():
    db = SessionLocal()
    try:
        data = db.query(Proveedor).filter(Proveedor.activo == True).all()
        return data
    except Exception as e:
        print(f"Error al listar: {e}")
        return []
    finally:
        db.close()


def buscar_proveedores(texto):
    db = SessionLocal()
    try:
        data = db.query(Proveedor).filter(
            (Proveedor.activo == True) & 
            (
                (Proveedor.nombre.like(f"%{texto}%")) | 
                (Proveedor.cuit.like(f"%{texto}%")) |
                (Proveedor.contacto.like(f"%{texto}%"))
            )
        ).all()
        return data
    except Exception as e:
        print(f"Error al buscar: {e}")
        return []
    finally:
        db.close()


def crear_proveedor(nombre, cuit, telefono, email, direccion, contacto):
    db = SessionLocal()
    try:
        existente = db.query(Proveedor).filter_by(cuit=cuit, activo=True).first()
        if existente:
            return False, "Ya existe un proveedor activo con ese CUIT."

        nuevo_proveedor = Proveedor(
            nombre=nombre, cuit=cuit, telefono=telefono,
            email=email, direccion=direccion, contacto=contacto,
            activo=True
        )
        db.add(nuevo_proveedor)
        db.commit()
        return True, "Proveedor creado correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al guardar: {str(e)}"
    finally:
        db.close()


def actualizar_proveedor(id_proveedor, nombre, cuit, telefono, email, direccion, contacto):
    """Actualiza los datos de un proveedor existente."""
    db = SessionLocal()
    try:
        prov = db.query(Proveedor).filter_by(id=id_proveedor, activo=True).first()
        if not prov:
            return False, "Proveedor no encontrado."
        
        # Validar que el CUIT nuevo no lo tenga otro proveedor diferente
        existente = db.query(Proveedor).filter(Proveedor.cuit == cuit, Proveedor.id != id_proveedor, Proveedor.activo == True).first()
        if existente:
            return False, "El CUIT ingresado ya pertenece a otro proveedor."

        prov.nombre = nombre
        prov.cuit = cuit
        prov.telefono = telefono
        prov.email = email
        prov.direccion = direccion
        prov.contacto = contacto
        
        db.commit()
        return True, "Proveedor actualizado correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al actualizar: {str(e)}"
    finally:
        db.close()


def eliminar_proveedor(id_proveedor):
    """Realiza la baja lógica (activo = False) usando el argumento correcto."""
    db = SessionLocal()
    try:
        prov = db.query(Proveedor).filter_by(id=id_proveedor).first()
        if not prov:
            return False, "Proveedor no encontrado."
        
        prov.activo = False
        db.commit()
        return True, "Proveedor eliminado correctamente."
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar: {str(e)}"
    finally:
        db.close()


# =====================================================================
# INTERFAZ GRÁFICA AVANZADA (TKINTER)
# =====================================================================

def mostrar_modulo_proveedores(panel_derecho):
    for widget in panel_derecho.winfo_children():
        widget.destroy()

    panel_derecho.configure(bg=COLOR_FONDO)
    
    # Variable interna para rastrear si estamos editando un ID específico
    id_seleccionado = {"id": None}

    # TÍTULO
    tk.Label(
        panel_derecho,
        text="🏭 Gestión de Proveedores",
        font=(FUENTE, 22, "bold"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO
    )

    # CONTENEDOR DEL FORMULARIO
    frame_form = tk.LabelFrame(
        panel_derecho,
        text=" Datos del proveedor ",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10, "bold"),
        relief="flat",
        bd=1
    )

    frame_form.columnconfigure(1, weight=1)
    frame_form.columnconfigure(3, weight=1)

    # =========================
    # RAZON SOCIAL
    # =========================

    tk.Label(
        frame_form,
        text="Razón Social *",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=0, column=0, sticky="w", pady=8, padx=8)

    entry_nombre = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_nombre.grid(
        row=0,
        column=1,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # =========================
    # CUIT
    # =========================

    tk.Label(
        frame_form,
        text="CUIT *",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=0, column=2, sticky="w", pady=8, padx=8)

    entry_cuit = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_cuit.grid(
        row=0,
        column=3,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # =========================
    # TELEFONO
    # =========================

    tk.Label(
        frame_form,
        text="Teléfono",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=1, column=0, sticky="w", pady=8, padx=8)

    entry_tel = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_tel.grid(
        row=1,
        column=1,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # =========================
    # EMAIL
    # =========================

    tk.Label(
        frame_form,
        text="Email",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=1, column=2, sticky="w", pady=8, padx=8)

    entry_email = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_email.grid(
        row=1,
        column=3,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # =========================
    # DIRECCION
    # =========================

    tk.Label(
        frame_form,
        text="Dirección",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=2, column=0, sticky="w", pady=8, padx=8)

    entry_direccion = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_direccion.grid(
        row=2,
        column=1,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # =========================
    # CONTACTO
    # =========================

    tk.Label(
        frame_form,
        text="Contacto",
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
        font=(FUENTE, 10)
    ).grid(row=2, column=2, sticky="w", pady=8, padx=8)

    entry_contacto = tk.Entry(
        frame_form,
        font=(FUENTE, 10),
        bg=COLOR_INPUT,
        fg="white",
        insertbackground="white",
        relief="flat",
        bd=0
    )

    entry_contacto.grid(
        row=2,
        column=3,
        sticky="ew",
        pady=8,
        padx=8,
        ipady=6
    )

    # BOTONES DEL FORMULARIO
    frame_botones_form = tk.Frame(frame_form, bg=COLOR_PANEL)
    frame_botones_form.grid(row=3, column=0, columnspan=4, sticky="e", pady=12)

    def guardar_proveedor_interfaz():
        nom = entry_nombre.get().strip()
        cuit = entry_cuit.get().strip()
        tel = entry_tel.get().strip()
        em = entry_email.get().strip()
        dir_prov = entry_direccion.get().strip()
        cont = entry_contacto.get().strip()

        if not nom or not cuit:
            messagebox.showwarning("Campos Vacíos", "La Razón Social y el CUIT son obligatorios.")
            return

        # Si hay un ID seleccionado, editamos; de lo contrario, creamos uno nuevo
        if id_seleccionado["id"]:
            exito, mensaje = actualizar_proveedor(
                id_proveedor=id_seleccionado["id"], nombre=nom, cuit=cuit,
                telefono=tel, email=em, direccion=dir_prov, contacto=cont
            )
        else:
            exito, mensaje = crear_proveedor(
                nombre=nom, cuit=cuit, telefono=tel, email=em, direccion=dir_prov, contacto=cont
            )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            limpiar_campos()
            refrescar_tabla()
        else:
            messagebox.showerror("Error", mensaje)

    def limpiar_campos():
        id_seleccionado["id"] = None
        entry_nombre.delete(0, tk.END)
        entry_cuit.delete(0, tk.END)
        entry_tel.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_direccion.delete(0, tk.END)
        entry_contacto.delete(0, tk.END)
        btn_guardar.configure(text="💾 Guardar Proveedor",bg=COLOR_NARANJA)
        if tabla.selection():
            tabla.selection_remove(tabla.selection())

    btn_guardar = tk.Button(
        frame_botones_form, text="💾 Guardar Proveedor", 
        bg="#4CAF50", fg="white", font=(FUENTE, 10, "bold"), 
        padx=15, pady=4, relief="flat", command=guardar_proveedor_interfaz
    )
    btn_guardar.pack(side="right", padx=5)
    
    btn_limpiar = tk.Button(
        frame_botones_form, text="🧹 Limpiar / Nuevo", 
        bg="#555555", fg="white", font=("Arial", 10), 
        padx=10, pady=4, relief="flat", command=limpiar_campos
    )
    btn_limpiar.pack(side="right", padx=5)

    # FILTRO RÁPIDO DE BÚSQUEDA
    frame_buscar = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_buscar.pack(fill="x", padx=20, pady=(15, 5))

    tk.Label(frame_buscar, text="🔍 Filtro rápido:", font=(FUENTE, 10, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO).pack(side="left", padx=5)
    entry_buscar = tk.Entry(frame_buscar, font=("Arial", 10), width=35)
    entry_buscar.pack(side="left", padx=5)

    def al_escribir_busqueda(event):
        refrescar_tabla(entry_buscar.get().strip())
        
    entry_buscar.bind("<KeyRelease>", al_escribir_busqueda)

    # TABLA DE DATOS (TREEVIEW)
    frame_tabla = tk.Frame(panel_derecho, bg=COLOR_PANEL)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=5)

    columnas = ("id", "nombre", "cuit", "telefono", "email", "direccion", "contacto")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse")
    
    tabla.heading("id", text="ID")
    tabla.heading("nombre", text="Razón Social / Nombre")
    tabla.heading("cuit", text="CUIT")
    tabla.heading("telefono", text="Teléfono")
    tabla.heading("email", text="Email")
    tabla.heading("direccion", text="Dirección")
    tabla.heading("contacto", text="Contacto Vendedor")

    tabla.column("id", width=40, anchor="center")
    tabla.column("nombre", width=180, anchor="w")
    tabla.column("cuit", width=100, anchor="center")
    tabla.column("telefono", width=90, anchor="center")
    tabla.column("email", width=130, anchor="w")
    tabla.column("direccion", width=150, anchor="w")
    tabla.column("contacto", width=110, anchor="w")

    scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scrollbar_y.set)
    
    tabla.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")

    # Pasar los datos de la fila a las cajas de texto al hacer clic
    def al_seleccionar_fila(event):
        item_seleccionado = tabla.selection()
        if not item_seleccionado:
            return
        v = tabla.item(item_seleccionado, "values")
        
        # Guardamos el ID que se va a editar
        id_seleccionado["id"] = int(v[0])
        
        # Rellenamos el formulario
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, v[1])
        
        entry_cuit.delete(0, tk.END)
        entry_cuit.insert(0, v[2])
        
        entry_tel.delete(0, tk.END)
        entry_tel.insert(0, v[3] if v[3] != "-" else "")
        
        entry_email.delete(0, tk.END)
        entry_email.insert(0, v[4] if v[4] != "-" else "")
        
        entry_direccion.delete(0, tk.END)
        entry_direccion.insert(0, v[5] if v[5] != "-" else "")
        
        entry_contacto.delete(0, tk.END)
        entry_contacto.insert(0, v[6] if v[6] != "-" else "")
        
        # Cambiamos el aspecto del botón para avisar que está en modo edición
        btn_guardar.configure(text="✏️ Modificar Proveedor", bg=COLOR_AZUL)

    tabla.bind("<<TreeviewSelect>>", al_seleccionar_fila)

    # ACCIONES INFERIORES: ELIMINAR
    frame_acciones = tk.Frame(panel_derecho, bg=COLOR_FONDO)
    frame_acciones.pack(fill="x", padx=20, pady=15)

    def ejecutar_eliminacion():
        item_seleccionado = tabla.selection()
        if not item_seleccionado:
            messagebox.showwarning("Atención", "Selecciona un proveedor de la lista haciendo clic sobre él.")
            return
        
        valores = tabla.item(item_seleccionado, "values")
        id_prov = int(valores[0])
        nombre_prov = valores[1]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de dar de baja al proveedor:\n'{nombre_prov}'?"):
            # Corregido: Se envía la variable id_prov directamente
            exito, mensaje = eliminar_proveedor(id_prov)
            if exito:
                messagebox.showinfo("Operación Exitosa", mensaje)
                limpiar_campos()
                refrescar_tabla()
            else:
                messagebox.showerror("Error", mensaje)

    btn_eliminar = tk.Button(
        frame_acciones, text="❌ Eliminar Proveedor Seleccionado", 
        bg=COLOR_ROJO, fg="white", font=("Arial", 10, "bold"), 
        padx=15, pady=6, relief="flat", command=ejecutar_eliminacion
    )
    btn_eliminar.pack(side="left")

    def refrescar_tabla(filtro_texto=""):
        for item in tabla.get_children():
            tabla.delete(item)
        
        if filtro_texto:
            proveedores = buscar_proveedores(filtro_texto)
        else:
            proveedores = listar_proveedores()
        
        for p in proveedores:
            tabla.insert(
                "", "end", 
                values=(
                    p.id, p.nombre, p.cuit, 
                    p.telefono if p.telefono else "-",
                    p.email if p.email else "-",
                    p.direccion if p.direccion else "-",
                    p.contacto if p.contacto else "-"
                )
            )

    refrescar_tabla()