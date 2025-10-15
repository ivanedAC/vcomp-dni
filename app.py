from flask import Flask, request, jsonify, render_template
import lector
import tempfile
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('camara.html')

@app.route('/api/leer-dni', methods=['POST'])
def leer_dni():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió imagen'}), 400
    
    imagen = request.files['imagen']
    
    # Guardar la imagen temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        imagen.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Llamar a la función del lector para extraer datos e imagen procesada
        resultado = lector.leer_dni(tmp_path)
        
        # Devolver los datos y la imagen procesada en base64
        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Eliminar el archivo temporal
        os.remove(tmp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
