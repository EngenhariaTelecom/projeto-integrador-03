# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TelaMonitoramento(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        conteudo = tb.Frame(self)
        conteudo.grid(row=0, column=0, sticky="nsew")

        tb.Label(conteudo, text="📊 Monitoramento de Bateria", font=("Helvetica", 18, "bold")).pack(pady=20)
        tb.Label(conteudo, text="(Simulação da tela de monitoramento — gráficos e status virão depois)").pack(pady=10)

        btns = tb.Frame(conteudo)
        btns.pack(pady=40)

        tb.Button(btns, text="Testes de Ciclo", bootstyle="info",
                  command=lambda: controller.show_frame("TelaCiclos")).grid(row=0, column=0, padx=10)
        tb.Button(btns, text="Histórico", bootstyle="secondary",
                  command=lambda: controller.show_frame("TelaHistorico")).grid(row=0, column=1, padx=10)
        tb.Button(btns, text="Trocar Bateria", bootstyle="warning-outline",
                  command=lambda: controller.show_frame("TelaSelecao")).grid(row=0, column=2, padx=10)
