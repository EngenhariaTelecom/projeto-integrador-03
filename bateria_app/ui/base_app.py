# ui/base_app.py
import ttkbootstrap as tb
from ui.tela_selecao import TelaSelecao
from ui.tela_monitoramento import TelaMonitoramento
from ui.tela_ciclos import TelaCiclos
from ui.tela_historico import TelaHistorico

class BatteryApp(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Monitor de Bateria v1.0")
        self.geometry("1200x700")

        # container principal
        self.container = tb.Frame(self)
        self.container.pack(fill="both", expand=True)

        # páginas
        self.frames = {}
        for Tela in (TelaSelecao, TelaMonitoramento, TelaCiclos, TelaHistorico):
            frame = Tela(parent=self.container, controller=self)
            self.frames[Tela.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("TelaSelecao")

    def show_frame(self, nome):
        frame = self.frames[nome]
        frame.tkraise()
