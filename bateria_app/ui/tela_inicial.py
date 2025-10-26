# ui/tela_inicial.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TelaInicial(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        container = tb.Frame(self)
        container.pack(expand=True)

        tb.Label(
            container,
            text="🖥️ Monitor de Bateria",
            font=("Segoe UI", 30, "bold")
        ).pack(pady=(0, 50))

        tb.Button(
            container,
            text="⚡ Iniciar Teste",
            bootstyle=SUCCESS,
            width=20,
            padding=10,
            command=lambda: controller.show_frame("TelaSelecao")
        ).pack(pady=10)

        tb.Button(
            container,
            text="📚 Ver Histórico",
            bootstyle=INFO,
            width=20,
            padding=10,
            command=lambda: controller.show_frame("TelaHistorico")
        ).pack(pady=10)