import base64
import cv2
import easyocr
from datetime import datetime
import re

# Inicializar el lector de EasyOCR
reader = easyocr.Reader(['es'])

def calcular_edad(fecha_nacimiento):
    fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%d %m %Y")
    hoy = datetime.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad

def extraer_datos(texto):
    # Función para extraer los datos del texto obtenido del OCR
    datos = {}
    
    match = re.search(r"Primer Apellido\s*([A-Za-záéíóúÁÉÍÓÚ]+)", texto)
    if match:
        datos['primerApellido'] = match.group(1)
    
    match = re.search(r"Segundo Apellido\s*([A-Za-záéíóúÁÉÍÓÚ]+)", texto)
    if match:
        datos['segundoApellido'] = match.group(1)
    
    match = re.search(r"Prenombres\s*([A-Za-záéíóúÁÉÍÓÚ ]+)", texto)
    if match:
        datos['prenombres'] = match.group(1)
    
    match = re.search(r"Fecha de Nacimiento\s*(\d{2} \d{2} \d{4})", texto)
    if match:
        datos['fechaNacimiento'] = match.group(1)
        datos['edad'] = calcular_edad(match.group(1))
    
    match = re.search(r"DOCUMENTO NACIONAL DE IDENTIDAD", texto)
    if match:
        datos['tipoDocumento'] = "DNI"
    
    match = re.search(r"\d{8}-\d", texto)  # Esto debería coincidir con el formato del DNI
    if match:
        datos['numeroDocumento'] = match.group(0)
    
    match = re.search(r"Sexo\s*(M|F)", texto)
    if match:
        datos['sexo'] = "MASCULINO" if match.group(1) == "M" else "FEMENINO"
    
    match = re.search(r"Estado Civil\s*(\w+)", texto)
    if match:
        datos['estadoCivil'] = match.group(1)
    
    datos['fechaHoraIngreso'] = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return datos

def auto_capture_dni(img):
    """
    Función que detecta automáticamente el área del DNI en la imagen utilizando contornos.
    Devuelve la imagen recortada que contiene solo el DNI, además de mostrar un rectángulo verde.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # Ajusta este valor según sea necesario
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            dni_img = img[y:y+h, x:x+w]
            return dni_img, img  # Devuelve la imagen con el rectángulo y el DNI recortado
    
    return None, img  # Si no se detectó ningún DNI

def leer_dni(path_imagen):
    # Leer la imagen usando OpenCV
    img = cv2.imread(path_imagen)
    if img is None:
        raise FileNotFoundError("No se pudo cargar la imagen. Revisa la ruta.")
    
    dni_img, img_con_rectangulo = auto_capture_dni(img)
    
    if dni_img is not None:
        # Convertir la imagen con el rectángulo verde a base64
        _, buffer = cv2.imencode('.jpg', img_con_rectangulo)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Usar EasyOCR para extraer texto del DNI recortado
        result = reader.readtext(dni_img)
        extracted_text = " ".join([text[1] for text in result])
        
        # Devolver los datos extraídos y la imagen con el rectángulo en base64
        return {
            'datos': extraer_datos(extracted_text),
            'imagen': img_base64
        }
    else:
        raise Exception("No se detectó el DNI en la imagen.")
