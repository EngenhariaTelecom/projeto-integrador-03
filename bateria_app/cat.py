import glob
import os

# Onde será salvo o resultado final
ARQUIVO_SAIDA = "concatenado.txt"

# Arquivos na raiz
arquivos = ["main.py"]

# Adiciona todos os arquivos .py da pasta ui/
arquivos.extend(sorted(glob.glob(os.path.join("ui", "*.py"))))

# Adiciona todos os arquivos .py da pasta core/
arquivos.extend(sorted(glob.glob(os.path.join("core", "*.py"))))

print("Arquivos encontrados:")
for a in arquivos:
    print(" -", a)

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as out:
    for i, arquivo in enumerate(arquivos):
        with open(arquivo, "r", encoding="utf-8") as f:
            # Nome do arquivo aparece como cabeçalho (opcional, mas útil)
            out.write(f"\n===== {arquivo} =====\n")
            out.write(f.read())

        # Não coloca separador no final
        if i < len(arquivos) - 1:
            out.write("\n==================================\n")

print(f"\nArquivo final gerado: {ARQUIVO_SAIDA}")