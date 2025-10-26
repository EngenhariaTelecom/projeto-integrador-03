# ui/tela_selecao.py
import os
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.autocomplete import AutocompleteEntry

class TelaSelecao(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        # Container central
        container = ttk.Frame(self)
        container.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Título
        titulo = ttk.Label(container, text="🔋 Seleção de Bateria", font=("Segoe UI", 26, "bold"))
        titulo.grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Subtítulo
        subtitulo = ttk.Label(container, text="Digite ou selecione uma bateria:", font=("Segoe UI", 15))
        subtitulo.grid(row=1, column=0, pady=(0, 20), sticky="n")

        # Frame de seleção
        self.selecao_frame = ttk.Frame(container)
        self.selecao_frame.grid(row=2, column=0, sticky="nsew")
        self.selecao_frame.grid_columnconfigure(0, weight=1)

        # Campos e StringVars
        self.campos = {}
        self.campos_var = {}

        # Carrega baterias
        self._carregar_baterias()

        # Campos da bateria (capacidade, tensao_carga, tensao_descarga)
        campos_info = [
            ("capacidade", "Capacidade (Ah)"),
            ("tensao_carga", "Tensão de Carga (V)"),
            ("tensao_descarga", "Tensão de Descarga (V)")
        ]

        for key, label_text in campos_info:
            frame = ttk.Frame(self.selecao_frame)
            frame.pack(fill="x", pady=5)

            label = ttk.Label(frame, text=label_text, width=20)
            label.pack(side="left")

            var = tk.StringVar()
            entry = ttk.Entry(frame, font=("Segoe UI", 12), textvariable=var)
            entry.pack(side="left", fill="x", expand=True)

            entry.config(state="disabled")  # Inicialmente desativado
            var.trace_add("write", lambda *a: self._verificar_valores())

            self.campos[key] = entry
            self.campos_var[key] = var

            # Botão iniciar monitoramento
        self.botao_confirmar = ttk.Button(
            self.selecao_frame,
            text="Iniciar Monitoramento",
            bootstyle=SUCCESS,
            padding=10,
            state="disabled",
            command=self._confirmar_selecao
        )
        self.botao_confirmar.pack(pady=20)

    def _carregar_baterias(self):
        pasta = os.path.join(os.getcwd(), "baterias")
        if not os.path.exists(pasta):
            os.makedirs(pasta)

        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]

        self.baterias_dados = []
        display_list = []
        self.display_map = {}

        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.baterias_dados.append(dados)
                    nome = dados.get("nome", "Desconhecida").upper()
                    display_list.append(nome)
                    self.display_map[nome] = dados
            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")

        display_list.append("Outro")  # Sempre adiciona a opção "Outro"

        # Autocomplete (colocado ANTES dos campos, para ficar acima)
        self.entry_bateria = AutocompleteEntry(
            self.selecao_frame,
            autocomplete_list=display_list,
            placeholder="Digite ou selecione a bateria",
            bootstyle="primary",
            font=("Segoe UI", 14),
            on_select_callback=self._atualizar_campos
        )
        self.entry_bateria.pack(pady=(0, 20), fill="x")

    def _atualizar_campos(self, texto_selecionado):
        """Atualiza os campos de acordo com a seleção."""
        outro = texto_selecionado.lower() == "outro"

        if outro:
            for key in ["capacidade", "tensao_carga", "tensao_descarga"]:
                entry = self.campos[key]
                var = self.campos_var[key]
                entry.config(state="normal")
                var.set("")
                entry.config(validate="key", validatecommand=(self.register(self._validar_numero), "%P"))
        else:
            dados = self.display_map.get(texto_selecionado, {})
            for key in ["capacidade", "tensao_carga", "tensao_descarga"]:
                entry = self.campos[key]
                var = self.campos_var[key]
                var.set(str(dados.get(key, "")))
                entry.config(state="disabled")
                entry.config(validate="none")

        self._verificar_valores()

    def _validar_numero(self, P):
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def _verificar_valores(self):
        texto_selecionado = self.entry_bateria.get().strip()
        if not texto_selecionado:
            self.botao_confirmar.config(state="disabled")
            return

        outro = texto_selecionado.lower() == "outro"
        existe = texto_selecionado in self.display_map

        if outro:
            try:
                capacidade = self.campos_var["capacidade"].get().strip()
                tensao_carga = self.campos_var["tensao_carga"].get().strip()
                tensao_descarga = self.campos_var["tensao_descarga"].get().strip()

                if not capacidade or not tensao_carga or not tensao_descarga:
                    self.botao_confirmar.config(state="disabled")
                    return

                tensao_carga_val = float(''.join(c for c in tensao_carga if c.isdigit() or c=='.'))
                tensao_descarga_val = float(''.join(c for c in tensao_descarga if c.isdigit() or c=='.'))

                if tensao_carga_val <= tensao_descarga_val:
                    self.botao_confirmar.config(state="disabled")
                    return

                self.botao_confirmar.config(state="normal")
            except Exception:
                self.botao_confirmar.config(state="disabled")
        elif existe:
            self.botao_confirmar.config(state="normal")
        else:
            self.botao_confirmar.config(state="disabled")

    def _confirmar_selecao(self):
        self.dados_bateria = {key: var.get() for key, var in self.campos_var.items()}
        print(f"Selecionado: {self.dados_bateria}")
        self.controller.show_frame("TelaMonitoramento")
