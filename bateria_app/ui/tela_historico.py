# ui/tela_historico.py
import ttkbootstrap as tb

class TelaHistorico(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tb.Label(self, text="📚 Histórico de Testes", font=("Helvetica", 18, "bold")).pack(pady=20)
        tb.Label(self, text="(Aqui serão exibidos os registros anteriores e opção de exportar CSV)").pack(pady=10)

        tb.Button(self, text="Voltar ao Monitoramento", bootstyle="secondary-outline",
                  command=lambda: controller.show_frame("TelaMonitoramento")).pack(pady=20)
