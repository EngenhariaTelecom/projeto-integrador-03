# core/monitor.py
import serial
import serial.tools.list_ports
import threading
import time

class ESPReader(threading.Thread):
    """Thread que lê dados da ESP32 via serial e mantém o último valor atualizado."""

    def __init__(self, porta=None, baudrate=115200):
        super().__init__(daemon=True)
        self.porta = porta
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self.ultima_leitura = None
        self.ultima_tensao = None

    def conectar(self):
        try:
            # se a porta não foi especificada, tenta detectar automaticamente
            if self.porta is None:
                print("🔍 Procurando porta serial da ESP32...")
                portas_disponiveis = list(serial.tools.list_ports.comports())

                if not portas_disponiveis:
                    raise Exception("Nenhuma porta serial encontrada.")

                for porta in portas_disponiveis:
                    try:
                        print(f"🔌 Testando {porta.device}...")
                        self.ser = serial.Serial(porta.device, self.baudrate, timeout=1)
                        time.sleep(2)  # tempo para estabilizar

                        # tentativa de leitura
                        self.ser.reset_input_buffer()
                        linha = self.ser.readline().decode('utf-8').strip()
                        if linha:
                            print(f"✅ ESP32 detectada na porta {porta.device}")
                            self.porta = porta.device
                            break
                        else:
                            self.ser.close()
                    except Exception:
                        continue

                if not self.ser or not self.ser.is_open:
                    raise Exception("Nenhuma ESP32 respondendo nas portas disponíveis.")

            else:
                # caso a porta seja informada manualmente
                self.ser = serial.Serial(self.porta, self.baudrate, timeout=1)
                time.sleep(2)
                print(f"✅ Conectado manualmente à ESP32 na porta {self.porta}")

            self.running = True

        except Exception as e:
            print("❌ Erro ao conectar à ESP32:", e)
            self.running = False

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
            try:
                self.ser.close()
                print("🔌 Conexão encerrada.")
            except Exception:
                pass
