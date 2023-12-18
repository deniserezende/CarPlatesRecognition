try:
    from PIL import Image
except ImportError:
    import Image
import os
import cv2
import re
import numpy as np
import pytesseract

# pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

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
    contraste = cv2.multiply(imagem, np.array([0.7]))    #ajuste de contraste
    gray = cv2.cvtColor(contraste, cv2.COLOR_BGR2GRAY)   #escala de cinza
    blur = cv2.GaussianBlur(gray, (3,3), 0)              #redução de ruídos
    equalizada = cv2.equalizeHist(blur)                  #equalização de histograma (realce)
    binary = binary_quantize(equalizada)                 #binarização
    blur = cv2.GaussianBlur(binary, (3,3), 0)            #redução de ruídos
    cv2.imshow('Imagem tratada', blur)
    
    return blur

# 2 e Z
# 1 e I
# Q e O
# def replace_commun_letters(char):
#     if char == '2':
#         return 'Z'
#     if char == 'Z':
#         return '2'
#     if char == '1':
#         return 'I'

# def get_possible_plates(text):
#     # Verificar se o texto tem pelo menos 7 caracteres
#     if len(text) < 7:
#         return []

#     # RIOZAI94
#     # RIO2A19
#     possible_plates = []

#     # Padrão: 3 letras seguidas de 4 números
#     # 3 Letras
#     possible_letters = text[:3]
#     if not possible_letters.isalpha():
#         result = ""
#         for letter in possible_letters:
#                 if not letter.isalpha():
#                     result += replace_commun_letters(letter)
#                 else:
#                     result += letter
    
#     possible_numbers = text[2:]
                
#     # Padrão: 3 letras, 1 dígito, 1 letra, 2 dígitos

#     return possible_plates

def is_brazilian_license_plate(text):
    # Padrão para placas brasileiras:
    brazilian_plate_pattern_mercosul = re.compile(r'^[A-Z]{3}-?\d{1}^[A-Z]{1}\d{2}')
    
    # Padrão para o sistema anterior com três letras e quatro números
    brazilian_plate_pattern_anterior = re.compile(r'^[A-Z]{3}-?\d{4}$')

    return bool(brazilian_plate_pattern_mercosul.match(text)) or bool(brazilian_plate_pattern_anterior.match(text))

def extract_non_overlapping_boxes(image, boxes):
    selected_boxes = []

    for b in boxes.splitlines():
        b = b.split()
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        print(f"box: x={x}; y={y}; w={w}; h={h}")
        # Check if the current box is not overlapping with any selected box
        if all(not is_overlap(box, (x, y, w, h)) for box in selected_boxes):
            selected_boxes.append((x, y, w, h))

    return selected_boxes

def is_overlap(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def is_plate(image, contour):
    x, y, w, h = cv2.boundingRect(contour)                      #retângulo delimitador do contorno
    
    if (h >= w) or (w < 100 and h < 30):
        return False

    aspect_ratio = w / h
    if not (2.5 <= aspect_ratio <= 5.0):
        return False

    # roi = image[y:y+h, x:x+w]                                   #recorta a região de interessa
    # text = pytesseract.image_to_string(roi, config='--psm 6')   #tenta extrair o texto da imagem
    # print(text)

    # OLD AQUI
    roi = image[y:y+h, x:x+w]                                   #recorta a região de interessa
    custom_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --oem 3'
    result = pytesseract.image_to_string(roi, config=custom_config, output_type=pytesseract.Output.DICT)
    possible_plate = result['text'].strip()
    first_seven_characters = possible_plate[:7]

    # IMPRIMIR OS QUADRADOS
    h, w = roi.shape[:2]
    boxes = pytesseract.image_to_boxes(roi, config=custom_config)

    for b in boxes.splitlines():
        b = b.split()
        char_x, char_y, char_w, char_h = int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])
        cv2.rectangle(roi, (char_x, char_y), (char_w, char_h), (0, 255, 0), 2)

    # Display the image with bounding boxes
    cv2.imshow('Character Boxes', roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # # NEW
    # # Your code for extracting character boxes
    # roi = image[y:y+h, x:x+w]
    # custom_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --oem 3'
    # boxes = pytesseract.image_to_boxes(roi, config=custom_config)

    # # Extract non-overlapping boxes
    # selected_boxes = extract_non_overlapping_boxes(roi, boxes)
    # cv2.imshow('Character Boxes', roi)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # # Extract text from selected boxes
    # for box in selected_boxes:
    #     x, y, w, h = box
    #     char_roi = roi[y:h, x:w]
    #     result = pytesseract.image_to_string(char_roi, config=custom_config, output_type=pytesseract.Output.DICT)
    #     possible_plate = result['text'].strip()
    #     print(f"Text in box ({x}, {y}, {w}, {h}): {possible_plate}")

    # # Display the image with non-overlapping bounding boxes
    # for box in selected_boxes:
    #     x, y, w, h = box
    #     cv2.rectangle(roi, (x, y), (w, h), (0, 255, 0), 2)

    # cv2.imshow('Character Boxes (Non-overlapping)', roi)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # print(possible_plate)
    # return True

    print(possible_plate)
    print(f"first_seven_characters={first_seven_characters}")
    if is_brazilian_license_plate(first_seven_characters):
        print(first_seven_characters)
        # print("É uma placa brasileira.")
        return True
    else:
        # print("Não é uma placa brasileira.")
        return False

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