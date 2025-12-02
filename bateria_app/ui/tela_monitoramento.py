# ui/tela_monitoramento.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from collections import deque
import time
import os
import json
from tkinter import messagebox

class TelaMonitoramento(tb.Frame):
    """
    Tela de monitoramento da bateria.
    Exibe tensão e corrente em tempo real e salva dados via ESPReader.
    Implementa finalização automática para carga/descarga e para ciclos.
    """
    LOG_FILE = os.path.join(os.getcwd(), "assets", "dados", "simulacao_log.json")

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.modo_ciclos = False
        self.tempo_inicial = time.time()

        # Dados para gráfico (tensão apenas)
        self.MAX_PONTOS = 10000
        self.dados_tempo = deque(maxlen=self.MAX_PONTOS)
        self.dados_tensao = deque(maxlen=self.MAX_PONTOS)

        # Controle de ciclos
        self.ciclos_totais = 0
        self.ciclo_atual = 0
        self._prev_carga_state = None  # para detectar transições de carga/descarga

        # Layout
        conteudo = tb.Frame(self)
        conteudo.pack(padx=10, pady=10, fill="both", expand=True)

        # Topo info
        frame_info = tb.Frame(conteudo)
        frame_info.pack(fill="x", pady=(0,5))

        self.bateria_label = tb.Label(frame_info, text="Bateria: ---")
        self.capacidade_label = tb.Label(frame_info, text="Capacidade: ---")
        self.tipo_label = tb.Label(frame_info, text="Tipo: ---")
        self.porta_label = tb.Label(frame_info, text="Porta: ---")
        self.csv_label = tb.Label(frame_info, text="CSV: ---")
        self.ciclo_label = tb.Label(frame_info, text="Ciclo: 0/0")  # Nova label

        for i, lbl in enumerate([
            self.bateria_label, self.capacidade_label, self.tipo_label,
            self.porta_label, self.csv_label, self.ciclo_label
        ]):
            lbl.grid(row=0, column=i, padx=12)
            frame_info.grid_columnconfigure(i, weight=1)

        # Tensão e Corrente (lado a lado)
        frame_medidas = tb.Frame(conteudo)
        frame_medidas.pack(fill="x", pady=(10,10))

        self.tensao_label = tb.Label(
            frame_medidas,
            text="Tensão: -- V",
            font=("Segoe UI", 22, "bold"),
            foreground="#4CAF50"
        )
        self.tensao_label.grid(row=0, column=0, padx=40, pady=5, sticky="e")

        self.corrente_label = tb.Label(
            frame_medidas,
            text="Corrente: -- A",
            font=("Segoe UI", 18, "bold"),
            foreground="#2196F3"
        )
        self.corrente_label.grid(row=0, column=1, padx=40, pady=5, sticky="w")

        self.tempo_execucao_label = tb.Label(
            frame_medidas,
            text="Tempo: 0s",
            font=("Segoe UI", 18, "bold"),
            foreground="#FFC107"
        )
        self.tempo_execucao_label.grid(row=0, column=2, padx=40, pady=5, sticky="w")

        self.descanso_label = tb.Label(
            frame_medidas,
            text="Descanso: --",
            font=("Segoe UI", 18, "bold"),
            foreground="#FF5722"
        )
        self.descanso_label.grid(row=0, column=3, padx=40, pady=5, sticky="w")

        frame_medidas.grid_columnconfigure(0, weight=1)
        frame_medidas.grid_columnconfigure(1, weight=1)
        frame_medidas.grid_columnconfigure(2, weight=1)
        frame_medidas.grid_columnconfigure(3, weight=1)

        self.ciclo_label.grid_remove()
        self.descanso_label.grid_remove()


        # Modo / Carga / Descarga
        frame_status = tb.Frame(conteudo)
        frame_status.pack(fill="x", pady=(0,10))

        self.modo_label = tb.Label(frame_status, text="Modo: --")
        self.carga_label = tb.Label(frame_status, text="Carga: --")
        self.descarga_label = tb.Label(frame_status, text="Descarga: --")

        self.modo_label.grid(row=0, column=0, padx=10)
        self.carga_label.grid(row=0, column=1, padx=10)
        self.descarga_label.grid(row=0, column=2, padx=10)
        frame_status.grid_columnconfigure((0,1,2), weight=1)

        # Gráfico de tensão
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(8,3))
        self.line, = self.ax.plot([], [], color='tab:green')
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Tensão (V)")
        self.ax.set_title("Tensão da Bateria em Tempo Real")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=conteudo)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(0,10))

        # Botões
        frame_botoes = tb.Frame(conteudo)
        frame_botoes.pack(pady=(10,0))

        self.btn_carga = tb.Button(frame_botoes, text="▶️ Iniciar Carga", bootstyle=SUCCESS, command=self.iniciar_carga)
        self.btn_carga.grid(row=0, column=0, padx=5)
        self.btn_descarga = tb.Button(frame_botoes, text="⚡ Iniciar Descarga", bootstyle=INFO, command=self.iniciar_descarga)
        self.btn_descarga.grid(row=0, column=1, padx=5)
        self.btn_desativar = tb.Button(frame_botoes, text="⏹ Desativar Tudo", bootstyle=WARNING, command=self.desativar_tudo)
        self.btn_desativar.grid(row=0, column=2, padx=5)

        # Voltar
        frame_voltar = tb.Frame(conteudo)
        frame_voltar.pack(pady=(15,5))
        tb.Button(
            frame_voltar,
            text="← Voltar à Tela Inicial",
            bootstyle="secondary-outline",
            width=25,
            command=lambda: self.voltar_tela_inicial()
        ).pack()

        # Animação do gráfico
        self.ani = FuncAnimation(self.fig, self.atualizar_grafico, interval=1000, cache_frame_data=False)
        self.after_id = None
        self._usb_on_job = None

        # Inicia labels
        self.atualizar_labels()

    # =========================
    # Inicialização/retomada
    # =========================
    def atualizar_dados(self, dados, retomar=False):
        self.controller.simulacao_dados = dados or {}
        esp = getattr(self.controller, "esp_reader", None)

        if esp and "csv" in (dados or {}):
            try:
                esp.definir_csv(dados["csv"])
            except Exception:
                pass

        self.ciclos_totais = int((dados or {}).get("ciclos", 0))

        if not retomar:
            self.dados_tempo.clear()
            self.dados_tensao.clear()
            self.tempo_inicial = time.time()
            self.descanso_em_andamento = False
            self.tempo_restante_descanso = 0
            self.ax.clear()
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Tensão (V)")
            self.ax.set_title("Tensão da Bateria em Tempo Real")
            self.ax.grid(True)
            self.canvas.draw()
            self.ciclo_atual = 0
            self._prev_carga_state = None
            self.controller.simulacao_dados["ciclo_atual"] = self.ciclo_atual
            self._criar_log()
        else:
            self.ciclo_atual = int((self.controller.simulacao_dados.get("ciclo_atual", 0)) or 0)

        # --------------------------------------------------
        # MODO: CICLOS vs MANUAL
        # --------------------------------------------------
        tipo = (dados or {}).get("tipo", "")
        if tipo.lower() == "ciclos":
            self.modo_ciclos = True

            # ESP em modo AUTO
            if esp:
                esp.modo = "AUTO"
                try:
                    if hasattr(esp, "bateria_controller"):
                        esp.bateria_controller.alternar_modo()
                except Exception:
                    pass

            # Oculta botões de manual
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid_remove()

            # Mostra elementos de ciclos
            try: self.ciclo_label.grid()           # MOSTRA
            except: pass
            try: self.descanso_label.grid()        # MOSTRA
            except: pass

            # Tempo de execução SEMPRE aparece, então não mexemos nele

        else:
            self.modo_ciclos = False

            # ESP em modo MANUAL
            if esp:
                esp.modo = "MANUAL"

            # Reexibe botões
            for btn in [self.btn_carga, self.btn_descarga, self.btn_desativar]:
                btn.grid()

            # Esconde ciclo e descanso
            try: self.ciclo_label.grid_remove()
            except: pass
            try: self.descanso_label.grid_remove()
            except: pass

            # ⚠️ Tempo continua visível -> NÃO remover!

        # --------------------------------------------------
        # INICIAR ENVIO PERIÓDICO USB ON
        # --------------------------------------------------
        if esp:
            try:
                esp.iniciar_envio_periodico("USB ON", intervalo=3)
                print("[MONITORAMENTO] Envio periódico iniciado.")
            except Exception as e:
                print(f"[MONITORAMENTO] Falha ao iniciar envio periódico: {e}")

    # =========================
    # Log
    # =========================
    def _criar_log(self):
        try:
            os.makedirs(os.path.dirname(self.LOG_FILE), exist_ok=True)
            log_info = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "bateria": self.controller.simulacao_dados.get("dados_bateria", {}).get("nome", "---"),
                "serial": self.controller.simulacao_dados.get("porta", "---"),
                "arquivo_csv": self.controller.simulacao_dados.get("csv", "---"),
                "modo": self.controller.simulacao_dados.get("tipo", "---"),
                "ciclos_totais": self.ciclos_totais,
                "ciclo_atual": int(self.ciclo_atual)
            }
            with open(self.LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(log_info, f, indent=2, ensure_ascii=False)
            print(f"[LOG] Arquivo de log criado/atualizado: {self.LOG_FILE}")
        except Exception as e:
            print(f"[LOG] Erro ao criar/atualizar log: {e}")

    def _apagar_log(self):
        if os.path.exists(self.LOG_FILE):
            os.remove(self.LOG_FILE)

    # =========================
    # Botões / ações
    # =========================
    def iniciar_carga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.carga = "ON"
            esp.descarga = "OFF"
            esp.modo = "MANUAL"
            try:
                esp.bateria_controller.iniciar_carga()
            except Exception:
                pass

    def iniciar_descarga(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            esp.descarga = "ON"
            esp.carga = "OFF"
            esp.modo = "MANUAL"
            try:
                esp.bateria_controller.iniciar_descarga()
            except Exception:
                pass

    def desativar_tudo(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            try:
                esp.bateria_controller.desligar_tudo()
            except Exception:
                pass

    # =========================
    # Voltar / Encerrar
    # =========================
    def voltar_tela_inicial(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            try:
                esp.bateria_controller.desligar_tudo()
            except Exception: pass
            try:
                esp.parar_envio_periodico()
            except Exception:
                pass


        if os.path.exists(self.LOG_FILE):
            resposta = messagebox.askyesno(
                "Interromper Simulação",
                "Deseja interromper a leitura de dados e apagar o log?"
            )
            if resposta:
                if esp:
                    try:
                        esp.parar()
                    except Exception:
                        pass
                self._apagar_log()
                self.controller.simulacao_dados = {}
                self.controller.show_frame("TelaInicial")
        else:
            self.controller.show_frame("TelaInicial")

    # =========================
    # Atualização labels (1s)
    # =========================
    def atualizar_labels(self):
        if not self.winfo_exists():
            return
        try:
            esp = getattr(self.controller, "esp_reader", None)
            dados = getattr(self.controller, "simulacao_dados", {})

            if "csv" in dados:
                rel_csv = os.path.relpath(dados["csv"], os.getcwd())
                self.csv_label.config(text=f"CSV: {rel_csv}")
            bateria = dados.get("dados_bateria", {})
            self.bateria_label.config(text=f"Bateria: {bateria.get('nome','---')}")
            self.capacidade_label.config(text=f"Capacidade: {bateria.get('capacidade','---')}")
            self.porta_label.config(text=f"Porta: {dados.get('porta','---')}")
            tipo = dados.get("tipo","---")
            self.tipo_label.config(text=f"Tipo: {tipo}")
            self.ciclo_label.config(text=f"Ciclo: {self.ciclo_atual}/{self.ciclos_totais}")

            if esp:
                try:
                    self.tensao_label.config(
                        text=f"Tensão: {esp.ultima_tensao:.3f} V" if esp.ultima_tensao is not None else "Tensão: -- V"
                    )
                except Exception:
                    self.tensao_label.config(text="Tensão: -- V")
                try:
                    self.corrente_label.config(
                        text=f"Corrente: {esp.corrente:.3f} A" if esp.corrente is not None else "Corrente: -- A"
                    )
                except Exception:
                    self.corrente_label.config(text="Corrente: -- A")
                self.modo_label.config(text=f"Modo: {esp.modo}")
                self.carga_label.config(text=f"Carga: {esp.carga}")
                self.descarga_label.config(text=f"Descarga: {esp.descarga}")

                # Atualiza tempo total de execução
                tempo_total = int(time.time() - self.tempo_inicial)
                self.tempo_execucao_label.config(text=f"Tempo: {tempo_total}s")

                # Se estiver descansando, mostrar contador regressivo
                if self.descanso_em_andamento:
                    self.descanso_label.config(text=f"Descanso: {int(self.tempo_restante_descanso)}s")
                else:
                    self.descanso_label.config(text="Descanso: --")

            if self.winfo_exists():
                self.after_id = self.after(1000, self.atualizar_labels)
        except Exception:
            pass

    # =========================
    # Atualização do gráfico e checagem de término
    # =========================
    def atualizar_grafico(self, frame):
        esp = getattr(self.controller, "esp_reader", None)
        if not esp or esp.ultima_tensao is None:
            return

        try:
            # Atualiza buffers
            t = time.time() - self.tempo_inicial
            self.dados_tempo.append(t)
            self.dados_tensao.append(esp.ultima_tensao)

            # Redesenha gráfico
            self.ax.clear()
            self.ax.plot(self.dados_tempo, self.dados_tensao, color='tab:green')
            self.ax.set_xlabel("Tempo (s)")
            self.ax.set_ylabel("Tensão (V)")
            self.ax.set_title("Tensão da Bateria em Tempo Real")
            self.ax.grid(True)
            self.canvas.draw()

            # Salva CSV se aplicável
            try:
                if hasattr(esp, "salvar_csv") and esp.arquivo_csv:
                    esp.salvar_csv(esp.ultima_tensao, esp.corrente)
            except Exception as e:
                print(f"[MONITORAMENTO] Erro ao salvar CSV via ESPReader: {e}")

            # Dados para análise de encerramento
            dados_bat = self.controller.simulacao_dados.get("dados_bateria", {}) or {}
            tipo_teste = (self.controller.simulacao_dados.get("tipo", "") or "").lower().strip()

            # Converte tensões com segurança
            try:
                tensao_carga = float(str(dados_bat.get("tensao_carga", "")).replace(",", ".") or 0)
            except Exception:
                print(f"[MONITORAMENTO] Tensão de carga inválida)")
                tensao_carga = 0.0
            try:
                tensao_descarga = float(str(dados_bat.get("tensao_descarga", "")).replace(",", ".") or 0)
            except Exception:
                print(f"[MONITORAMENTO] Tensão de descarga inválida)")
                tensao_descarga = 0.0

            tolerancia = 0.01  # 10 mV de margem

            def finalizar_teste(mensagem="Teste finalizado"):
                ############################################
                # 1) DESLIGAR TUDO IMEDIATAMENTE
                ############################################
                try:
                    esp.bateria_controller.desligar_tudo()
                except Exception:
                    pass

                # Para envio periódico ("USB ON")
                try:
                    esp.parar_envio_periodico()
                except Exception:
                    pass

                # Para a thread da serial e fecha conexão
                try:
                    esp.parar()
                except Exception:
                    pass


                ############################################
                # 2) APAGAR LOG E LIMPAR SIMULAÇÃO
                ############################################
                try:
                    self._apagar_log()
                except:
                    pass

                self.controller.simulacao_dados = {}


                ############################################
                # 3) PARAR ANIMAÇÃO DO GRÁFICO
                ############################################
                try:
                    if hasattr(self, "ani") and self.ani.event_source:
                        self.ani.event_source.stop()
                except Exception:
                    pass


                ############################################
                # 4) PARAR CALLBACKS after()
                ############################################
                try:
                    if hasattr(self, "after_id") and self.after_id:
                        self.after_cancel(self.after_id)
                        self.after_id = None
                except Exception:
                    pass


                ############################################
                # 5) LIMPAR BUFFERS DO GRÁFICO
                ############################################
                self.dados_tempo.clear()
                self.dados_tensao.clear()


                ############################################
                # 6) VOLTAR PARA TELA INICIAL E MOSTRAR MSG
                ############################################
                self.controller.show_frame("TelaInicial")

                # Aguarda UI trocar de tela antes do popup
                self.after(100, lambda: messagebox.showinfo("Teste finalizado", mensagem))



            # --- Teste de carga ---
            if tipo_teste == "carga" and tensao_carga > 0:
                if esp.ultima_tensao >= (tensao_carga - tolerancia):
                    print(f"[MONITORAMENTO] Tensão de carga atingida ({esp.ultima_tensao:.3f} V ≥ {tensao_carga:.3f} V)")
                    finalizar_teste("Tensão de carga atingida. Teste finalizado.")
                    return

            # --- Teste de descarga ---
            if tipo_teste == "carga" and tensao_descarga > 0:
                if esp.ultima_tensao <= (tensao_descarga + tolerancia):
                    print(f"[MONITORAMENTO] Tensão de descarga atingida ({esp.ultima_tensao:.3f} V ≤ {tensao_descarga:.3f} V)")
                    finalizar_teste("Tensão de descarga atingida. Teste finalizado.")
                    return

            # --- Ciclos ---
            if tipo_teste == "ciclos":
                # Se estamos descansando, não monitoramos mudança de estado
                if self.descanso_em_andamento:
                    # Atualiza contagem regressiva
                    self.tempo_restante_descanso -= 1
                    if self.tempo_restante_descanso <= 0:
                        # Descanso acabou — voltar ao AUTO e continuar teste
                        self.descanso_em_andamento = False
                        try:
                            esp.bateria_controller.alternar_modo()
                        except: pass
                    return

                # Detecta mudanças de carga ↔ descarga
                current_charge_state = esp.carga

                if self._prev_carga_state is None:
                    self._prev_carga_state = current_charge_state
                elif current_charge_state != self._prev_carga_state:

                    # Contou um ciclo
                    self.ciclo_atual += 1
                    self.controller.simulacao_dados["ciclo_atual"] = self.ciclo_atual
                    self._criar_log()
                    self.ciclo_label.config(text=f"Ciclo: {self.ciclo_atual}/{self.ciclos_totais}")
                    self._prev_carga_state = current_charge_state

                    # Verifica se finalizou
                    if self.ciclos_totais and self.ciclo_atual >= self.ciclos_totais:
                        finalizar_teste("Todos os ciclos concluídos. Teste finalizado.")
                        return

                    # Inicia descanso
                    descanso = int(self.controller.simulacao_dados.get("descanso", 60))
                    self.descanso_em_andamento = True
                    self.tempo_restante_descanso = descanso
                    self.descanso_label.config(text=f"Descanso: {descanso}s")

                    # Desliga carga/descarga no descanso
                    try:
                        esp.bateria_controller.desligar_tudo()
                    except:
                        pass

                    return


        except Exception as e:
            print(f"[MONITORAMENTO] Erro geral em atualizar_grafico: {e}")
            pass

    # =========================
    # Destroy seguro
    # =========================
    def destroy(self):
        esp = getattr(self.controller, "esp_reader", None)
        if esp:
            try:
                esp.parar_envio_periodico()
            except Exception:
                pass
        if hasattr(self, 'after_id') and self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
        if hasattr(self, 'ani') and self.ani.event_source:
            try:
                self.ani.event_source.stop()
            except Exception:
                pass
            del self.ani
        if hasattr(self, 'fig'):
            try:
                plt.close(self.fig)
            except Exception:
                pass
        super().destroy()