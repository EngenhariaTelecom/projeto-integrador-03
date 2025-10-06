import ttkbootstrap as tb

class TelaCiclos(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Centraliza tudo visualmente no meio da tela
        conteudo = tb.Frame(self)
        conteudo.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(conteudo, text="🔄 Teste de Ciclos", font=("Helvetica", 18, "bold")).pack(pady=20)
        tb.Label(conteudo, text="(Aqui serão configurados e executados os ciclos de carga/descarga)").pack(pady=10)
        tb.Button(conteudo, text="Voltar ao Monitoramento", bootstyle="secondary-outline",
                  command=lambda: controller.show_frame("TelaMonitoramento")).pack(pady=20)
