# ui/tela_selecao.py
import os
import json
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.autocomplete import AutocompleteEntry
from ui.tela_configuracao import TelaConfiguracao

class TelaSelecao(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.dados_bateria = {}

        # Container central
        container = ttk.Frame(self)
        container.pack(pady=20, padx=20)

        # Título
        ttk.Label(container, text="⚡ Seleção de Bateria", font=("Segoe UI", 24, "bold")).pack(pady=(0,20))
        ttk.Label(container, text="Digite ou selecione uma bateria:", font=("Segoe UI", 14)).pack(pady=(0,20))

        # Carrega baterias
        self.baterias_list = []
        self.baterias_map = {}
        self._carregar_baterias()

        # Autocomplete
        self.entry_bateria = AutocompleteEntry(
            container,
            autocomplete_list=self.baterias_list,
            placeholder="Digite ou selecione a bateria",
            bootstyle="primary",
            font=("Segoe UI", 12),
            on_select_callback=self._atualizar_campos
        )
        self.entry_bateria.pack(pady=(0,20))

        # Campos de informação
        self.campos_var = {}
        self.campos = {}
        campos_info = [
            ("capacidade", "Capacidade (mAh)"),
            ("tensao_carga", "Tensão de Carga (V)"),
            ("tensao_descarga", "Tensão de Descarga (V)")
        ]
        self.frame_campos = ttk.Frame(container)
        self.frame_campos.pack()
        for key, label_text in campos_info:
            frame = ttk.Frame(self.frame_campos)
            frame.pack(pady=5)
            ttk.Label(frame, text=label_text, width=20).pack(side="left")
            var = tk.StringVar()
            entry = ttk.Entry(frame, font=("Segoe UI", 12), width=15, textvariable=var)
            entry.pack(side="left")
            entry.config(state="disabled")
            var.trace_add("write", lambda *a: self._verificar_valores())
            self.campos_var[key] = var
            self.campos[key] = entry

        # Botão continuar
        self.botao_continuar = ttk.Button(
            container,
            text="Continuar",
            bootstyle=SUCCESS,
            padding=10,
            state="disabled",
            command=self._continuar
        )
        self.botao_continuar.pack(pady=(10,0))

    def _carregar_baterias(self):
        pasta = os.path.join(os.getcwd(), "baterias")
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        arquivos = [f for f in os.listdir(pasta) if f.endswith(".json")]

        self.baterias_list = []
        self.baterias_map = {}
        for arq in arquivos:
            caminho = os.path.join(pasta, arq)
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    nome = dados.get("nome", "Desconhecida")
                    self.baterias_list.append(nome)
                    self.baterias_map[nome] = dados
            except:
                continue
        self.baterias_list.append("Outro")  # Sempre adiciona a opção Outro

    def _atualizar_campos(self, texto_selecionado):
        outro = texto_selecionado.lower() == "outro"
        if outro:
            for key in self.campos:
                self.campos[key].config(state="normal")
                self.campos_var[key].set("")
        else:
            dados = self.baterias_map.get(texto_selecionado, {})
            for key in self.campos:
                self.campos_var[key].set(str(dados.get(key, "")))
                self.campos[key].config(state="disabled")
        self._verificar_valores()

    def _verificar_valores(self):
        texto = self.entry_bateria.get().strip()
        if not texto:
            self.botao_continuar.config(state="disabled")
            return
        if texto.lower() == "outro":
            try:
                cap = self.campos_var["capacidade"].get()
                tc = self.campos_var["tensao_carga"].get()
                td = self.campos_var["tensao_descarga"].get()
                if not cap or not tc or not td:
                    self.botao_continuar.config(state="disabled")
                    return
                if float(tc) <= float(td):
                    self.botao_continuar.config(state="disabled")
                    return
                self.botao_continuar.config(state="normal")
            except:
                self.botao_continuar.config(state="disabled")
        else:
            if texto in self.baterias_map:
                self.botao_continuar.config(state="normal")
            else:
                self.botao_continuar.config(state="disabled")

    def _continuar(self):
        nome = self.entry_bateria.get().strip()
        if nome.lower() == "outro":
            self.dados_bateria = {
                "nome": "Outro",
                "capacidade": self.campos_var["capacidade"].get(),
                "tensao_carga": self.campos_var["tensao_carga"].get(),
                "tensao_descarga": self.campos_var["tensao_descarga"].get()
            }
        else:
            self.dados_bateria = self.baterias_map.get(nome, {})

        # Integração com TelaConfiguracao
        config_frame = self.controller.frames.get("TelaConfiguracao")
        if config_frame is None:
            config_frame = TelaConfiguracao(
                parent=self.controller.container,
                controller=self.controller,
                dados_bateria=self.dados_bateria
            )
            self.controller.frames["TelaConfiguracao"] = config_frame
            config_frame.grid(row=0, column=0, sticky="nsew")
        else:
            if hasattr(config_frame, "atualizar_dados_bateria"):
                config_frame.atualizar_dados_bateria(self.dados_bateria)

        self.controller.show_frame("TelaConfiguracao")