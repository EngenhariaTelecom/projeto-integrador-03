# core/esp_backend.py
import serial
import threading
import time

class ESPReader(threading.Thread):
    """Thread que lê dados da ESP32 via serial e mantém o último valor atualizado."""

    def __init__(self, porta='/dev/ttyUSB0', baudrate=115200):
        super().__init__(daemon=True)
        self.porta = porta
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.ultima_leitura = None
        self.ultima_tensao = None

    def conectar(self):
        try:
            self.ser = serial.Serial(self.porta, self.baudrate, timeout=1)
            time.sleep(2)  # tempo para inicializar a conexão
            self.running = True
            print("✅ Conectado à ESP32!")
        except Exception as e:
            print("❌ Erro ao conectar:", e)

    def run(self):
        """Loop que lê continuamente os dados"""
        if not self.ser:
            self.conectar()
        while self.running:
            try:
                linha = self.ser.readline().decode('utf-8').strip()
                if linha:
                    leitura, tensao = linha.split(',')
                    self.ultima_leitura = int(leitura)
                    self.ultima_tensao = float(tensao)
            except Exception as e:
                print("⚠️ Erro na leitura:", e)

    def parar(self):
        self.running = False
        if self.ser:
            self.ser.close()
            print("🔌 Conexão encerrada.")
