import tkinter as tk
from tkinter import messagebox

from routes.remitos import (
    listar_remitos,
    crear_remito,
    firmar_remito
)


# ======================================================
# COLORES - DARK ORANGE UI
# ======================================================

COLOR_FONDO = "#0f0f0f"
COLOR_PANEL = "#1a1a1a"
COLOR_CARD = "#202020"

COLOR_NARANJA = "#ff7b00"
COLOR_NARANJA_HOVER = "#ff9500"

COLOR_AZUL = "#0288D1"
COLOR_AZUL_HOVER = "#03a9f4"

COLOR_TEXTO = "#f5f5f5"
COLOR_SECUNDARIO = "#9e9e9e"

COLOR_INPUT = "#262626"
COLOR_BORDE = "#2f2f2f"

FUENTE = "Segoe UI"


# ======================================================
# HOVER BOTONES
# ======================================================

def hover(btn, normal, hover_color):

    btn.bind(
        "<Enter>",
        lambda e: btn.config(bg=hover_color) if str(btn['state']) == 'normal' else None
    )

    btn.bind(
        "<Leave>",
        lambda e: btn.config(bg=normal) if str(btn['state']) == 'normal' else None
    )


# ======================================================
# FRAME REMITOS
# ======================================================

class RemitosFrame(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent, bg=COLOR_FONDO)

        # ==================================================
        # TITULO
        # ==================================================

        header = tk.Frame(
            self,
            bg=COLOR_PANEL,
            height=90
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="📄 Gestión de Remitos",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 22, "bold")
        ).pack(side="left", padx=30, pady=25)

        # ==================================================
        # CONTENIDO
        # ==================================================

        contenido = tk.Frame(
            self,
            bg=COLOR_FONDO
        )

        contenido.pack(fill="both", expand=True, padx=25, pady=25)

        # ==================================================
        # PANEL LISTA
        # ==================================================

        panel_lista = tk.Frame(
            contenido,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )

        panel_lista.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

        tk.Label(
            panel_lista,
            text="📋 Listado de remitos",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=20)

        self.frame_lista = tk.Frame(
            panel_lista,
            bg=COLOR_PANEL
        )

        self.frame_lista.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # ==================================================
        # PANEL FORMULARIO
        # ==================================================

        panel_form = tk.Frame(
            contenido,
            bg=COLOR_PANEL,
            width=350,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1
        )

        panel_form.pack(side="right", fill="y")
        panel_form.pack_propagate(False)

        tk.Label(
            panel_form,
            text="➕ Nuevo remito",
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            font=(FUENTE, 14, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 25))

        # ==================================================
        # NÚMERO DE REMITO
        # ==================================================

        tk.Label(
            panel_form,
            text="Número Remito",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_numero = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_numero.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # ID VENTA
        # ==================================================

        tk.Label(
            panel_form,
            text="ID Venta",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_venta = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_venta.pack(
            fill="x",
            padx=20,
            pady=(8, 18),
            ipady=10
        )

        # ==================================================
        # OBSERVACIONES
        # ==================================================

        tk.Label(
            panel_form,
            text="Observaciones",
            bg=COLOR_PANEL,
            fg=COLOR_SECUNDARIO,
            font=(FUENTE, 10)
        ).pack(anchor="w", padx=20)

        self.entry_obs = tk.Entry(
            panel_form,
            bg=COLOR_INPUT,
            fg="white",
            insertbackground="white",
            relief="flat",
            font=(FUENTE, 11)
        )

        self.entry_obs.pack(
            fill="x",
            padx=20,
            pady=(8, 30),
            ipady=10
        )

        # ==================================================
        # BOTON CREAR
        # ==================================================

        btn_crear = tk.Button(
            panel_form,
            text="➕ Registrar Remito",
            command=self.guardar,
            bg=COLOR_NARANJA,
            fg="white",
            activebackground=COLOR_NARANJA_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(FUENTE, 11, "bold"),
            pady=12
        )

        btn_crear.pack(
            fill="x",
            padx=20
        )

        hover(
            btn_crear,
            COLOR_NARANJA,
            COLOR_NARANJA_HOVER
        )

        # ==================================================
        # CARGAR LISTA
        # ==================================================

        self.refrescar()

    # ======================================================
    # REFRESCAR LISTA
    # ======================================================

    def refrescar(self):

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        remitos = listar_remitos()

        # ==================================================
        # NO HAY REMITOS
        # ==================================================

        if not remitos:

            tk.Label(
                self.frame_lista,
                text="No hay remitos registrados",
                bg=COLOR_PANEL,
                fg=COLOR_SECUNDARIO,
                font=(FUENTE, 11)
            ).pack(pady=20)

            return

        # ==================================================
        # LISTADO
        # ==================================================

        for r in remitos:

            fila = tk.Frame(
                self.frame_lista,
                bg=COLOR_CARD,
                highlightbackground=COLOR_BORDE,
                highlightthickness=1
            )

            fila.pack(
                fill="x",
                pady=6,
                ipady=10
            )

            # Validar estado booleano de la DB
            est_texto = "✅ Firmado" if getattr(r, "firmado", False) else "⏳ Pendiente"
            obs_texto = r.observaciones if r.observaciones else "-"

            info = (
                f"📄 Nº: {r.numero}   |   "
                f"Venta ID: {r.venta_id}   |   "
                f"Obs: {obs_texto}   |   "
                f"{est_texto}"
            )

            tk.Label(
                fila,
                text=info,
                bg=COLOR_CARD,
                fg=COLOR_TEXTO,
                anchor="w",
                font=(FUENTE, 10)
            ).pack(
                side="left",
                padx=15,
                expand=True,
                fill="x"
            )

            # ==================================================
            # BOTON ACCION (FIRMAR SI ESTÁ PENDIENTE)
            # ==================================================
            
            if not getattr(r, "firmado", False):
                btn_firmar = tk.Button(
                    fila,
                    text="✍️ Firmar",
                    command=lambda id=r.id: self.firmar_y_refrescar(id),
                    bg=COLOR_AZUL,
                    fg="white",
                    activebackground=COLOR_AZUL_HOVER,
                    activeforeground="white",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    font=(FUENTE, 9, "bold"),
                    padx=15,
                    pady=6
                )

                btn_firmar.pack(
                    side="right",
                    padx=10
                )

                hover(
                    btn_firmar,
                    COLOR_AZUL,
                    COLOR_AZUL_HOVER
                )

    # ======================================================
    # ACCION DE FIRMA
    # ======================================================

    def firmar_y_refrescar(self, id):

        if messagebox.askyesno("Confirmación", f"¿Marcar el Remito ID {id} como firmado?"):
            exito, mensaje = firmar_remito(id)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.refrescar()
            else:
                messagebox.showerror("Error", mensaje)

    # ======================================================
    # GUARDAR
    # ======================================================

    def guardar(self):

        num = self.entry_numero.get().strip()
        v_id = self.entry_venta.get().strip()
        obs = self.entry_obs.get().strip()

        if not num or not v_id:
            messagebox.showwarning("Campos Vacíos", "El Número de Remito y el ID de Venta son obligatorios.")
            return

        if not v_id.isdigit():
            messagebox.showwarning("Tipo Incorrecto", "El ID de Venta debe ser un número entero.")
            return

        exito, msg = crear_remito(
            numero=num,
            venta_id=int(v_id),
            observaciones=obs
        )

        if exito:
            messagebox.showinfo("Información", msg)
            self.entry_numero.delete(0, "end")
            self.entry_venta.delete(0, "end")
            self.entry_obs.delete(0, "end")
            self.refrescar()
        else:
            messagebox.showerror("Error", msg)