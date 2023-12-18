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

def find_valid_plates(possible_plates):
    valid_plates = []

    for plate in possible_plates:
        # Inicializa os índices
        idx = 0
        # Encontra as primeiras 3 letras
        first_three_letters = ''
        while idx < len(plate) and len(first_three_letters) < 3:
            if plate[idx].isalpha():
                first_three_letters += plate[idx]
            idx += 1

        # Encontra o próximo número
        next_digit = ''
        while idx < len(plate) and not plate[idx].isdigit():
            idx += 1
        while idx < len(plate) and plate[idx].isdigit() and len(next_digit) < 1:
            next_digit += plate[idx]
            idx += 1

        # Encontra a próxima letra ou numero
        next_character = ''
        while idx < len(plate) and not plate[idx].isalnum():
            idx += 1
        while idx < len(plate) and plate[idx].isalnum() and len(next_character) < 1:
            next_character += plate[idx]
            idx += 1

        # Encontra os próximos dois números
        next_two_digits = ''
        while idx < len(plate) and not plate[idx].isdigit():
            idx += 1
        while idx < len(plate) and plate[idx].isdigit() and len(next_two_digits) < 2:
            next_two_digits += plate[idx]
            idx += 1

        
        
        # Verifica se a placa atende aos critérios
        if (
            len(first_three_letters) == 3 and
            len(next_digit) == 1 and
            len(next_character) == 1 and
            len(next_two_digits) == 2
        ):
            new_plate = f"{first_three_letters}{next_digit}{next_character}{next_two_digits}"
            if new_plate not in valid_plates:
                valid_plates.append(new_plate)

    return valid_plates

def generate_possible_plates(plate_text, max_substitutions=2):
    substitutions = {
        '2': ['Z'],
        'Z': ['2'],
        '1': ['I'],
        'I': ['1'], 
        'O': ['Q', '0'],
        'Q': ['O'],
        'G': ['4'],
        '4': ['G'],
    }

    possible_plates = [plate_text]

    for _ in range(max_substitutions):
        current_plates = possible_plates[:]

        for plate in current_plates:
            for i, char in enumerate(plate):
                if char in substitutions:
                    for replacement in substitutions[char]:
                        new_plate = plate[:i] + replacement + plate[i+1:]
                        possible_plates.append(new_plate)

    return possible_plates

def is_brazilian_license_plate(text):
    # Padrão para placas brasileiras:
    brazilian_plate_pattern_mercosul = re.compile(r'^[A-Z]{3}-?\d{1}^[A-Z]{1}\d{2}')
    
    # Padrão para o sistema anterior com três letras e quatro números
    brazilian_plate_pattern_anterior = re.compile(r'^[A-Z]{3}-?\d{4}$')

    return bool(brazilian_plate_pattern_mercosul.match(text)) or bool(brazilian_plate_pattern_anterior.match(text))

def is_plate(image, contour):
    x, y, w, h = cv2.boundingRect(contour)                      #retângulo delimitador do contorno

    if (h >= w) or (w < 100 and h < 30):
        return False

    aspect_ratio = w / h
    if not (2.5 <= aspect_ratio <= 5.0):
        return False

    # OLD AQUI
    roi = image[y:y+h, x:x+w]                                   #recorta a região de interessa
    custom_config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 --oem 3'
    result = pytesseract.image_to_string(roi, config=custom_config, output_type=pytesseract.Output.DICT)
    possible_plate = result['text'].strip()
    first_seven_characters = possible_plate[:7]
    
    # # IMPRIMIR OS QUADRADOS
    # h, w = roi.shape[:2]
    # boxes = pytesseract.image_to_boxes(roi, config=custom_config)

    # for b in boxes.splitlines():
    #     b = b.split()
    #     char_x, char_y, char_w, char_h = int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])
    #     cv2.rectangle(roi, (char_x, char_y), (char_w, char_h), (0, 255, 0), 2)

    # # Display the image with bounding boxes
    # cv2.imshow('Character Boxes', roi)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    if len(possible_plate) >= 7 and '\n' not in possible_plate:
        print(f"Read from image={possible_plate}")
        possible_plates = generate_possible_plates(possible_plate)
        # print(f"Possible errors={possible_plates}")
        final_plates = find_valid_plates(possible_plates)
        print(f"\nPossible plates={final_plates}\n")
        if final_plates:
            return True
    
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
            break

    cv2.imshow("License Plate Detection", img_original)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

image = get_image()
find_license_plate(image)