# ui/selecao.py
import os
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TelaSelecao(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configura grid do frame principal
        self.grid_rowconfigure(0, weight=1)  # linha de cima vazia
        self.grid_rowconfigure(1, weight=0)  # linha do container
        self.grid_rowconfigure(2, weight=1)  # linha de baixo vazia
        self.grid_columnconfigure(0, weight=1)  # coluna esquerda
        self.grid_columnconfigure(1, weight=0)  # coluna container
        self.grid_columnconfigure(2, weight=1)  # coluna direita

        # Frame central (fixo, mas que expande com o conteúdo)
        container = ttk.Frame(self)
        container.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        for i in range(3):
            container.grid_rowconfigure(i, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Título
        titulo = ttk.Label(container, text="🔋 Seleção de Bateria", font=("Segoe UI", 26, "bold"))
        titulo.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Subtítulo
        subtitulo = ttk.Label(container, 
                              text="Escolha uma bateria abaixo para iniciar o monitoramento:",
                              font=("Segoe UI", 15))
        subtitulo.grid(row=1, column=0, pady=(0, 30), sticky="n")

        # Frame dos botões centralizados
        self.baterias_frame = ttk.Frame(container)
        self.baterias_frame.grid(row=2, column=0, sticky="nsew")
        self.baterias_frame.grid_columnconfigure(0, weight=1)

        self._carregar_baterias()

    def _carregar_baterias(self):
        pasta = os.path.join(os.getcwd(), "baterias")

        if not os.path.exists(pasta):
            os.makedirs(pasta)
            ttk.Label(self.baterias_frame, text="Nenhum arquivo de bateria encontrado.").pack()
            return

        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]
        if not arquivos:
            ttk.Label(self.baterias_frame, text="Nenhuma bateria cadastrada.").pack()
            return

        estilos = [INFO, SUCCESS, WARNING, PRIMARY, DANGER]
        max_por_linha = 4

        for widget in self.baterias_frame.winfo_children():
            widget.destroy()

        for i, arquivo in enumerate(arquivos):
            caminho = os.path.join(pasta, arquivo)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")
                continue

            nome = dados.get("nome", "Bateria desconhecida").upper()
            capacidade = dados.get("capacidade", "N/A")
            tensao_carga = dados.get("tensao_carga", "N/A")
            tensao_descarga = dados.get("tensao_descarga", "N/A")

            texto = (
                f"{nome}\n"
                f"Capacidade: {capacidade}\n"
                f"Tensão de Carga: {tensao_carga}\n"
                f"Tensão de Descarga: {tensao_descarga}"
            )

            estilo = estilos[i % len(estilos)]
            botao = ttk.Button(
                self.baterias_frame,
                text=texto,
                bootstyle=estilo,
                padding=20,
                command=lambda d=dados: self._selecionar_bateria(d)
            )

            linha = i // max_por_linha
            coluna = i % max_por_linha
            botao.grid(row=linha, column=coluna, padx=20, pady=20, sticky="nsew")

        # Expansão proporcional dos botões
        for c in range(max_por_linha):
            self.baterias_frame.grid_columnconfigure(c, weight=1)
        for r in range((len(arquivos) + max_por_linha - 1) // max_por_linha):
            self.baterias_frame.grid_rowconfigure(r, weight=1)

    def _selecionar_bateria(self, dados):
        print(f"Selecionado: {dados['nome']}")
        self.controller.show_frame("TelaMonitoramento")
