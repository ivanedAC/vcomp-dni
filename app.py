from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import lector
import tempfile
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Habilitar CORS si necesitas acceder desde otros dominios

# Configuración
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('camara.html')

@app.route('/api/leer-dni', methods=['POST'])
def leer_dni():
    """
    Endpoint para leer y extraer datos del DNI
    Acepta una imagen y retorna los datos extraídos
    """
    # Validar que se envió una imagen
    if 'imagen' not in request.files:
        return jsonify({
            'error': 'No se envió imagen',
            'codigo': 'NO_IMAGE'
        }), 400
    
    imagen = request.files['imagen']
    
    # Validar que el archivo tenga nombre
    if imagen.filename == '':
        return jsonify({
            'error': 'Archivo sin nombre',
            'codigo': 'EMPTY_FILENAME'
        }), 400
    
    # Validar extensión del archivo
    if not allowed_file(imagen.filename):
        return jsonify({
            'error': 'Formato de archivo no permitido. Use PNG, JPG o JPEG',
            'codigo': 'INVALID_FORMAT'
        }), 400
    
    # Guardar la imagen temporalmente
    filename = secure_filename(imagen.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
        imagen.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Llamar a la función del lector para extraer datos
        resultado = lector.leer_dni(tmp_path)
        
        # Validar que se extrajeron datos
        if not resultado.get('datos'):
            return jsonify({
                'error': 'No se pudieron extraer datos del DNI',
                'codigo': 'NO_DATA_EXTRACTED'
            }), 422
        
        # Devolver los datos y la imagen procesada
        return jsonify({
            'exito': True,
            'datos': resultado['datos'],
            'mensaje': 'Datos extraídos correctamente'
        }), 200
        
    except FileNotFoundError as e:
        return jsonify({
            'error': 'No se pudo leer la imagen',
            'codigo': 'FILE_NOT_FOUND',
            'detalle': str(e)
        }), 500
        
    except Exception as e:
        error_msg = str(e)
        codigo = 'PROCESSING_ERROR'
        
        # Identificar tipo de error específico
        if 'No se detectó el DNI' in error_msg:
            codigo = 'DNI_NOT_DETECTED'
        elif 'No se pudieron extraer suficientes datos' in error_msg:
            codigo = 'INSUFFICIENT_DATA'
        
        return jsonify({
            'error': error_msg,
            'codigo': codigo
        }), 500
        
    finally:
        # Eliminar el archivo temporal
        try:
            os.remove(tmp_path)
        except:
            pass

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servicio está activo"""
    return jsonify({
        'status': 'OK',
        'servicio': 'Lector de DNI',
        'version': '1.0'
    }), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """Manejo de archivos demasiado grandes"""
    return jsonify({
        'error': 'Archivo demasiado grande. Máximo 10MB',
        'codigo': 'FILE_TOO_LARGE'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor"""
    return jsonify({
        'error': 'Error interno del servidor',
        'codigo': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    # Configuración para desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # Para producción, usa:
    # app.run(host='0.0.0.0', port=5000, debug=False)