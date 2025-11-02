# ui/base_app.py
import os
import ttkbootstrap as tb
from ui.tela_inicial import TelaInicial
from ui.tela_selecao import TelaSelecao
from ui.tela_configuracao import TelaConfiguracao
from ui.tela_monitoramento import TelaMonitoramento
from ui.tela_ciclos import TelaCiclos
from ui.tela_historico import TelaHistorico
from tkinter import PhotoImage, messagebox
import json

class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("Monitor de Bateria v1.0")
        self.geometry("1200x700")

        # Backend ESPReader
        self.esp_reader = None
        self.simulacao_dados = {}

        # Caminho do arquivo de log
        self.log_file = os.path.join(os.getcwd(), "assets", "dados", "simulacao_log.json")

        # Configura protocolo de fechamento
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

        # Inicializa todas as telas
        self.frames = {}
        for Tela in (TelaInicial, TelaSelecao, TelaConfiguracao, TelaMonitoramento, TelaCiclos, TelaHistorico):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Verifica se há log de simulação intacto
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    log_data = json.load(f)
                resposta = messagebox.askyesno(
                    "Retomar Simulação",
                    "Foi detectada uma simulação interrompida.\nDeseja continuar de onde parou?"
                )
                if resposta:
                    # Retoma simulação
                    self.simulacao_dados = log_data
                    self.show_frame("TelaMonitoramento")
                else:
                    os.remove(self.log_file)
                    self.show_frame("TelaInicial")
            except Exception:
                self.show_frame("TelaInicial")
        else:
            self.show_frame("TelaInicial")

    def show_frame(self, nome):
        """Mostra a tela indicada pelo nome da classe"""
        frame = self.frames[nome]

        # Se for Monitoramento, atualiza dados e cria log
        if nome == "TelaMonitoramento" and hasattr(frame, "atualizar_dados"):
            frame.atualizar_dados(self.simulacao_dados)
            self._criar_log()

        # Atualiza histórico para voltar à TelaInicial
        if nome == "TelaHistorico":
            if hasattr(frame, "btn_voltar"):
                frame.btn_voltar.config(command=lambda: self.show_frame("TelaInicial"))

        frame.tkraise()

    def _criar_log(self):
        """Cria ou atualiza o arquivo de log com os dados atuais da simulação"""
        pasta = os.path.dirname(self.log_file)
        os.makedirs(pasta, exist_ok=True)
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.simulacao_dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Erro criando log de simulação:", e)

    def voltar_tela_inicial_com_log(self):
        """Função para o botão 'Voltar à Tela Inicial' na TelaMonitoramento"""
        if not self.simulacao_dados:
            self.show_frame("TelaInicial")
            return

        resposta = messagebox.askyesno(
            "Interromper Simulação",
            "Deseja interromper a leitura de dados?\nSe sim, o arquivo de log será apagado."
        )
        if resposta:
            # Interrompe leitura e apaga log
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
        else:
            # Mantém simulação ativa
            pass

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