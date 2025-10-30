# ui/base_app.py
import os
import sys
import ttkbootstrap as tb
from ui.tela_inicial import TelaInicial
from ui.tela_selecao import TelaSelecao
from ui.tela_configuracao import TelaConfiguracao
from ui.tela_monitoramento import TelaMonitoramento
from ui.tela_ciclos import TelaCiclos
from ui.tela_historico import TelaHistorico
from tkinter import PhotoImage

class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cyborg")
        self.title("Monitor de Bateria v1.0")
        self.geometry("1200x700")

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

        # Backend ESPReader (inicialmente None)
        self.esp_reader = None
        self.simulacao_dados = {}

        # Inicializa todas as telas
        self.frames = {}
        for Tela in (TelaInicial, TelaSelecao, TelaConfiguracao, TelaMonitoramento, TelaCiclos, TelaHistorico):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Mostra TelaInicial
        self.show_frame("TelaInicial")

    def show_frame(self, nome):
        """Mostra a tela indicada pelo nome da classe"""
        frame = self.frames[nome]

        # Se for Monitoramento, atualiza dados
        if nome == "TelaMonitoramento" and hasattr(frame, "atualizar_dados"):
            frame.atualizar_dados(self.simulacao_dados)

        # Atualiza histórico para voltar à TelaInicial
        if nome == "TelaHistorico":
            if hasattr(frame, "btn_voltar"):
                frame.btn_voltar.config(command=lambda: self.show_frame("TelaInicial"))

        frame.tkraise()

    def on_closing(self):
        """Encerra backend e fecha app"""
        # Para ESPReader
        if self.esp_reader is not None:
            try:
                self.esp_reader.parar()
            except Exception:
                pass

        # Para frames que usam after ou matplotlib
        for frame in self.frames.values():
            try:
                # Se o frame tiver animação, parar antes de destruir
                if hasattr(frame, 'ani') and frame.ani.event_source:
                    try:
                        frame.ani.event_source.stop()
                    except Exception:
                        pass
                frame.destroy()
            except Exception:
                pass

        # Destroi a janela principal
        try:
            self.destroy()
        except Exception:
            pass

        # Força saída total do Python
        import os
        os._exit(0)