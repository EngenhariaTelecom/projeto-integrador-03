# ui/tela_configuracao.py
import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import serial.tools.list_ports
from ui.autocomplete import AutocompleteEntry
from core.monitor import ESPReader

class TelaConfiguracao(ttk.Frame):
    def __init__(self, parent, controller, dados_bateria=None):
        super().__init__(parent)
        self.controller = controller
        self.dados_bateria = dados_bateria or {}

        container = ttk.Frame(self)
        container.pack(padx=20, pady=20, fill="both", expand=True)

        ttk.Label(container, text="⚙️ Configuração da Simulação", font=("Segoe UI", 20, "bold")).pack(pady=(0,15))

        # Informações da bateria selecionada
        self.frame_bateria = ttk.Frame(container)
        self.frame_bateria.pack(pady=5)
        self._atualizar_frame_bateria()

        # Porta USB
        self.frame_porta = ttk.Frame(container)
        self.frame_porta.pack(pady=10, fill="x")
        ttk.Label(self.frame_porta, text="Porta USB da ESP:").pack(side="left", padx=(0,5))
        self.porta_var = tk.StringVar()
        self.portas_disponiveis = self._listar_portas_usb()
        self.porta_entry = AutocompleteEntry(
            self.frame_porta,
            autocomplete_list=[p.split(" - ")[0] for p in self.portas_disponiveis],
            placeholder="Selecione ou digite a porta",
            bootstyle="primary",
            textvariable=self.porta_var,
            on_select_callback=self._selecionar_porta
        )
        self.porta_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(self.frame_porta, text="Buscar ESP", bootstyle=PRIMARY, command=self._buscar_esp).pack(side="left", padx=(5,0))
        self.status_label = ttk.Label(container, text="Status: ---")
        self.status_label.pack(pady=(5,0))

        # Nome do arquivo CSV
        self.frame_csv = ttk.Frame(container)
        self.frame_csv.pack(pady=10, fill="x")
        ttk.Label(self.frame_csv, text="Nome do arquivo CSV:").pack(side="left", padx=(0,5))
        self.csv_var = tk.StringVar()
        ttk.Entry(self.frame_csv, textvariable=self.csv_var, width=30).pack(side="left", fill="x", expand=True)
        ttk.Label(self.frame_csv, text=".csv será adicionado automaticamente").pack(side="left", padx=(5,0))

        # Tipo de teste
        self.frame_tipo = ttk.Frame(container)
        self.frame_tipo.pack(pady=10, fill="x")
        ttk.Label(self.frame_tipo, text="Tipo de teste:").pack(side="left", padx=(0,5))
        self.tipo_var = tk.StringVar(value="carga")
        ttk.Radiobutton(self.frame_tipo, text="Carga/Descarga", variable=self.tipo_var, value="carga", command=self._toggle_ciclos).pack(side="left", padx=5)
        ttk.Radiobutton(self.frame_tipo, text="Ciclos múltiplos", variable=self.tipo_var, value="ciclos", command=self._toggle_ciclos).pack(side="left", padx=5)
        self.ciclos_label = ttk.Label(self.frame_tipo, text="Qtd ciclos:")
        self.ciclos_entry = ttk.Entry(self.frame_tipo, width=5)
        self.ciclos_var = tk.StringVar(value="1")
        self._toggle_ciclos()

        # Botões de navegação
        self.frame_botoes = ttk.Frame(container)
        self.frame_botoes.pack(pady=20)
        ttk.Button(self.frame_botoes, text="Voltar", bootstyle=WARNING, command=lambda: controller.show_frame("TelaInicial")).pack(side="left", padx=5)
        ttk.Button(self.frame_botoes, text="Iniciar Simulação", bootstyle=SUCCESS, command=self._iniciar_simulacao).pack(side="left", padx=5)

        # Inicializa ESP como None
        self.esp_reader = None

    def _atualizar_frame_bateria(self):
        for widget in self.frame_bateria.winfo_children():
            widget.destroy()
        ttk.Label(self.frame_bateria, text=f"Bateria selecionada: {self.dados_bateria.get('nome','')}").pack()
        ttk.Label(self.frame_bateria, text=f"Capacidade: {self.dados_bateria.get('capacidade','')}").pack()
        ttk.Label(self.frame_bateria, text=f"Tensão de Carga: {self.dados_bateria.get('tensao_carga','')}").pack()
        ttk.Label(self.frame_bateria, text=f"Tensão de Descarga: {self.dados_bateria.get('tensao_descarga','')}").pack()

    def atualizar_dados_bateria(self, dados):
        self.dados_bateria = dados
        self._atualizar_frame_bateria()

    def _listar_portas_usb(self):
        portas = []
        for p in serial.tools.list_ports.comports():
            portas.append(f"{p.device} - {p.description}")
        return portas if portas else []

    def _selecionar_porta(self, porta):
        self.porta_var.set(porta)
        self.status_label.config(text=f"Status: Porta selecionada ({porta})")

    def _toggle_ciclos(self):
        if self.tipo_var.get() == "ciclos":
            self.ciclos_label.pack(side="left", padx=(10,0))
            self.ciclos_entry.pack(side="left")
            self.ciclos_entry.config(textvariable=self.ciclos_var)
        else:
            self.ciclos_label.pack_forget()
            self.ciclos_entry.pack_forget()

    def _buscar_esp(self):
        self.status_label.config(text="Status: Buscando ESP...")
        threading.Thread(target=self._thread_busca_esp, daemon=True).start()

    def _thread_busca_esp(self):
        try:
            esp = ESPReader()
            esp.conectar()
            if esp.running:
                self.esp_reader = esp
                self.porta_var.set(esp.porta)
                self.status_label.config(text=f"Status: ESP encontrada na porta {esp.porta}")
            else:
                self.status_label.config(text="Status: Nenhuma ESP encontrada")
        except Exception as e:
            self.status_label.config(text=f"Erro: {e}")

    def _iniciar_simulacao(self):
        porta = self.porta_var.get().strip()
        nome_arquivo = self.csv_var.get().strip()
        tipo = self.tipo_var.get()
        ciclos = int(self.ciclos_var.get()) if self.ciclos_var.get().isdigit() else 1

        if not porta:
            messagebox.showwarning("Erro", "Selecione uma porta USB.")
            return
        if not nome_arquivo:
            messagebox.showwarning("Erro", "Informe o nome do arquivo CSV.")
            return

        # Cria diretório assets/dados se não existir
        pasta_dados = os.path.join(os.getcwd(), "assets", "dados")
        if not os.path.exists(pasta_dados):
            os.makedirs(pasta_dados)

        # Caminho completo do CSV
        csv_file = os.path.join(pasta_dados, f"{nome_arquivo}.csv")

        # Salva dados no controller
        self.controller.simulacao_dados = {
            "porta": porta,
            "csv": csv_file,
            "tipo": tipo,
            "ciclos": ciclos,
            "dados_bateria": self.dados_bateria
        }

        # Inicia ESPReader
        try:
            self.controller.esp_reader = ESPReader(porta)
            self.controller.esp_reader.start()
        except Exception as e:
            print("Erro iniciando ESPReader:", e)

        # Vai para TelaMonitoramento
        self.controller.show_frame("TelaMonitoramento")