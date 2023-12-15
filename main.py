import os
import cv2
import numpy as np
import re
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'c:/users/laura/appdata/local/packages/pythonsoftwarefoundation.python.3.10_qbz5n2kfra8p0/localcache/local-packages/python310/site-packages'


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
    imagem_equalizada=binary_quantize(imagem_equalizada)

    # Equalização de Histograma
    # Pode ser feita diretamente na imagem colorida ou em cada canal separadamente
    canais = cv2.split(imagem_equalizada)
    equalizados = [cv2.equalizeHist(channel) for channel in canais]
    imagem_equalizada_dois = cv2.merge(equalizados)

    # Exibir as imagens resultantes (para análise visual)
    #cv2.imshow('Imagem Original', imagem)
    #cv2.imshow('Imagem com Contraste Ajustado', imagem_contraste)
    #cv2.imshow('Imagem com Redução de Ruídos', imagem_ruido)
    cv2.imshow('Imagem com Realce de Histograma', imagem_equalizada_dois)
    
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


"""def is_plate(contour):
    # Calcule o retângulo delimitador do contorno
    x, y, w, h = cv2.boundingRect(contour)

    # Defina uma relação mínima entre altura e largura para considerar como placa
    min_aspect_ratio = 0.5

    # Verifique se a relação entre altura e largura atende à condição de placa
    return h < w and h / w > min_aspect_ratio
    """
def is_plate(image, contour):
    # Calculate the bounding rectangle of the contour
    x, y, w, h = cv2.boundingRect(contour)

    # Crop the region of interest (ROI) from the image using the bounding rectangle
    roi = image[y:y+h, x:x+w]

    # Convert the cropped region to grayscale
    #gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Use Tesseract OCR to extract text from the cropped region
    text = pytesseract.image_to_string(roi, config='--psm 8')

    # Check if the extracted text contains letters or numbers
    if any(c.isalpha() or c.isdigit() for c in text):
        return True
    else:
        return False

def find_license_plate(image_original):

    # Pré-processamento da imagem
    image = pre_processing(image_original)

    # Detecção de bordas usando Canny
    edges = cv2.Canny(image, 50, 150)

    # Encontrar contornos na imagem
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterar sobre os contornos
    for contour in contours:
        # Ajuste de polígono para o contorno
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Verificar se o contorno representa uma placa
        if is_plate(image, approx):
            # Desenhar a caixa delimitadora ao redor da placa
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image_original, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            print("Contorno descartado. Não representa uma placa.")

    # Exibir a imagem resultante
    cv2.imshow("License Plate Detection", image_original)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  
image = get_image()
find_license_plate(image)


"""def detect_license_plate(rectangle_text):
    # Padrão de placa de veículo brasileira (exemplo, adapte conforme necessário)
    license_plate_pattern = re.compile(r'^[A-Z]{3}\d{4}$')

    # Verificar se o texto dentro do retângulo corresponde ao padrão da placa de veículo
    match = license_plate_pattern.match(rectangle_text)

    # Se houver correspondência, é uma placa de veículo
    if match:
        return True
    else:
        return False
# Exemplo de uso
rectangle_text = "ABC1234"
result = detect_license_plate(rectangle_text)

if result:
    print("Placa de veículo detectada!")
else:
    print("Não é uma placa de veículo.")"""