# ui/base_app.py
import os
import sys
import time
import json
import ttkbootstrap as tb
from tkinter import PhotoImage, messagebox

from ui.tela_inicial import TelaInicial
from ui.tela_selecao import TelaSelecao
from ui.tela_configuracao import TelaConfiguracao
from ui.tela_monitoramento import TelaMonitoramento
from ui.tela_ciclos import TelaCiclos
from ui.tela_historico import TelaHistorico

# import do ESPReader para poder recriar ao retomar
try:
    from core.monitor import ESPReader
except Exception:
    ESPReader = None  # se não disponível, continuamos mas sem reconectar serial


class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("Monitor de Bateria")
        self.geometry("1200x700")

        # Comunicação com ESP
        self.esp_reader = None
        self.simulacao_dados = {}

        # Arquivo de log
        self.log_file = os.path.join(os.getcwd(), "assets", "dados", "simulacao_log.json")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ícone
        caminho_icone = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "icon.png")
        caminho_icone = os.path.abspath(caminho_icone)
        try:
            icon_image = PhotoImage(file=caminho_icone)
            self.iconphoto(False, icon_image)
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")

        # Container principal
        self.container = tb.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Criação de telas
        self.frames = {}
        for Tela in (TelaInicial, TelaSelecao, TelaConfiguracao, TelaMonitoramento, TelaCiclos, TelaHistorico):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Detectar simulação interrompida
        self._verificar_log()

    def _verificar_log(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                resposta = messagebox.askyesno(
                    "Retomar Simulação",
                    "Foi detectada uma simulação interrompida.\nDeseja continuar de onde parou?"
                )
                if resposta:
                    # salva nos dados do app
                    self.simulacao_dados = log_data

                    # tenta recriar e iniciar ESPReader se a porta estiver no log
                    porta = log_data.get("porta")
                    csv_path = log_data.get("csv")
                    if ESPReader is not None and porta:
                        try:
                            esp = ESPReader(porta=porta)
                            # garante que o esp saiba qual csv usar (mesmo caminho absoluto)
                            if csv_path:
                                try:
                                    esp.definir_csv(csv_path)
                                except Exception:
                                    pass
                            # guarda referência no app e inicia thread (daemon)
                            self.esp_reader = esp
                            self.esp_reader.start()
                            # deixa controller apontando também
                            # (algumas telas leem controller.esp_reader)
                            time.sleep(0.05)  # pequena margem para thread iniciar (não bloqueante)
                        except Exception as e:
                            print("Não foi possível criar ESPReader ao retomar:", e)

                    # carregar tela de monitoramento com retomar=True
                    frame = self.frames["TelaMonitoramento"]
                    # chamar atualizar_dados com retomar=True
                    try:
                        frame.atualizar_dados(self.simulacao_dados, retomar=True)
                    except TypeError:
                        # se versão antiga do método atualizar_dados (sem retomar param)
                        frame.atualizar_dados(self.simulacao_dados)
                    self.show_frame("TelaMonitoramento")
                else:
                    try:
                        os.remove(self.log_file)
                    except Exception:
                        pass
                    self.show_frame("TelaInicial")
            except Exception as e:
                print("Erro ao ler log:", e)
                self.show_frame("TelaInicial")
        else:
            self.show_frame("TelaInicial")

    def show_frame(self, nome):
        """Mostra a tela indicada pelo nome da classe"""
        frame = self.frames[nome]

        # Se for Monitoramento, atualiza dados e cria log
        if nome == "TelaMonitoramento" and hasattr(frame, "atualizar_dados"):
            frame.atualizar_dados(self.simulacao_dados)
            frame._criar_log()

        # Atualiza histórico para voltar à TelaInicial
        if nome == "TelaHistorico":
            if hasattr(frame, "btn_voltar"):
                frame.btn_voltar.config(command=lambda: self.show_frame("TelaInicial"))

        frame.tkraise()

    def voltar_tela_inicial_com_log(self):
        if not self.simulacao_dados:
            self.show_frame("TelaInicial")
            return

        resposta = messagebox.askyesno(
            "Interromper Simulação",
            "Deseja interromper a leitura de dados?\nSe sim, o arquivo de log será apagado."
        )
        if resposta:
            if self.esp_reader:
                try:
                    self.esp_reader.parar()
                except Exception:
                    pass
            if os.path.exists(self.log_file):
                try:
                    os.remove(self.log_file)
                except Exception:
                    pass
            self.simulacao_dados = {}
            self.show_frame("TelaInicial")

    def on_closing(self):
        if hasattr(self, "frames") and "TelaMonitoramento" in self.frames:
            # Só pergunta se estiver na tela de monitoramento e log existe
            if self.frames["TelaMonitoramento"].winfo_ismapped() and os.path.exists(self.log_file):
                from tkinter import messagebox
                resposta = messagebox.askyesno(
                    "Interromper Simulação",
                    "Deseja interromper a leitura de dados e fechar o app?"
                )
                if not resposta:
                    return  # Cancela o fechamento

        # Para ESPReader
        if self.esp_reader is not None:
            try:
                self.esp_reader.parar()
            except Exception:
                pass
        # Remove arquivo de log
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception:
                pass

        # Para frames que usam after ou matplotlib
        for frame in getattr(self, "frames", {}).values():
            try:
                if hasattr(frame, 'ani') and frame.ani.event_source:
                    try:
                        frame.ani.event_source.stop()
                    except Exception:
                        pass
                frame.destroy()
            except Exception:
                pass

        try:
            self.destroy()
        except Exception:
            pass

        os._exit(0)