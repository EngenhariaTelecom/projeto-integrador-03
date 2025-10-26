# ui/base_app.py
import ttkbootstrap as tb
from core.monitor import ESPReader
from ui.tela_selecao import TelaSelecao
from ui.tela_monitoramento import TelaMonitoramento
from ui.tela_ciclos import TelaCiclos
from ui.tela_historico import TelaHistorico

class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Monitor de Bateria v1.0")
        self.geometry("1200x700")

        # ALTERAR ICONE para multiplataforma usando .png
        import os
        from tkinter import PhotoImage
        caminho_icone = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "icon.png")
        caminho_icone = os.path.abspath(caminho_icone)
        try:
            icon_image = PhotoImage(file=caminho_icone)
            self.iconphoto(False, icon_image)
        except Exception as e:
            print(f"Não foi possível carregar o ícone: {e}")

        # container principal
        self.container = tb.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        # Faz a janela expandir o container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Faz o container expandir os frames
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)


        # --------------------------
        # Backend: ESPReader
        # --------------------------
        self.esp_reader = ESPReader() 
        self.esp_reader.start()  # inicia thread de leitura

        # páginas
        self.frames = {}
        for Tela in (TelaSelecao, TelaMonitoramento, TelaCiclos, TelaHistorico):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            # Garante que widgets internos do frame se expandam
            if hasattr(frame, 'grid_rowconfigure'):
                frame.grid_rowconfigure(0, weight=1)
            if hasattr(frame, 'grid_columnconfigure'):
                frame.grid_columnconfigure(0, weight=1)

        self.show_frame("TelaSelecao")

    def show_frame(self, nome):
        """Mostra a tela indicada pelo nome da classe"""
        frame = self.frames[nome]
        frame.tkraise()
        
    def on_closing(self):
        """Encerra o backend e fecha a janela"""
        if hasattr(self, 'esp_reader'):
            self.esp_reader.parar()  # função que fecha a serial e thread do backend
        self.destroy()