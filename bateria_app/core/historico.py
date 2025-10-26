# core/historico.py
import csv
import os

class Historico:
    """
    Manipula arquivos CSV contendo dados de tensão ao longo do tempo.
    Responsável por carregar e preparar dados para o gráfico.
    """
    def __init__(self, pasta_dados="assets/dados"):
        self.pasta = pasta_dados
        if not os.path.exists(self.pasta):
            os.makedirs(self.pasta)

    def listar_csvs(self):
        """Retorna uma lista dos arquivos CSV disponíveis na pasta de dados."""
        return [f for f in os.listdir(self.pasta) if f.lower().endswith(".csv")]

    def carregar_dados(self, nome_arquivo):
        """
        Carrega dados de um arquivo CSV e retorna listas de tempo e tensão.
        Retorna ([], []) se o arquivo estiver vazio ou inválido.
        """
        caminho = os.path.join(self.pasta, nome_arquivo)
        tempos, tensoes = [], []
        try:
            with open(caminho, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tempos.append(float(row.get("Tempo (s)", 0)))
                    tensoes.append(float(row.get("Tensao (V)", 0)))
        except Exception as e:
            print(f"[ERRO] Falha ao carregar {nome_arquivo}: {e}")
        return tempos, tensoes