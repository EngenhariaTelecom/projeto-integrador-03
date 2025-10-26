# ui/tela_historico.py
import ttkbootstrap as tb

class TelaHistorico(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Container central que ocupa todo o frame
        container = tb.Frame(self)
        container.pack(expand=True, fill="both")  # garante expansão total

        # Subcontainer para centralizar conteúdo
        conteudo = tb.Frame(container)
        conteudo.place(relx=0.5, rely=0.5, anchor="center")  # centraliza no meio

        # Título
        tb.Label(
            conteudo,
            text="📚 Histórico de Testes",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(0,20))

        # Subtítulo / descrição
        tb.Label(
            conteudo,
            text="(Aqui serão exibidos os registros anteriores e opção de exportar CSV)"
        ).pack(pady=(0,20))

        # Botão voltar para TelaInicial
        tb.Button(
            conteudo,
            text="Voltar à Tela Inicial",
            bootstyle="secondary-outline",
            command=lambda: controller.show_frame("TelaInicial")
        ).pack(pady=(10,0))