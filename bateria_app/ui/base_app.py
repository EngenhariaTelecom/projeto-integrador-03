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

# Import do ESPReader para poder recriar ao retomar
try:
    from core.monitor import ESPReader
except Exception:
    ESPReader = None  # se não disponível, o app continua mas sem conexão serial


class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("Monitor de Bateria")
        self.geometry("1200x700")

        # Comunicação com ESP
        self.esp_reader = None          # instância ativa do ESPReader
        self.simulacao_dados = {}       # dados carregados ou em execução

        # Arquivo LOG
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

        # Criação de todas as telas
        self.frames = {}
        for Tela in (
            TelaInicial,
            TelaSelecao,
            TelaConfiguracao,
            TelaMonitoramento,
            TelaCiclos,
            TelaHistorico
        ):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Verifica se existe uma simulação interrompida
        self._verificar_log()

    # ======================================================================
    # RETOMADA DE SIMULAÇÃO
    # ======================================================================
    def _verificar_log(self):
        if not os.path.exists(self.log_file):
            self.show_frame("TelaInicial")
            return

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except Exception as e:
            print("Erro ao ler log:", e)
            self.show_frame("TelaInicial")
            return

        resposta = messagebox.askyesno(
            "Retomar Simulação",
            "Foi detectada uma simulação interrompida.\nDeseja continuar de onde parou?"
        )

        if not resposta:
            try:
                os.remove(self.log_file)
            except:
                pass
            self.show_frame("TelaInicial")
            return

        # --------------------------------------------
        # RESTAURA DADOS
        # --------------------------------------------
        self.simulacao_dados = {
            "porta": log_data.get("serial"),
            "csv": log_data.get("arquivo_csv"),
            "tipo": log_data.get("modo"),
            "ciclos": log_data.get("ciclos_totais", 0),
            "ciclo_atual": log_data.get("ciclo_atual", 0),
            "descanso": log_data.get("descanso", 0),
            "descanso_restante": log_data.get("descanso_restante", 0),
            "tempo_decorrido": log_data.get("tempo_decorrido", 0),
            "dados_bateria": {
                "nome": log_data.get("bateria"),
                "capacidade": log_data.get("capacidade")
            },
            "_retomada": True   # 🔴 FLAG CRÍTICA
        }

        # --------------------------------------------
        # REABRE ESP
        # --------------------------------------------
        if ESPReader and self.simulacao_dados["porta"]:
            esp = ESPReader(porta=self.simulacao_dados["porta"])
            esp.controller = self

            esp.definir_csv(
                self.simulacao_dados["csv"],
                retomar=True,
                tempo_decorrido=self.simulacao_dados["tempo_decorrido"]
            )

            esp.set_ciclo(self.simulacao_dados["ciclo_atual"])

            self.esp_reader = esp
            esp.start()
            esp.iniciar_envio_periodico("USB ON", intervalo=3)

        frame = self.frames["TelaMonitoramento"]
        frame.atualizar_dados(self.simulacao_dados, retomar=True)

        if self.simulacao_dados["descanso_restante"] > 0:
            try:
                esp.bateria_controller.desligar_tudo()  # ou "IDLE", conforme seu firmware
            except:
                print("Erro ao desligar bateria durante retomada.")
                pass

        self.show_frame("TelaMonitoramento")

    # ======================================================================
    # TROCA DE TELAS
    # ======================================================================
    def show_frame(self, nome):
        frame = self.frames[nome]

        # Quando entra em Monitoramento manualmente
        if (
            nome == "TelaMonitoramento"
            and hasattr(frame, "atualizar_dados")
            and not self.simulacao_dados.get("_retomada")
        ):
            frame.atualizar_dados(self.simulacao_dados)
            frame._criar_log()


        if nome == "TelaHistorico":
            if hasattr(frame, "btn_voltar"):
                frame.btn_voltar.config(command=lambda: self.show_frame("TelaInicial"))

        frame.tkraise()

    # ======================================================================
    # VOLTAR PARA TELA INICIAL (COM LOG)
    # ======================================================================
    def voltar_tela_inicial_com_log(self):
        if not self.simulacao_dados:
            self.show_frame("TelaInicial")
            return

        resposta = messagebox.askyesno(
            "Interromper Simulação",
            "Deseja interromper a leitura de dados?\nSe sim, o arquivo de log será apagado."
        )
        if not resposta:
            return

        if self.esp_reader:
            try:
                self.esp_reader.parar()
            except:
                pass

        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except:
                pass

        self.simulacao_dados = {}
        self.show_frame("TelaInicial")

    def _esp_desconectada_inesperadamente(self):
    ###  Encerramento forçado por perda de comunicação com a ESP.
    ###  Simula cancelamento manual sem confirmação.
    # Para ESPReader
        if self.esp_reader:
            self.esp_reader._stop_requested = True
            try:
                self.esp_reader.parar_envio_periodico()
            except:
                pass
            try:
                self.esp_reader.parar()
            except:
                pass
            self.esp_reader = None

        # Remove log
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except:
                pass

        # Limpa dados
        self.simulacao_dados = {}

        # Volta para tela inicial
        self.show_frame("TelaInicial")

        # Informa o usuário
        messagebox.showerror(
            "ESP desconectada",
            "A ESP foi desconectada inesperadamente.\nO teste foi finalizado."
        )


    # ======================================================================
    # FECHAR A APLICAÇÃO
    # ======================================================================
    def on_closing(self):
        """Fecha o app de forma limpa."""
        fechar_agora = True

        # Se tela de monitoramento está aberta e existe log, perguntar
        if (
            hasattr(self, "frames")
            and "TelaMonitoramento" in self.frames
            and self.frames["TelaMonitoramento"].winfo_ismapped()
            and os.path.exists(self.log_file)
        ):
            resposta = messagebox.askyesno(
                "Interromper Simulação",
                "Deseja interromper a leitura de dados e fechar o app?"
            )
            fechar_agora = resposta

        if not fechar_agora:
            return

        # Parar ESPReader
        if self.esp_reader:
            try:
                self.esp_reader.parar()
            except:
                pass

        # Apagar log
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except:
                pass

        # Destruir frames com animações / after
        for frame in getattr(self, "frames", {}).values():
            try:
                if hasattr(frame, 'ani') and frame.ani.event_source:
                    frame.ani.event_source.stop()
                frame.destroy()
            except:
                pass

        try:
            self.destroy()
        except:
            pass

        os._exit(0)