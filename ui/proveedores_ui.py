import tkinter as tk
from routes.proveedores import mostrar_modulo_proveedores

class ProveedoresFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        
        # Renderizamos el módulo de proveedores pasando este frame como base
        mostrar_modulo_proveedores(self)