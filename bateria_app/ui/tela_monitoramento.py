# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from collections import deque
import time
import os
import json
from tkinter import messagebox


class TelaMonitoramento(tb.Frame):
    """
    Monitoramento de bateria com gráfico em tempo real
    integrado ao Tkinter, reaproveitando os métodos de CSV
    da ESPReader e exibindo também a corrente em tempo real.
    """
    LOG_FILE = os.path.join(os.getcwd(), "assets", "dados", "simulacao_log.json")

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modo_ciclos = False

        # =========================
        # Dados e gráfico
        # =========================
        self.MAX_PONTOS = 300
        self.dados_tensao = deque(maxlen=self.MAX_PONTOS)
        self.dados_tempo = deque(maxlen=self.MAX_PONTOS)
        self.dados_corrente = deque(maxlen=self.MAX_PONTOS)
        self.tempo_inicial = time.time()
        self.after_id = None
        self.csv_file = None

        # =========================
        # Layout principal
        # =========================
        conteudo = tb.Frame(self)
        conteudo.pack(padx=10, pady=10, fill="both", expand=True)

        # Top info
        frame_info = tb.Frame(conteudo)
        frame_info.pack(fill="x", pady=(0, 5))

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

        # Linha Tensão e Corrente (lado a lado)
        frame_medidas = tb.Frame(conteudo)
        frame_medidas.pack(fill="x", pady=(10, 10))
        self.tensao_label = tb.Label(
            frame_medidas,
            text="Tensão: -- V",
            font=("Segoe UI", 22, "bold"),
            foreground="#4CAF50"  # Verde
        )
        self.tensao_label.grid(row=0, column=0, padx=20, sticky="e")

        self.corrente_label = tb.Label(
            frame_medidas,
            text="Corrente: -- A",
            font=("Segoe UI", 22, "bold"),
            foreground="#2196F3"  # Azul
        )
        self.corrente_label.grid(row=0, column=1, padx=20, sticky="w")

        frame_medidas.grid_columnconfigure((0, 1), weight=1)

        # Modo / Carga / Descarga
        frame_status = tb.Frame(conteudo)
        frame_status.pack(fill="x", pady=(0, 10))
        self.modo_label = tb.Label(frame_status, text="Modo: --")
        self.carga_label = tb.Label(frame_status, text="Carga: --")
        self.descarga_label = tb.Label(frame_status, text="Descarga: --")
        self.modo_label.grid(row=0, column=0, padx=10)
        self.carga_label.grid(row=0, column=1, padx=10)
        self.descarga_label.grid(row=0, column=2, padx=10)
        frame_status.grid_columnconfigure((0, 1, 2), weight=1)

        # Gráfico
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.line_tensao, = self.ax.plot([], [], color='tab:green', label="Tensão (V)")
        self.line_corrente, = self.ax.plot([], [], color='tab:blue', label="Corrente (A)")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Valor")
        self.ax.set_title("Monitoramento em Tempo Real")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=conteudo)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(0, 10))

        # Botões
        frame_botoes = tb.Frame(conteudo)
        frame_botoes.pack(pady=(10, 0))
        self.frame_botoes = frame_botoes

        self.btn_carga = tb.Button(frame_botoes, text="▶️ Iniciar Carga", bootstyle=SUCCESS, command=self.iniciar_carga)
        self.btn_carga.grid(row=0, column=0, padx=5)
        self.btn_descarga = tb.Button(frame_botoes, text="⚡ Iniciar Descarga", bootstyle=INFO, command=self.iniciar_descarga)
        self.btn_descarga.grid(row=0, column=1, padx=5)
        self.btn_desativar = tb.Button(frame_botoes, text="⏹ Desativar Tudo", bootstyle=WARNING, command=self.desativar_tudo)
        self.btn_desativar.grid(row=0, column=2, padx=5)

        # Voltar
        frame_voltar = tb.Frame(conteudo)
        frame_voltar.pack(pady=(15, 5))
        tb.Button(
            frame_voltar,
            text="← Voltar à Tela Inicial",
            bootstyle="secondary-outline",
            width=25,
            command=lambda: self.voltar_tela_inicial()
        ).pack()

        # Atualização
        self.ani = FuncAnimation(self.fig, self.atualizar_grafico, interval=1000, cache_frame_data=False)
        self.atualizar_labels()

    # =========================
    # Atualizar dados (início)
    # =========================
    def atualizar_dados(self, dados, retomar=False):
        self.controller.simulacao_dados = dados or {}
        tipo = (dados or {}).get("tipo", "")
        esp = getattr(self.controller, "esp_reader", None)

        if dados and "csv" in dados and esp:
            self.csv_file = dados["csv"]
            esp.definir_csv(self.csv_file)

        if not retomar:
            self._criar_log()

        # Ciclos automáticos
        if tipo.lower() == "ciclos":
            self.modo_ciclos = True
            if esp:
                esp.modo = "AUTO"
                try:
                    esp.bateria_controller.alternar_modo()
                except Exception:
                    pass
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid_remove()
        else:
            self.modo_ciclos = False
            if esp:
                esp.modo = "MANUAL"
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid()

        # Envio periódico
        if esp:
            try:
                esp.iniciar_envio_periodico("USB ON", intervalo=3)
                print("[MONITORAMENTO] Envio periódico de 'USB ON' iniciado.")
            except Exception as e:
                print(f"[MONITORAMENTO] Falha ao iniciar envio periódico: {e}")

    # =========================
    # Log
    # =========================
    def _criar_log(self):
        try:
            os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
            log_info = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "bateria": self.controller.simulacao_dados.get("dados_bateria", {}).get("nome", "---"),
                "serial": self.controller.simulacao_dados.get("porta", "---"),
                "arquivo_csv": self.controller.simulacao_dados.get("csv", "---"),
                "modo": self.controller.simulacao_dados.get("tipo", "---"),
            }
            with open(self.LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(log_info, f, indent=2, ensure_ascii=False)
            print(f"[LOG] Criado com sucesso: {self.LOG_FILE}")
        except Exception as e:
            print(f"[LOG] Erro ao criar o arquivo de log: {e}")

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
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.parar_envio_periodico()

        if os.path.exists(self.LOG_FILE):
            resposta = messagebox.askyesno(
                "Interromper Simulação",
                "Deseja interromper a leitura de dados?\nSe sim, o log será apagado."
            )
            if resposta:
                if self.controller.esp_reader:
                    self.controller.esp_reader.parar()
                self._apagar_log()
                self.controller.simulacao_dados = {}
                self.controller.show_frame("TelaInicial")
        else:
            self.controller.show_frame("TelaInicial")

    # =========================
    # Atualização de labels
    # =========================
    def atualizar_labels(self):
        if not self.winfo_exists():
            return
        try:
            dados = getattr(self.controller, "simulacao_dados", {})
            esp = getattr(self.controller, "esp_reader", None)

            if esp and esp.ultima_tensao is not None:
                self.tensao_label.config(text=f"Tensão: {esp.ultima_tensao:.3f} V")
            else:
                self.tensao_label.config(text="Tensão: -- V")

            if esp and esp.corrente is not None:
                self.corrente_label.config(text=f"Corrente: {esp.corrente:.3f} A")
            else:
                self.corrente_label.config(text="Corrente: -- A")

            if esp:
                self.modo_label.config(text=f"Modo: {esp.modo}")
                self.carga_label.config(text=f"Carga: {esp.carga}")
                self.descarga_label.config(text=f"Descarga: {esp.descarga}")

            if "csv" in dados:
                rel_csv = os.path.relpath(dados["csv"], os.getcwd())
                self.csv_label.config(text=f"CSV: {rel_csv}")

            if self.winfo_exists():
                self.after_id = self.after(1000, self.atualizar_labels)
        except Exception:
            pass

    # =========================
    # Gráfico
    # =========================
    def atualizar_grafico(self, frame):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp or not esp.ultima_tensao:
            return

        try:
            t = time.time() - self.tempo_inicial
            self.dados_tempo.append(t)
            self.dados_tensao.append(esp.ultima_tensao)
            self.dados_corrente.append(esp.corrente or 0)

            # CSV via ESPReader
            if esp.arquivo_csv:
                esp.salvar_csv(esp.ultima_tensao, esp.corrente)

            # Atualiza gráfico
            self.ax.clear()
            self.ax.plot(self.dados_tempo, self.dados_tensao, color='tab:green', label="Tensão (V)")
            self.ax.plot(self.dados_tempo, self.dados_corrente, color='tab:blue', label="Corrente (A)")
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Valor")
            self.ax.set_title("Monitoramento em Tempo Real")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
        except Exception:
            pass
        
    # =========================
    # Destroy seguro
    # =========================
    def destroy(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            try:
                esp.parar_envio_periodico()
                print("[MONITORAMENTO] Envio periódico de 'USB ON' parado (destroy).")
            except Exception:
                pass

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
