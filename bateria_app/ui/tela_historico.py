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
        if not tempos or not tensoes:
            # sem dados válidos — informa e atualiza o canvas
            self.ax.set_title(f"Nenhum dado válido em {nome_arquivo}")
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Tensão (V)")
            self.ax.grid(True)
            self.canvas.draw()
            return

        # Ordena por tempo caso o CSV não esteja em ordem (segurança)
        try:
            paired = sorted(zip(tempos, tensoes), key=lambda p: p[0])
            tempos, tensoes = zip(*paired)
        except Exception:
            # se algo falhar, segue com os dados originais
            pass

        # Converte para listas (podem ser tuplas após zip)
        tempos = list(tempos)
        tensoes = list(tensoes)

        # Plota normalmente
        self.ax.plot(tempos, tensoes, color='tab:green')
        self.ax.set_title(f"Tensão vs Tempo — {nome_arquivo}")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Tensão (V)")
        # Ajusta limites do eixo Y de forma segura:
        try:
            vmin = min(tensoes)
            vmax = max(tensoes)
            if vmin == vmax:
                # único valor: dá um range pequeno em torno dele
                delta = abs(vmin) * 0.02 if abs(vmin) > 0 else 0.02
                self.ax.set_ylim(vmin - delta, vmax + delta)
            else:
                self.ax.set_ylim(vmin * 0.95, vmax * 1.05)
        except Exception:
            # fallback simples
            pass

        # Não força xlim iniciar em 0 — aceita que o primeiro tempo seja >0
        self.ax.grid(True)
        self.canvas.draw()