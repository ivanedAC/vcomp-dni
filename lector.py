import base64
import cv2
import numpy as np
import easyocr
from datetime import datetime
import re

# Inicializar el lector de EasyOCR
reader = easyocr.Reader(['es'], gpu=False)

def calcular_edad(fecha_nacimiento):
    """Calcula la edad a partir de una fecha de nacimiento"""
    try:
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%d %m %Y")
        hoy = datetime.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        return edad
    except:
        return None

def preprocesar_imagen(img):
    """
    Preprocesamiento avanzado de la imagen para mejorar la extracción de texto
    """
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar CLAHE para mejorar contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # Reducir ruido
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Binarización adaptativa
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Dilatar ligeramente para conectar componentes de texto
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.dilate(binary, kernel, iterations=1)
    
    return processed

def detectar_dni(img):
    """
    Detecta automáticamente el área del DNI en la imagen
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar desenfoque para reducir ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detección de bordes
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilatar para conectar bordes
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos por área y relación de aspecto típica de un DNI
    dni_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:  # Área mínima
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            # DNI peruano tiene relación de aspecto aproximada de 1.5-1.7
            if 1.3 < aspect_ratio < 1.9 and area > img.shape[0] * img.shape[1] * 0.1:
                dni_contours.append((area, x, y, w, h))
    
    if dni_contours:
        # Seleccionar el contorno más grande
        dni_contours.sort(reverse=True, key=lambda x: x[0])
        _, x, y, w, h = dni_contours[0]
        
        # Agregar margen
        margin = 10
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img.shape[1] - x, w + 2*margin)
        h = min(img.shape[0] - y, h + 2*margin)
        
        # Dibujar rectángulo en la imagen original
        img_con_rectangulo = img.copy()
        cv2.rectangle(img_con_rectangulo, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        # Extraer región del DNI
        dni_img = img[y:y+h, x:x+w]
        
        return dni_img, img_con_rectangulo
    
    return None, img

def extraer_datos(texto):
    """
    Extrae datos del texto OCR con patrones más flexibles
    """
    datos = {}
    
    # Limpiar el texto
    texto = texto.upper()
    
    # Tipo de documento
    if "DOCUMENTO NACIONAL" in texto or "DNI" in texto or "IDENTIDAD" in texto:
        datos['tipoDocumento'] = "DNI"
    
    # Número de DNI (8 dígitos)
    match = re.search(r'\b(\d{8})\b', texto)
    if match:
        datos['numeroDocumento'] = match.group(1)
    
    # Primer Apellido
    patterns_apellido1 = [
        r"PRIMER\s*APELLIDO[:\s]*([A-ZÁÉÍÓÚÑ]+)",
        r"APELLIDO\s*PATERNO[:\s]*([A-ZÁÉÍÓÚÑ]+)",
        r"PATERNO[:\s]*([A-ZÁÉÍÓÚÑ]+)"
    ]
    for pattern in patterns_apellido1:
        match = re.search(pattern, texto)
        if match:
            datos['primerApellido'] = match.group(1).title()
            break
    
    # Segundo Apellido
    patterns_apellido2 = [
        r"SEGUNDO\s*APELLIDO[:\s]*([A-ZÁÉÍÓÚÑ]+)",
        r"APELLIDO\s*MATERNO[:\s]*([A-ZÁÉÍÓÚÑ]+)",
        r"MATERNO[:\s]*([A-ZÁÉÍÓÚÑ]+)"
    ]
    for pattern in patterns_apellido2:
        match = re.search(pattern, texto)
        if match:
            datos['segundoApellido'] = match.group(1).title()
            break
    
    # Prenombres
    patterns_nombres = [
        r"PRENOMBRES?[:\s]*([A-ZÁÉÍÓÚÑ\s]+?)(?=FECHA|NACIMIENTO|SEXO|\d)",
        r"NOMBRES?[:\s]*([A-ZÁÉÍÓÚÑ\s]+?)(?=FECHA|NACIMIENTO|SEXO|\d)"
    ]
    for pattern in patterns_nombres:
        match = re.search(pattern, texto)
        if match:
            nombres = match.group(1).strip()
            # Limpiar palabras comunes que no son nombres
            nombres = re.sub(r'\b(FECHA|NACIMIENTO|SEXO|ESTADO)\b', '', nombres).strip()
            if nombres:
                datos['prenombres'] = nombres.title()
                break
    
    # Fecha de Nacimiento (múltiples formatos)
    patterns_fecha = [
        r'(\d{2})[/\s.-](\d{2})[/\s.-](\d{4})',
        r'(\d{2})\s+(\d{2})\s+(\d{4})'
    ]
    for pattern in patterns_fecha:
        match = re.search(pattern, texto)
        if match:
            fecha = f"{match.group(1)} {match.group(2)} {match.group(3)}"
            datos['fechaNacimiento'] = fecha
            edad = calcular_edad(fecha)
            if edad:
                datos['edad'] = edad
            break
    
    # Sexo
    match = re.search(r'SEXO[:\s]*(M|F|MASCULINO|FEMENINO)', texto)
    if match:
        sexo = match.group(1)
        if sexo in ['M', 'MASCULINO']:
            datos['sexo'] = "MASCULINO"
        elif sexo in ['F', 'FEMENINO']:
            datos['sexo'] = "FEMENINO"
    
    # Estado Civil
    estados_civiles = ['SOLTERO', 'CASADO', 'VIUDO', 'DIVORCIADO']
    for estado in estados_civiles:
        if estado in texto:
            datos['estadoCivil'] = estado
            break
    
    # Fecha y hora de ingreso
    datos['fechaHoraIngreso'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    return datos

def leer_dni(path_imagen):
    """
    Función principal para leer y extraer datos del DNI
    """
    # Leer la imagen
    img = cv2.imread(path_imagen)
    if img is None:
        raise FileNotFoundError("No se pudo cargar la imagen. Revisa la ruta.")
    
    # Detectar área del DNI
    dni_img, img_con_rectangulo = detectar_dni(img)
    
    if dni_img is None:
        raise Exception("No se detectó el DNI en la imagen. Asegúrate de que el DNI sea visible.")
    
    # Preprocesar la imagen del DNI
    dni_procesado = preprocesar_imagen(dni_img)
    
    # Convertir la imagen con el rectángulo a base64
    _, buffer = cv2.imencode('.jpg', img_con_rectangulo)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Extraer texto usando EasyOCR en ambas versiones (original y procesada)
    result_original = reader.readtext(dni_img)
    result_procesado = reader.readtext(dni_procesado)
    
    # Combinar resultados
    texto_original = " ".join([text[1] for text in result_original])
    texto_procesado = " ".join([text[1] for text in result_procesado])
    texto_completo = texto_original + " " + texto_procesado
    
    # Extraer datos
    datos_extraidos = extraer_datos(texto_completo)
    
    # Validar que se extrajeron datos mínimos
    if not datos_extraidos or len(datos_extraidos) < 3:
        raise Exception("No se pudieron extraer suficientes datos del DNI. Intenta con mejor iluminación.")
    
    return {
        'datos': datos_extraidos,
        'imagen': img_base64,
        'textoExtraido': texto_completo[:500]  # Para debugging
    }