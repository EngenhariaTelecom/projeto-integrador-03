# core/bateria.py
class BateriaController:
    """
    Envia comandos via serial para a ESP32
    """
    def __init__(self, esp_reader):
        self.esp = esp_reader

    def iniciar_carga(self):
        self.esp.enviar_comando("CHARGE ON")
        self.esp.enviar_comando("DISCH OFF")

    def iniciar_descarga(self):
        self.esp.enviar_comando("DISCH ON")
        self.esp.enviar_comando("CHARGE OFF")

    def alternar_modo(self):
        self.esp.enviar_comando("AUTO")

    def desligar_tudo(self):
        self.esp.enviar_comando("CHARGE OFF")
        self.esp.enviar_comando("DISCH OFF")