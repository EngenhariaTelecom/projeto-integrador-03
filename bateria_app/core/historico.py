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
        Tenta ser tolerante a cabeçalhos diferentes e linhas inválidas.
        """
        caminho = os.path.join(self.pasta, nome_arquivo)
        tempos, tensoes = [], []
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # tenta várias chaves possíveis para tempo e tensão
                    t_raw = None
                    for key in ("Tempo (s)", "Tempo", "Time", "t"):
                        if key in row and row[key] not in (None, ""):
                            t_raw = row[key]
                            break
                    v_raw = None
                    for key in ("Tensao (V)", "Tensao", "Tensão (V)", "Tensão", "Voltage", "Vbat", "Tensao(V)"):
                        if key in row and row[key] not in (None, ""):
                            v_raw = row[key]
                            break

                    # Se faltou tempo ou tensão, pula a linha
                    if t_raw is None or v_raw is None:
                        continue

                    # tenta converter para float (aceita vírgula)
                    try:
                        t = float(str(t_raw).replace(",", "."))
                        v = float(str(v_raw).replace(",", "."))
                    except Exception:
                        # linha inválida -> ignora
                        continue

                    tempos.append(t)
                    tensoes.append(v)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar {nome_arquivo}: {e}")
        return tempos, tensoes