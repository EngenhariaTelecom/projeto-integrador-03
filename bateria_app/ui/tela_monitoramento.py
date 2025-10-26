import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TelaMonitoramento(tb.Frame):
    """
    Tela de monitoramento da bateria.
    Atualiza leitura e tensão em tempo real de forma segura,
    opcionalmente com ESPReader, mas não depende dele.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.simulacao_dados = getattr(controller, "simulacao_dados", {})

        # Layout principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        conteudo = tb.Frame(self)
        conteudo.grid(row=0, column=0, sticky="nsew")

        # Título
        tb.Label(conteudo, text="📊 Monitoramento de Bateria", font=("Helvetica", 18, "bold")).pack(pady=20)

        # Labels de dados da simulação
        self.bateria_label = tb.Label(conteudo, text="Bateria: ---")
        self.bateria_label.pack()
        self.capacidade_label = tb.Label(conteudo, text="Capacidade: ---")
        self.capacidade_label.pack()
        self.porta_label = tb.Label(conteudo, text="Porta: ---")
        self.porta_label.pack()
        self.csv_label = tb.Label(conteudo, text="CSV: ---")
        self.csv_label.pack()
        self.tipo_label = tb.Label(conteudo, text="Tipo: ---")
        self.tipo_label.pack(pady=(0,20))

        # Labels de leitura
        self.leitura_label = tb.Label(conteudo, text="Leitura: --")
        self.leitura_label.pack(pady=5)
        self.tensao_label = tb.Label(conteudo, text="Tensão: -- V")
        self.tensao_label.pack(pady=5)
        self.modo_label = tb.Label(conteudo, text="Modo: --")
        self.modo_label.pack(pady=5)
        self.carga_label = tb.Label(conteudo, text="Carga: --")
        self.carga_label.pack(pady=5)
        self.descarga_label = tb.Label(conteudo, text="Descarga: --")
        self.descarga_label.pack(pady=5)

        # Botão de voltar
        tb.Button(
            conteudo,
            text="⬅️ Voltar para Tela Inicial",
            bootstyle="warning-outline",
            command=lambda: controller.show_frame("TelaInicial")
        ).pack(pady=40)

        # Inicia loop de atualização
        self.atualizar_labels()

    def atualizar_dados(self, dados):
        """Atualiza os labels com dados da simulação"""
        self.simulacao_dados = dados

    def atualizar_labels(self):
        """
        Atualiza labels periodicamente.
        Usa dados simulados e, se existir, ESPReader.
        """
        # Atualiza dados da simulação
        dados = self.simulacao_dados
        bateria = dados.get("dados_bateria", {})
        self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
        self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
        self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
        self.csv_label.config(text=f"CSV: {dados.get('csv','---')}")
        tipo = dados.get("tipo","---")
        ciclos = dados.get("ciclos",1)
        self.tipo_label.config(text=f"Tipo: {tipo}, Ciclos: {ciclos}")

        # Atualiza valores do ESPReader se existir
        esp = getattr(self.controller, "esp_reader", None)
        if esp and esp.running:
            if esp.ultima_tensao is not None:
                self.leitura_label.config(text=f"Leitura: {esp.ultima_leitura}")
                self.tensao_label.config(text=f"Tensão: {esp.ultima_tensao:.3f} V")
                self.modo_label.config(text=f"Modo: {esp.modo}")
                self.carga_label.config(text=f"Carga: {esp.carga}")
                self.descarga_label.config(text=f"Descarga: {esp.descarga}")
        else:
            # Valores padrões se ESPReader não estiver ativo
            self.leitura_label.config(text="Leitura: --")
            self.tensao_label.config(text="Tensão: -- V")
            self.modo_label.config(text="Modo: --")
            self.carga_label.config(text="Carga: --")
            self.descarga_label.config(text="Descarga: --")

        # Reexecuta a cada 1 segundo
        self.after(1000, self.atualizar_labels)
