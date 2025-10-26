# core/historico.py
import csv
import os
from collections import deque
import time

class Historico:
    """
    Lê dados da ESPReader ou de um CSV e fornece listas de dados para gráfico.
    """
    def __init__(self, esp_reader=None, arquivo_csv=None, max_pontos=300):
        self.esp = esp_reader
        self.arquivo_csv = arquivo_csv
        self.max_pontos = max_pontos
        self.tempo = deque(maxlen=max_pontos)
        self.tensao = deque(maxlen=max_pontos)

    def atualizar(self):
        """Atualiza dados do ESPReader ou CSV"""
        if self.esp and self.esp.ultima_tensao is not None:
            t = time.time()
            self.tempo.append(t)
            self.tensao.append(self.esp.ultima_tensao)
        elif self.arquivo_csv:
            self._ler_csv()

    def _ler_csv(self):
        """Carrega CSV completo"""
        if not os.path.exists(self.arquivo_csv):
            return
        with open(self.arquivo_csv, "r") as f:
            reader = csv.DictReader(f)
            self.tempo.clear()
            self.tensao.clear()
            for row in reader:
                self.tempo.append(float(row["Tempo (s)"]))
                self.tensao.append(float(row["Tensao (V)"]))

    def get_dados(self):
        return list(self.tempo), list(self.tensao)