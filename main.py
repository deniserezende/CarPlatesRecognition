import os
import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

def get_image():
    folder = 'conjunto-de-dados'
    absolute_path = os.path.abspath(folder)
    png_files = [file for file in os.listdir(absolute_path) if file.endswith('.png')]   #recuperando todos os arquivos .png da pasta conjunto-de-dados

    print("\nConjunto de dados:")
    i = 0
    for arquivo in png_files:
        print(f"\t{i}. {arquivo}")
        i += 1

    indice = input("\nDigite o índice da imagem que deseja carregar: ")
    if indice == '.':
        image = 'image-car-front.png'
    else:
        image = png_files[int(indice)]
    image = cv2.imread(f'{folder}/{image}')
    
    return image

def binary_quantize(image):
    q_image = image.copy()
    q_image[q_image < 200] = 0      #define pixels mais escuros como preto
    q_image[q_image >= 200] = 255   #define pixels mais claros como branco

    return q_image

def pre_processing(imagem):
    contraste = cv2.multiply(imagem, np.array([0.8]))    #ajuste de contraste
    gray = cv2.cvtColor(contraste, cv2.COLOR_BGR2GRAY)   #escala de cinza
    blur = cv2.GaussianBlur(gray, (3,3), 0)              #redução de ruídos
    equalizada = cv2.equalizeHist(blur)                  #equalização de histograma (realce)
    binary = binary_quantize(equalizada)                 #binarização
    blur = cv2.GaussianBlur(binary, (3,3), 0)            #redução de ruídos
    
    cv2.imshow('Imagem tratada', blur)
    
    return blur

def is_plate(image, contour):
    
    x, y, w, h = cv2.boundingRect(contour)                      #retângulo delimitador do contorno
    
    if h >= w or (w < 100 and h < 30):
        return False

    roi = image[y:y+h, x:x+w]                                   #recorta a região de interessa
    text = pytesseract.image_to_string(roi, config='--psm 6')   #tenta extrair o texto da imagem
    print(text)

    if any(c.isalpha() or c.isdigit() for c in text):
        return True
    else:
        return False

def find_license_plate(img_original):
    image = pre_processing(img_original)    #pré-processamento da imagem   
    edges = cv2.Canny(image, 50, 150)       #detecção de bordas
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #encontrando contornos na imagem

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if is_plate(image, approx):
            x, y, w, h = cv2.boundingRect(contour) #desenha uma caixa delimitadora ao redor da placa
            cv2.rectangle(img_original, (x, y), (x + w, y + h), (0, 255, 0), 2)
            print("Placa detectada!")

    cv2.imshow("License Plate Detection", img_original)
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