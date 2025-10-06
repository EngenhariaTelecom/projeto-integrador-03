# ui/tela_selecao.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TelaSelecao(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        titulo = tb.Label(self, text="🔋 Seleção de Bateria", font=("Helvetica", 18, "bold"))
        titulo.pack(pady=20)

        desc = tb.Label(
            self,
            text="Escolha o tipo de bateria que você deseja monitorar ou testar.",
            font=("Helvetica", 11)
        )
        desc.pack(pady=(0, 20))

        # Simulação de opções (poderá ser dinâmica depois)
        for i, nome in enumerate(["Li-Ion 3.7V - 500mAh", "Li-Ion 14.8V - 1200mAh", "Alcalina 9V"]):
            card = tb.Button(
                self,
                text=nome,
                bootstyle="secondary-outline",
                width=30,
                command=lambda n=nome: self._selecionar_bateria(n)
            )
            card.pack(pady=8)

    def _selecionar_bateria(self, nome):
        print(f"Bateria selecionada: {nome}")
        self.controller.show_frame("TelaMonitoramento")
