import tkinter as tk
from routes.remitos import mostrar_modulo_remitos

class RemitosFrame(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        # Delegamos la visualización completa y moderna al controlador centralizado
        mostrar_modulo_remitos(self)