# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from collections import deque
import time
import os
import csv
from tkinter import messagebox
import json

class TelaMonitoramento(tb.Frame):
    """
    Monitoramento de bateria com gráfico em tempo real
    integrado ao Tkinter, com CSV automático, proteção
    contra erros ao fechar a aplicação, e suporte a log
    para retomada de simulação.
    """
    LOG_FILE = os.path.join(os.getcwd(), "assets", "dados", "simulacao_log.json")

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modo_ciclos = False

        # =========================
        # Configurações do gráfico e dados
        # =========================
        self.MAX_PONTOS = 300
        self.dados_tensao = deque(maxlen=self.MAX_PONTOS)
        self.dados_tempo = deque(maxlen=self.MAX_PONTOS)
        self.tempo_inicial = time.time()

        self.csv_file = None
        self.after_id = None

        # =========================
        # Layout principal
        # =========================
        conteudo = tb.Frame(self)
        conteudo.pack(padx=10, pady=10, fill="both", expand=True)

        # Top info (centralizado)
        frame_info = tb.Frame(conteudo)
        frame_info.pack(fill="x", pady=(0,5))

        info_labels = [
            tb.Label(frame_info, text="Bateria: ---"),
            tb.Label(frame_info, text="Capacidade: ---"),
            tb.Label(frame_info, text="Tipo: ---"),
            tb.Label(frame_info, text="Porta: ---"),
            tb.Label(frame_info, text="CSV: ---"),
        ]
        for i, lbl in enumerate(info_labels):
            lbl.grid(row=0, column=i, padx=12)
        frame_info.grid_columnconfigure(tuple(range(len(info_labels))), weight=1)
        self.bateria_label, self.capacidade_label, self.tipo_label, self.porta_label, self.csv_label = info_labels

        # Tensão destacada
        frame_tensao = tb.Frame(conteudo)
        frame_tensao.pack(fill="x", pady=(10,10))
        self.tensao_label = tb.Label(
            frame_tensao,
            text="Tensão: -- V",
            font=("Segoe UI", 22, "bold"),
            foreground="#4CAF50"
        )
        self.tensao_label.pack(anchor="center")

        # Modo / Carga / Descarga
        frame_status = tb.Frame(conteudo)
        frame_status.pack(fill="x", pady=(0,10))
        self.modo_label = tb.Label(frame_status, text="Modo: --")
        self.carga_label = tb.Label(frame_status, text="Carga: --")
        self.descarga_label = tb.Label(frame_status, text="Descarga: --")
        self.modo_label.grid(row=0, column=0, padx=10)
        self.carga_label.grid(row=0, column=1, padx=10)
        self.descarga_label.grid(row=0, column=2, padx=10)
        frame_status.grid_columnconfigure((0,1,2), weight=1)

        # Gráfico
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8,3))
        self.line, = self.ax.plot([], [], color='tab:blue')
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Tensão (V)")
        self.ax.set_title("Tensão da Bateria em Tempo Real")
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=conteudo)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(0,10))

        # Botões
        frame_botoes = tb.Frame(conteudo)
        frame_botoes.pack(pady=(10,0))
        self.frame_botoes = frame_botoes

        self.btn_carga = tb.Button(frame_botoes, text="▶️ Iniciar Carga", bootstyle=SUCCESS, command=self.iniciar_carga)
        self.btn_carga.grid(row=0, column=0, padx=5)
        self.btn_descarga = tb.Button(frame_botoes, text="⚡ Iniciar Descarga", bootstyle=INFO, command=self.iniciar_descarga)
        self.btn_descarga.grid(row=0, column=1, padx=5)
        self.btn_desativar = tb.Button(frame_botoes, text="⏹ Desativar Tudo", bootstyle=WARNING, command=self.desativar_tudo)
        self.btn_desativar.grid(row=0, column=3, padx=5)

        # Botão de voltar
        frame_voltar = tb.Frame(conteudo)
        frame_voltar.pack(pady=(15, 5))
        tb.Button(
            frame_voltar,
            text="← Voltar à Tela Inicial",
            bootstyle="secondary-outline",
            width=25,
            command=lambda: self.voltar_tela_inicial()
        ).pack()

        # Atualização periódica
        self.ani = FuncAnimation(self.fig, self.atualizar_grafico, interval=1000, cache_frame_data=False)
        self.atualizar_labels()

    # =========================
    # Atualizar dados
    # =========================
    def atualizar_dados(self, dados):
        self.controller.simulacao_dados = dados
        tipo = dados.get("tipo", "")
        esp = getattr(self.controller, "esp_reader", None)

        # Define CSV
        if "csv" in dados:
            self.csv_file = dados["csv"]
            self._inicializar_csv()
            self._carregar_csv_existente()

        # Log
        self._criar_log()

        if tipo.lower() == "ciclos":
            self.modo_ciclos = True
            if esp:
                esp.modo = "AUTO"
                esp.bateria_controller.alternar_modo()
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid_remove()
        else:
            self.modo_ciclos = False
            if esp:
                esp.modo = "MANUAL"
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid()

    # =========================
    # CSV
    # =========================
    def _inicializar_csv(self):
        if not self.csv_file:
            return
        pasta = os.path.dirname(self.csv_file)
        os.makedirs(pasta, exist_ok=True)
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Tempo (s)", "Tensao (V)", "Modo", "Carga", "Descarga"])

    def _carregar_csv_existente(self):
        if not self.csv_file or not os.path.exists(self.csv_file):
            return
        with open(self.csv_file, "r", newline='') as f:
            reader = csv.DictReader(f)
            self.dados_tempo.clear()
            self.dados_tensao.clear()
            for row in reader:
                try:
                    t = float(row["Tempo (s)"])
                    v = float(row["Tensao (V)"])
                    self.dados_tempo.append(t)
                    self.dados_tensao.append(v)
                except Exception:
                    continue
        if self.dados_tempo:
            self.tempo_inicial = time.time() - self.dados_tempo[-1]
        else:
            self.tempo_inicial = time.time()

    def salvar_csv(self, t, tensao, modo, carga, descarga):
        if not self.csv_file:
            return
        try:
            with open(self.csv_file, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([f"{t:.1f}", f"{tensao:.3f}", modo, carga, descarga])
        except Exception:
            pass

    # =========================
    # Log
    # =========================
    def _criar_log(self):
        os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
        try:
            with open(self.LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.controller.simulacao_dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Erro criando log:", e)

    def _apagar_log(self):
        if os.path.exists(self.LOG_FILE):
            os.remove(self.LOG_FILE)

    # =========================
    # Botões
    # =========================
    def iniciar_carga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.carga = "ON"
            esp.descarga = "OFF"
            esp.modo = "MANUAL"
            esp.bateria_controller.iniciar_carga()

    def iniciar_descarga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.descarga = "ON"
            esp.carga = "OFF"
            esp.modo = "MANUAL"
            esp.bateria_controller.iniciar_descarga()

    def alternar_modo(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.modo = "AUTO"
            esp.bateria_controller.alternar_modo()

    def desativar_tudo(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.carga = "OFF"
            esp.descarga = "OFF"
            esp.modo = "MANUAL"
            esp.bateria_controller.desligar_tudo()

    # =========================
    # Voltar com confirmação
    # =========================
    def voltar_tela_inicial(self):
        if os.path.exists(self.LOG_FILE):
            resposta = messagebox.askyesno(
                "Interromper Simulação",
                "Deseja interromper a leitura de dados?\nSe sim, o log será apagado."
            )
            if resposta:
                if self.controller.esp_reader:
                    try:
                        self.controller.esp_reader.parar()
                    except Exception:
                        pass
                self._apagar_log()
                self.controller.simulacao_dados = {}
                self.controller.show_frame("TelaInicial")
        else:
            self.controller.show_frame("TelaInicial")

    # =========================
    # Atualização labels
    # =========================
    def atualizar_labels(self):
        if not self.winfo_exists():
            return
        try:
            dados = getattr(self.controller, "simulacao_dados", {})

            if "csv" in dados:
                if self.csv_file != dados["csv"]:
                    self.csv_file = dados["csv"]
                    self._inicializar_csv()
                    self._carregar_csv_existente()
                rel_csv = os.path.relpath(self.csv_file, os.getcwd())
                self.csv_label.config(text=f"CSV: {rel_csv}")

            bateria = dados.get("dados_bateria", {})
            self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
            self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
            self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
            tipo = dados.get("tipo","---")
            ciclos = dados.get("ciclos",1)
            self.tipo_label.config(text=f"Tipo: {tipo}, Ciclos: {ciclos}")

            esp = getattr(self.controller, "esp_reader", None)
            if esp:
                self.tensao_label.config(text=f"{esp.ultima_tensao:.3f} V" if esp.ultima_tensao else "Tensão: -- V")
                self.modo_label.config(text=f"Modo: {esp.modo}")
                self.carga_label.config(text=f"Carga: {esp.carga}")
                self.descarga_label.config(text=f"Descarga: {esp.descarga}")

                if not self.modo_ciclos:
                    if esp.carga == "ON":
                        self.btn_carga.grid_remove()
                        self.btn_descarga.grid()
                    elif esp.descarga == "ON":
                        self.btn_descarga.grid_remove()
                        self.btn_carga.grid()
                    else:
                        self.btn_carga.grid()
                        self.btn_descarga.grid()

            if self.winfo_exists():
                self.after_id = self.after(1000, self.atualizar_labels)
        except Exception:
            pass

    # =========================
    # Gráfico
    # =========================
    def atualizar_grafico(self, frame):
        if not self.winfo_exists():
            return
        try:
            esp = getattr(self.controller, "esp_reader", None)
            if esp and esp.ultima_tensao is not None:
                t = time.time() - self.tempo_inicial
                self.dados_tempo.append(t)
                self.dados_tensao.append(esp.ultima_tensao)
                self.salvar_csv(t, esp.ultima_tensao, esp.modo, esp.carga, esp.descarga)

            if len(self.dados_tempo) > 0:
                self.ax.clear()
                self.ax.plot(self.dados_tempo, self.dados_tensao, color='tab:blue')
                self.ax.set_xlabel("Tempo (s)")
                self.ax.set_ylabel("Tensão (V)")
                self.ax.set_title("Tensão da Bateria em Tempo Real")
                self.ax.grid(True)
                try:
                    self.ax.set_ylim(0, self.controller.simulacao_dados["dados_bateria"]["tensao_descarga"]*1.1)
                except Exception:
                    pass
                self.canvas.draw()
        except Exception:
            pass

    # =========================
    # Destroy seguro
    # =========================
    def destroy(self):
        if hasattr(self, 'after_id') and self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

        if hasattr(self, 'ani') and self.ani.event_source:
            try:
                self.ani.event_source.stop()
            except Exception:
                pass
            del self.ani

        if hasattr(self, 'fig'):
            try:
                plt.close(self.fig)
            except Exception:
                pass

        super().destroy()