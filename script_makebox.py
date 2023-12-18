import os
import subprocess

def executar_tesseract(diretorio):
    # Loop através dos arquivos .jpg no diretório
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".jpg"):
            nome_base = os.path.splitext(arquivo)[0]

            # Caminho completo para o arquivo
            caminho_arquivo = os.path.join(diretorio, arquivo)

            # Comando tesseract
            comando_tesseract = f"tesseract {caminho_arquivo} {os.path.join(diretorio, 'output_boxes/output_base_' + nome_base)} batch.nochop makebox"

            # Executar o comando tesseract usando subprocess
            subprocess.run(comando_tesseract, shell=True)

            print(f"Concluído para {arquivo}")

if __name__ == "__main__":
    # Substitua "/caminho/para/seu/diretorio" pelo caminho real para o diretório que contém seus arquivos .jpg
    diretorio_base = "/Users/Denise/Documents/GitHub/UELGit/CarPlatesRecognition/out"
    executar_tesseract(diretorio_base)
