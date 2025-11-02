# core/bateria.py
class BateriaController:
    """
    Envia comandos via serial para a ESP32
    """
    def __init__(self, esp_reader):
        self.esp = esp_reader

    def enviar_comando(self, comando: str):
        """Envia um comando via Serial para a ESP32"""
        if self.esp.ser and self.esp.ser.is_open:
            try:
                self.esp.ser.write((comando + "\n").encode())
                print(f"📤 Enviado para ESP32: {comando}")
            except Exception as e:
                print(f"⚠️ Erro ao enviar comando '{comando}': {e}")

    def iniciar_carga(self):
        self.enviar_comando("CHARGE ON")
        self.enviar_comando("DISCH OFF")

    def iniciar_descarga(self):
        self.enviar_comando("DISCH ON")
        self.enviar_comando("CHARGE OFF")

    def alternar_modo(self):
        self.enviar_comando("AUTO")

    def desligar_tudo(self):
        self.enviar_comando("CHARGE OFF")
        self.enviar_comando("DISCH OFF")