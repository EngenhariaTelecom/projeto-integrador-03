# ui/tela_historico.py
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from core.historico import Historico

class TelaHistorico(tb.Frame):
    """
    Exibe lista de arquivos CSV e gera gráfico de Tensão vs Tempo
    para o arquivo selecionado.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.historico = Historico()  # Lida com leitura e listagem dos CSVs

        # ==============================
        # Layout principal
        # ==============================
        container = tb.Frame(self)
        container.pack(expand=True, fill="both", padx=10, pady=10)

        conteudo = tb.Frame(container)
        conteudo.place(relx=0.5, rely=0.5, anchor="center")

        # ------------------------------
        # Título
        # ------------------------------
        tb.Label(
            conteudo,
            text="📚 Histórico de Testes",
            font=("Helvetica", 18, "bold")
        ).pack(pady=(0, 15))

        # ------------------------------
        # Parte superior: lista e gráfico
        # ------------------------------
        frame_main = tb.Frame(conteudo)
        frame_main.pack(fill="both", expand=True, pady=(0, 15))

        # Lista de CSVs à esquerda
        frame_lista = tb.Labelframe(frame_main, text="Arquivos CSV", bootstyle=INFO)
        frame_lista.pack(side="left", fill="y", padx=(0, 15))

        self.lista_csv = tk.Listbox(frame_lista, height=15, width=35)
        self.lista_csv.pack(padx=5, pady=5, fill="both", expand=True)
        self.lista_csv.bind("<<ListboxSelect>>", self.on_csv_select)

        tb.Button(
            frame_lista,
            text="🔄 Atualizar Lista",
            bootstyle=SECONDARY,
            command=self.atualizar_lista
        ).pack(padx=5, pady=5, fill="x")

        # Gráfico à direita
        frame_grafico = tb.Labelframe(frame_main, text="Gráfico de Tensão vs Tempo", bootstyle=PRIMARY)
        frame_grafico.pack(side="right", fill="both", expand=True)

        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(7,4))
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Tensão (V)")
        self.ax.set_title("Selecione um arquivo CSV para visualizar")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # ------------------------------
        # Botão Voltar
        # ------------------------------
        tb.Button(
            conteudo,
            text="⏪ Voltar à Tela Inicial",
            bootstyle="secondary-outline",
            command=lambda: controller.show_frame("TelaInicial")
        ).pack(pady=(15,0))

        # ------------------------------
        # Inicialização
        # ------------------------------
        self.atualizar_lista()

    # ==============================
    # Métodos
    # ==============================
    def atualizar_lista(self):
        """Atualiza a lista de arquivos CSV disponíveis."""
        self.lista_csv.delete(0, "end")
        for nome in self.historico.listar_csvs():
            self.lista_csv.insert("end", nome)

    def on_csv_select(self, event):
        """Quando o usuário seleciona um CSV, gera o gráfico correspondente."""
        selecionado = self.lista_csv.curselection()
        if not selecionado:
            return

        nome_arquivo = self.lista_csv.get(selecionado[0])
        tempos, tensoes = self.historico.carregar_dados(nome_arquivo)

        self.ax.clear()
        if tempos and tensoes:
            self.ax.plot(tempos, tensoes, color='tab:green')
            self.ax.set_title(f"Tensão vs Tempo — {nome_arquivo}")
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Tensão (V)")
            self.ax.set_ylim(min(tensoes) * 0.95, max(tensoes) * 1.05)
            self.ax.grid(True)
        else:
            self.ax.set_title(f"Nenhum dado válido em {nome_arquivo}")

        self.canvas.draw()