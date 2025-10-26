import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class TelaMonitoramento(tb.Frame):
    """
    Tela de monitoramento da bateria.
    Atualiza leitura e tensão em tempo real de forma segura.
    Possui botões para:
      - Iniciar Carga / Iniciar Descarga
      - Alternar Modo Auto/Manual
      - Desativar Tudo
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

        tb.Label(conteudo, text="📊 Monitoramento de Bateria", font=("Helvetica", 18, "bold")).pack(pady=20)

        # Labels principais
        self.bateria_label = tb.Label(conteudo, text="Bateria: ---"); self.bateria_label.pack()
        self.capacidade_label = tb.Label(conteudo, text="Capacidade: ---"); self.capacidade_label.pack()
        self.porta_label = tb.Label(conteudo, text="Porta: ---"); self.porta_label.pack()
        self.csv_label = tb.Label(conteudo, text="CSV: ---"); self.csv_label.pack()
        self.tipo_label = tb.Label(conteudo, text="Tipo: ---"); self.tipo_label.pack(pady=(0,20))

        # Labels de leitura
        self.leitura_label = tb.Label(conteudo, text="Leitura: --"); self.leitura_label.pack(pady=5)
        self.tensao_label = tb.Label(conteudo, text="Tensão: -- V"); self.tensao_label.pack(pady=5)
        self.modo_label = tb.Label(conteudo, text="Modo: --"); self.modo_label.pack(pady=5)
        self.carga_label = tb.Label(conteudo, text="Carga: --"); self.carga_label.pack(pady=5)
        self.descarga_label = tb.Label(conteudo, text="Descarga: --"); self.descarga_label.pack(pady=5)

        # Botões de ação
        self.frame_botoes = tb.Frame(conteudo)
        self.frame_botoes.pack(pady=20)

        self.btn_carga = tb.Button(self.frame_botoes, text="Iniciar Carga", bootstyle=SUCCESS, command=self.alternar_carga)
        self.btn_descarga = tb.Button(self.frame_botoes, text="Iniciar Descarga", bootstyle=DANGER, command=self.alternar_descarga)
        self.btn_modo = tb.Button(self.frame_botoes, text="Alternar Modo", bootstyle=INFO, command=self.alternar_modo)
        self.btn_desativar = tb.Button(self.frame_botoes, text="Desativar Tudo", bootstyle=WARNING, command=self.desativar_tudo)

        self.btn_carga.grid(row=0, column=0, padx=5)
        self.btn_descarga.grid(row=0, column=1, padx=5)
        self.btn_modo.grid(row=0, column=2, padx=5)
        self.btn_desativar.grid(row=0, column=3, padx=5)

        # Botão de voltar
        tb.Button(conteudo, text="⬅️ Voltar", bootstyle=SECONDARY,
                  command=lambda: controller.show_frame("TelaInicial")).pack(pady=10)

        # Atualiza interface a cada segundo
        self.atualizar_labels()

    # ===== Funções dos botões =====

    def alternar_carga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp: return

        # Inicia carga e desativa descarga
        esp.carga = "ON"
        esp.descarga = "OFF"

    def alternar_descarga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp: return

        # Inicia descarga e desativa carga
        esp.carga = "OFF"
        esp.descarga = "ON"

    def alternar_modo(self):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp: return

        esp.modo = "MANUAL" if esp.modo == "AUTO" else "AUTO"

    def desativar_tudo(self):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp: return

        esp.carga = "OFF"
        esp.descarga = "OFF"

    # ===== Atualização de labels =====

    def atualizar_labels(self):
        dados = self.simulacao_dados
        bateria = dados.get("dados_bateria", {})
        self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
        self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
        self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
        self.csv_label.config(text=f"CSV: {dados.get('csv','---')}")
        tipo = dados.get("tipo","---")
        ciclos = dados.get("ciclos",1)
        self.tipo_label.config(text=f"Tipo: {tipo}, Ciclos: {ciclos}")

        # Atualiza dados do ESPReader
        esp = getattr(self.controller, "esp_reader", None)
        if esp and esp.running:
            self.leitura_label.config(text=f"Leitura: {esp.ultima_leitura or '--'}")
            self.tensao_label.config(text=f"Tensão: {esp.ultima_tensao:.3f} V" if esp.ultima_tensao else "Tensão: -- V")
            self.modo_label.config(text=f"Modo: {esp.modo}")
            self.carga_label.config(text=f"Carga: {esp.carga}")
            self.descarga_label.config(text=f"Descarga: {esp.descarga}")
        else:
            self.leitura_label.config(text="Leitura: --")
            self.tensao_label.config(text="Tensão: -- V")
            self.modo_label.config(text="Modo: --")
            self.carga_label.config(text="Carga: --")
            self.descarga_label.config(text="Descarga: --")

        # Atualiza botoes de carga/descarga dinamicamente
        if esp:
            if esp.carga == "ON":
                self.btn_carga.grid_remove()
                self.btn_descarga.grid()
            elif esp.descarga == "ON":
                self.btn_descarga.grid_remove()
                self.btn_carga.grid()
            else:
                self.btn_carga.grid()
                self.btn_descarga.grid()

        self.after(1000, self.atualizar_labels)