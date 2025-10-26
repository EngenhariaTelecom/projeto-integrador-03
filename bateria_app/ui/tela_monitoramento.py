# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class TelaMonitoramento(tb.Frame):
    """
    Tela de monitoramento da bateria.
    Atualiza leitura e tensão em tempo real de forma segura,
    mas não inicializa nem depende do ESPReader.
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

        # Labels de leitura simulados
        self.leitura_label = tb.Label(conteudo, text="Leitura: --")
        self.leitura_label.pack(pady=5)
        self.tensao_label = tb.Label(conteudo, text="Tensão: -- V")
        self.tensao_label.pack(pady=5)

        # Botão de voltar para Tela Inicial
        tb.Button(
            conteudo,
            text="⬅️ Voltar para Tela Inicial",
            bootstyle="warning-outline",
            command=lambda: controller.show_frame("TelaInicial")
        ).pack(pady=40)

        # Inicia loop de atualização segura
        self.atualizar_labels()

    def atualizar_dados(self, dados):
        """Atualiza os labels com dados da simulação"""
        self.simulacao_dados = dados

        bateria = dados.get("dados_bateria", {})
        self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
        self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
        self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
        self.csv_label.config(text=f"CSV: {dados.get('csv','---')}")
        tipo = dados.get("tipo","---")
        ciclos = dados.get("ciclos",1)
        self.tipo_label.config(text=f"Tipo: {tipo}, Ciclos: {ciclos}")

    def atualizar_labels(self):
        """
        Atualiza labels periodicamente sem acessar ESPReader diretamente.
        """
        # Apenas atualiza valores simulados se existirem
        dados = self.simulacao_dados
        bateria = dados.get("dados_bateria", {})
        self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
        self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
        self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
        self.csv_label.config(text=f"CSV: {dados.get('csv','---')}")
        tipo = dados.get("tipo","---")
        ciclos = dados.get("ciclos",1)
        self.tipo_label.config(text=f"Tipo: {tipo}, Ciclos: {ciclos}")

        # Atualiza labels de leitura/tensão com valores padrão
        self.leitura_label.config(text="Leitura: --")
        self.tensao_label.config(text="Tensão: -- V")

        # Reexecuta após 1 segundo
        self.after(1000, self.atualizar_labels)