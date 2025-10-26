import serial
import serial.tools.list_ports
import threading
import time
import os
import csv

class ESPReader(threading.Thread):
    """
    Thread que lê dados da ESP32 via serial.
    Responsável por:
      - Buscar a porta automaticamente se não fornecida
      - Ler linha no formato: Vbat: 3.874 V | Mode: AUTO | Charge: ON | Disch: OFF
      - Salvar últimos valores em atributos: ultima_leitura, ultima_tensao, modo, carga, descarga
      - Salvar dados em CSV
    """
    def __init__(self, porta=None, baudrate=115200, arquivo_csv="assets/dados/dados_bateria.csv"):
        super().__init__(daemon=True)
        self.porta = porta
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.ultima_leitura = None
        self.ultima_tensao = None
        self.modo = "AUTO"
        self.carga = "OFF"
        self.descarga = "OFF"
        self.arquivo_csv = arquivo_csv
        self.tempo_inicial = time.time()
        self._criar_csv()

    def _criar_csv(self):
        pasta = os.path.dirname(self.arquivo_csv)
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        if not os.path.exists(self.arquivo_csv):
            with open(self.arquivo_csv, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Tempo (s)", "Tensao (V)", "Modo", "Carga", "Descarga"])

    def salvar_csv(self, tensao):
        t = time.time() - self.tempo_inicial
        with open(self.arquivo_csv, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f"{t:.1f}", f"{tensao:.3f}", self.modo, self.carga, self.descarga])

    def conectar(self):
        try:
            # Busca porta automaticamente
            if self.porta is None:
                portas_disponiveis = list(serial.tools.list_ports.comports())
                if not portas_disponiveis:
                    raise Exception("Nenhuma porta serial encontrada.")
                for p in portas_disponiveis:
                    try:
                        self.ser = serial.Serial(p.device, self.baudrate, timeout=1)
                        time.sleep(2)
                        self.ser.reset_input_buffer()
                        linha = self.ser.readline().decode(errors='ignore').strip()
                        if linha:
                            self.porta = p.device
                            print(f"✅ ESP32 detectada na porta {p.device}")
                            break
                        else:
                            self.ser.close()
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

    def run(self):
        if not self.ser:
            self.conectar()
        while self.running:
            try:
                linha = self.ser.readline().decode(errors='ignore').strip()
                if linha.startswith("Vbat:"):
                    partes = linha.split("|")
                    if len(partes) == 4:
                        self.ultima_tensao = float(partes[0].split(":")[1].split("V")[0])
                        self.modo = partes[1].split(":")[1].strip()
                        self.carga = partes[2].split(":")[1].strip()
                        self.descarga = partes[3].split(":")[1].strip()
                        self.ultima_leitura = int(self.ultima_tensao * 1000)  # opcional: converter pra mV
                        self.salvar_csv(self.ultima_tensao)
            except Exception:
                pass

    def parar(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
                print("🔌 Conexão encerrada.")
            except Exception:
                pass