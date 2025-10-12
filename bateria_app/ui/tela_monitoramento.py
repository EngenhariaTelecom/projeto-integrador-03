# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time

class TelaMonitoramento(tb.Frame):
    """
    Tela de monitoramento da bateria.
    Mostra leitura e tensão em tempo real vindas do ESPReader.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # referência ao BatteryApp

        # Layout principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        conteudo = tb.Frame(self)
        conteudo.grid(row=0, column=0, sticky="nsew")

        # Título
        tb.Label(conteudo, text="📊 Monitoramento de Bateria", font=("Helvetica", 18, "bold")).pack(pady=20)

        # Labels que receberão os dados do ESPReader
        self.leitura_label = tb.Label(conteudo, text="Leitura: --")
        self.leitura_label.pack(pady=5)

        self.tensao_label = tb.Label(conteudo, text="Tensão: -- V")
        self.tensao_label.pack(pady=5)

        # Botões de navegação
        btns = tb.Frame(conteudo)
        btns.pack(pady=40)
        tb.Button(btns, text="Testes de Ciclo", bootstyle="info",
                  command=lambda: controller.show_frame("TelaCiclos")).grid(row=0, column=0, padx=10)
        tb.Button(btns, text="Histórico", bootstyle="secondary",
                  command=lambda: controller.show_frame("TelaHistorico")).grid(row=0, column=1, padx=10)
        tb.Button(btns, text="Trocar Bateria", bootstyle="warning-outline",
                  command=lambda: controller.show_frame("TelaSelecao")).grid(row=0, column=2, padx=10)

        # Thread que atualiza os labels em tempo real
        threading.Thread(target=self.atualizar_labels, daemon=True).start()

    def atualizar_labels(self):
        """
        Loop que atualiza os dados vindos do backend ESPReader.
        """
        while True:
            # acessa o backend pelo controller
            esp = self.controller.esp_reader
            if esp.ultima_leitura is not None:
                # atualiza labels da interface
                self.leitura_label.config(text=f"Leitura: {esp.ultima_leitura}")
                self.tensao_label.config(text=f"Tensão: {esp.ultima_tensao:.2f} V")
            time.sleep(1)  # atualiza a cada 1 segundo
