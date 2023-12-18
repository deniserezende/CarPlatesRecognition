import os
import subprocess

def extrair_unicharset(diretorio):
    # Loop através dos arquivos .box no diretório
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".box"):
            nome_base = os.path.splitext(arquivo)[0]

            # Caminho completo para o arquivo
            caminho_arquivo = os.path.join(diretorio, arquivo)

            # Verificar se o arquivo está vazio
            if os.path.getsize(caminho_arquivo) == 0:
                print(f"Arquivo {arquivo} está vazio. Pulando...")
                continue

            # Comando unicharset_extractor
            comando_unicharset = f"unicharset_extractor {caminho_arquivo}"

            # Executar o comando unicharset_extractor usando subprocess
            subprocess.run(comando_unicharset, shell=True)

            print(f"Concluído para {arquivo}")

if __name__ == "__main__":
    # Substitua "/caminho/para/seu/diretorio" pelo caminho real para o diretório que contém seus arquivos .box
    diretorio_base = "/Users/Denise/Documents/GitHub/UELGit/CarPlatesRecognition/out/output_boxes"
    extrair_unicharset(diretorio_base)
