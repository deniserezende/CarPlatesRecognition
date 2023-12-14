import os
import cv2
import numpy as np
# from PIL import Image
# import pytesseract


def get_image():
    pasta_desejada = 'conjunto-de-dados'

    caminho_completo = os.path.abspath(pasta_desejada)

    arquivos_png = [arquivo for arquivo in os.listdir(caminho_completo) if arquivo.endswith('.png')]

    print("\nArquivos PNG na pasta local:")
    for arquivo in arquivos_png:
        print(f"\t{arquivo}")

    nome_do_arquivo = input("\nDigite o nome do arquivo PNG que você deseja carregar: ")
    if nome_do_arquivo == '.':
        nome_do_arquivo = 'image-car-front.png'
    image = cv2.imread(f'{pasta_desejada}/{nome_do_arquivo}')
    return image


def binary_quantize(image):
    q_image = image.copy()

    # Aplica a quantização binária
    q_image[q_image < 200] = 0  # Define pixels mais escuros como preto
    q_image[q_image >= 200] = 255  # Define pixels mais claros como branco

    return q_image


def pre_processing(imagem):
    # Ajustes de Contraste
    # Você pode ajustar o contraste multiplicando a imagem por um fator
    contraste_fator = 0.3
    imagem_contraste = cv2.multiply(imagem, np.array([contraste_fator]))

    # Redução de Ruídos
    # Utilize um filtro gaussiano para reduzir ruídos
    imagem_ruido = cv2.GaussianBlur(imagem_contraste, (5, 5), 0)

    # Realce
    # Pode ser feito através de equalização do histograma
    imagem_gray = cv2.cvtColor(imagem_ruido, cv2.COLOR_RGB2GRAY)
    imagem_equalizada = cv2.equalizeHist(imagem_gray)
    # imagem_equalizada=binary_quantize(imagem_equalizada)

    # Equalização de Histograma
    # Pode ser feita diretamente na imagem colorida ou em cada canal separadamente
    canais = cv2.split(imagem_equalizada)
    equalizados = [cv2.equalizeHist(channel) for channel in canais]
    imagem_equalizada_dois = cv2.merge(equalizados)

    # Exibir as imagens resultantes (para análise visual)
    cv2.imshow('Imagem Original', imagem)
    cv2.imshow('Imagem com Contraste Ajustado', imagem_contraste)
    cv2.imshow('Imagem com Redução de Ruídos', imagem_ruido)
    cv2.imshow('Imagem com Realce de Histograma', imagem_equalizada_dois)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return imagem_equalizada_dois


def detect_plates(image):
    # if len(image.shape) == 2:
    #     print("Convertendo imagem para colorida.")
    #     image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    #
    # # Converte a imagem para tons de cinza
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Realiza a detecção de bordas usando o operador Canny
    edges = cv2.Canny(image, 50, 150)

    # Encontra contornos na imagem
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # # Filtrando os contornos com base em sua área
    # filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]
    #
    # # Desenhando os contornos na imagem original
    # cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 2)

    # Filtra os contornos que podem representar placas veiculares
    plate_contours = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.09 * perimeter, True)

        # Considera apenas os contornos que têm aproximadamente 4 vértices (placas retangulares)
        if len(approx) == 4:
            plate_contours.append(approx)

    # Desenha os contornos das placas na imagem original
    cv2.drawContours(image, contours, -1, (0, 255, 0), 1)

    # Exibe a imagem resultante
    cv2.imshow('Plates Detected', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()



image = get_image()
pre_proceed_image = pre_processing(image)
detect_plates(pre_proceed_image)

