# ui/tela_ciclos.py
import ttkbootstrap as tb

class TelaCiclos(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tb.Label(self, text="🔄 Teste de Ciclos", font=("Helvetica", 18, "bold")).pack(pady=20)
        tb.Label(self, text="(Aqui serão configurados e executados os ciclos de carga/descarga)").pack(pady=10)

        tb.Button(self, text="Voltar ao Monitoramento", bootstyle="secondary-outline",
                  command=lambda: controller.show_frame("TelaMonitoramento")).pack(pady=20)
