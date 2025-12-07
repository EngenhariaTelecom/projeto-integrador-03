# core/monitor.py
import serial
import serial.tools.list_ports
from .bateria import BateriaController
import threading
import time
import os
import csv

class ESPReader(threading.Thread):
    """
    Thread que lê dados da ESP32 via serial.
    Grava CSV por timer periódico controlado (para evitar gravações duplicadas).
    Possui controle de envio periódico de comandos (USB ON).
    """

    def __init__(self, porta=None, baudrate=115200):
        super().__init__(daemon=True)
        self.porta = porta
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.ultima_leitura = None
        self.ultima_tensao = None
        self.corrente = None
        self.modo = "AUTO"
        self.carga = "OFF"
        self.descarga = "OFF"
        self.arquivo_csv = None
        self.tempo_inicial = time.time()
        self.bateria_controller = BateriaController(self)

        # Controle de envio periódico (comando USB ON)
        self._envio_ativo = False
        self._thread_envio = None
        self._envio_intervalo = 3
        self._envio_comando = "USB ON"

        # Controle de gravação periódica (threading.Timer)
        self.enviando = False    # flag para gravação periódica
        self._save_timer = None
        self._save_interval = 1.0

        # Proteções
        self._last_save_time = 0.0
        self._save_min_interval = 0.8  # evita duplicatas (s)
        self._stop_requested = False

        # cache do ciclo fornecido pela TelaMonitoramento
        self._ciclo_cache = 0

    # ===============================
    # CSV
    # ===============================
    def definir_csv(self, caminho_csv):
        """Define arquivo CSV e garante cabeçalho (inclui Corrente e Ciclo)."""
        self.arquivo_csv = os.path.abspath(caminho_csv)
        pasta = os.path.dirname(self.arquivo_csv)
        os.makedirs(pasta, exist_ok=True)
        if not os.path.exists(self.arquivo_csv):
            with open(self.arquivo_csv, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Tempo (s)",
                    "Tensao (V)",
                    "Corrente (A)",
                    "Modo",
                    "Carga",
                    "Descarga",
                    "Ciclo"
                ])
        # reseta tempo inicial sempre que (re)definir CSV
        self.tempo_inicial = time.time()
        self._last_save_time = 0.0

    def set_ciclo(self, valor):
        """TelaMonitoramento deve chamar isso ao atualizar o ciclo."""
        try:
            self._ciclo_cache = int(valor)
        except:
            self._ciclo_cache = 0

    def salvar_csv(self, tensao, corrente):
        """Salva uma linha no CSV. Throttling para evitar duplicatas."""
        # Bloqueia gravação se já requisitado parar
        if self._stop_requested:
            return

        # Só grava se arquivo definido e gravação periódica ativada (enviando)
        if not self.arquivo_csv:
            return
        # Se gravação periódica não estiver ativa, não gravar (evita gravação pela UI)
        if not self.enviando:
            return

        agora = time.time()
        if agora - self._last_save_time < self._save_min_interval:
            # evita gravações repetidas muito próximas (ex.: run + timer + UI)
            return

        self._last_save_time = agora

        t = agora - self.tempo_inicial

        ciclo = getattr(self, "_ciclo_cache", 0)
        try:
            with open(self.arquivo_csv, "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    f"{t:.1f}",
                    f"{tensao:.3f}" if tensao is not None else "",
                    f"{corrente:.3f}" if corrente is not None else "",
                    self.modo,
                    self.carga,
                    self.descarga,
                    ciclo
                ])
        except Exception as e:
            print(f"[ESPReader] Erro ao escrever CSV: {e}")

    # ===============================
    # Conexão
    # ===============================
    def conectar(self):
        try:
            if self.porta is None:
                portas_disponiveis = list(serial.tools.list_ports.comports())
                if not portas_disponiveis:
                    raise Exception("Nenhuma porta serial encontrada.")
                for p in portas_disponiveis:
                    try:
                        self.ser = serial.Serial(p.device, self.baudrate, timeout=1)
                        time.sleep(2)
                        try:
                            self.ser.reset_input_buffer()
                        except Exception:
                            pass
                        linha = self.ser.readline().decode(errors='ignore').strip()
                        if linha:
                            self.porta = p.device
                            print(f"✅ ESP32 detectada na porta {p.device}")
                            break
                        else:
                            try:
                                self.ser.close()
                            except Exception:
                                pass
                    except Exception:
                        continue
                if not self.ser or not self.ser.is_open:
                    raise Exception("Nenhuma ESP32 respondendo nas portas disponíveis.")
            else:
                self.ser = serial.Serial(self.porta, self.baudrate, timeout=1)
                time.sleep(2)
                print(f"✅ Conectado manualmente à ESP32 na porta {self.porta}")
            self.running = True
        except Exception as e:
            print("❌ Erro ao conectar à ESP32:", e)
            self.running = False

    # ===============================
    # Loop de leitura principal
    # ===============================
    def run(self):
        if not self.ser:
            self.conectar()
        while self.running and not self._stop_requested:
            try:
                # readline tem timeout=1, então não fica preso indefinidamente
                linha = ""
                try:
                    linha = self.ser.readline().decode(errors='ignore').strip() if (self.ser and self.ser.is_open) else ""
                except Exception:
                    # se a porta foi fechada, readline pode lançar; quebra o loop se parar solicitado
                    if not self.running or self._stop_requested:
                        break
                    else:
                        time.sleep(0.1)
                        continue

                if not linha:
                    # sem dados lidos -> continua
                    continue

                # Ex.: "Vbat: 4.15 V | Mode: AUTO | Charge: ON | Disch: OFF | Corrente: 0.56 A"
                if linha.startswith("Vbat:"):
                    # print(linha)   # mantenha se quiser debug
                    partes = [p.strip() for p in linha.split("|")]
                    if len(partes) >= 5:
                        try:
                            # Tensao
                            p0 = partes[0].split(":", 1)[1].strip()
                            self.ultima_tensao = float(p0.replace("V", "").strip())
                            # Mode
                            self.modo = partes[1].split(":", 1)[1].strip()
                            # Charge
                            self.carga = partes[2].split(":", 1)[1].strip()
                            # Disch
                            self.descarga = partes[3].split(":", 1)[1].strip()
                            # Corrente
                            p4 = partes[4].split(":", 1)[1].strip()
                            try:
                                self.corrente = float(p4.replace("A", "").strip())
                            except:
                                self.corrente = None
                            self.ultima_leitura = int(self.ultima_tensao * 1000) if self.ultima_tensao is not None else None

                            # IMPORTANT: não chamamos salvar_csv aqui para evitar duplicação
                            # a gravação periódica é controlada pelo timer (iniciar_envio_periodico)
                        except Exception as e:
                            print(f"⚠️ Erro ao interpretar linha: {e}")
            except Exception:
                # se ocorrer erro de leitura, aguarda e continua até running=False
                # print("⚠️ Erro ao ler dados da ESP32.")
                time.sleep(0.1)
                continue

        # fim do loop run
        # garante que gravação periódica pare quando thread terminar
        self._stop_requested = True
        try:
            self.parar_envio_periodico()
        except:
            pass

    # ===============================
    # Envio periódico de comando (USB ON) e inicio do loop de gravação
    # ===============================
    def _sending_thread(self):
        """Thread que envia o comando USB ON a cada intervalo (se ativo)."""
        while self._envio_ativo and self.ser and getattr(self.ser, "is_open", False):
            try:
                self.ser.write((self._envio_comando + "\n").encode())
                # print(f"[SERIAL] Enviado: {self._envio_comando}")
            except Exception as e:
                print(f"[SERIAL] Falha ao enviar '{self._envio_comando}': {e}")
            # aguarda intervalo, mas pode sair se _envio_ativo virar False
            for _ in range(int(self._envio_intervalo * 10)):
                if not self._envio_ativo:
                    break
                time.sleep(0.1)

    def _loop_save(self):
        """Loop de gravação periódica acionado via threading.Timer."""
        if not self.enviando or self._stop_requested:
            return
        try:
            # grava usando os últimos valores lidos
            self.salvar_csv(self.ultima_tensao, self.corrente)
        except Exception as e:
            print("[ESPReader] erro ao salvar CSV:", e)
        # agenda próxima execução
        try:
            self._save_timer = threading.Timer(self._save_interval, self._loop_save)
            self._save_timer.daemon = True
            self._save_timer.start()
        except Exception as e:
            print("[ESPReader] falha ao agendar next save:", e)

    def iniciar_envio_periodico(self, comando="USB ON", intervalo=3):
        """Inicia thread que envia comando periódico à ESP e inicia a gravação periódica."""
        # Inicia envio de comando (thread contínua)
        try:
            self._envio_comando = comando
            self._envio_intervalo = intervalo
            if not (self._thread_envio and self._thread_envio.is_alive()):
                self._envio_ativo = True
                self._thread_envio = threading.Thread(target=self._sending_thread, daemon=True)
                self._thread_envio.start()
        except Exception as e:
            print("[ESPReader] falha ao iniciar thread de envio:", e)

        # Inicia gravação periódica (timer)
        try:
            if not self.enviando:
                self.enviando = True
                # garante que não temos timer ativo
                try:
                    if self._save_timer:
                        self._save_timer.cancel()
                except:
                    pass
                # começa loop de gravação
                self._loop_save()
        except Exception as e:
            print("[ESPReader] falha ao iniciar gravação periódica:", e)

    def parar_envio_periodico(self):
        """Interrompe o envio periódico e a gravação periódica."""
        self._envio_ativo = False
        try:
            if self._thread_envio and self._thread_envio.is_alive():
                # thread verá _envio_ativo False e terminará
                pass
        except:
            pass

        # para gravação periódica
        self.enviando = False
        try:
            if self._save_timer:
                self._save_timer.cancel()
        except:
            pass
        self._save_timer = None

    # ===============================
    # Encerramento
    # ===============================
    def parar(self):
        """Parada limpa: impede gravação e encerra conexão serial."""
        self._stop_requested = True
        self.running = False

        # para timers/loops
        try:
            self.parar_envio_periodico()
        except:
            pass

        # fecha serial para desbloquear readline
        try:
            if self.ser:
                try:
                    self.ser.close()
                except:
                    pass
        except:
            pass

        # tenta aguardar thread terminar (join)
        try:
            if self.is_alive():
                self.join(timeout=1)
        except:
            pass