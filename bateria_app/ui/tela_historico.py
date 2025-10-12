# ui/tela_historico.py
import ttkbootstrap as tb

class TelaHistorico(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        conteudo = tb.Frame(self)
        conteudo.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        conteudo.grid_rowconfigure(0, weight=1)
        conteudo.grid_columnconfigure(0, weight=1)

        label1 = tb.Label(conteudo, text="📚 Histórico de Testes", font=("Helvetica", 18, "bold"))
        label1.grid(row=0, column=0, pady=20, sticky="nsew")
        label2 = tb.Label(conteudo, text="(Aqui serão exibidos os registros anteriores e opção de exportar CSV)")
        label2.grid(row=1, column=0, pady=10, sticky="nsew")
        btn = tb.Button(conteudo, text="Voltar ao Monitoramento", bootstyle="secondary-outline",
              command=lambda: controller.show_frame("TelaMonitoramento"))
        btn.grid(row=2, column=0, pady=20, sticky="nsew")

