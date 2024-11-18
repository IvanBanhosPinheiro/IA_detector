from flask import Flask, request
import os
from datetime import datetime

app = Flask(__name__)

# Directorio para guardar las capturas de pantalla y alertas recibidas
#ruta_guardado_capturas = os.path.join(os.path.dirname(__file__), 'screenshots_recibidas')
ruta_guardado_capturas = os.path.join(os.path.dirname(__file__), 'screenshots_recibidas')
if not os.path.exists(ruta_guardado_capturas):
    os.makedirs(ruta_guardado_capturas)

# Ruta para el archivo de palabras clave
#ruta_keywords = os.path.abspath(os.path.join(os.path.dirname(__file__), 'keywords.txt'))
ruta_keywords = os.path.join(os.getcwd(), 'keywords.txt')


# Endpoint para subir capturas de pantalla y alertas
@app.route('/uploads', methods=['POST'])
def upload():
    try:
        # Obtener datos del formulario
        cliente_id = request.form['cliente_id']
        timestamp = request.form['timestamp']
        mensaje = request.form['mensaje']

        # Crear directorio para el cliente si no existe
        ruta_cliente = os.path.join(ruta_guardado_capturas, cliente_id)
        if not os.path.exists(ruta_cliente):
            os.makedirs(ruta_cliente)

        # Guardar captura de pantalla
        if 'screenshot' in request.files:
            screenshot = request.files['screenshot']
            nombre_archivo_captura = f"recibido_{timestamp}.png"
            ruta_archivo_captura = os.path.join(ruta_cliente, nombre_archivo_captura)
            screenshot.save(ruta_archivo_captura)
            print(f"[{datetime.now()}] Imagen guardada en: {ruta_archivo_captura}")

        # Guardar archivo de alerta
        if 'data' in request.files:
            alerta = request.files['data']
            nombre_archivo_alerta = f"alerta_{timestamp}.txt"
            ruta_archivo_alerta = os.path.join(ruta_cliente, nombre_archivo_alerta)
            alerta.save(ruta_archivo_alerta)
            print(f"[{datetime.now()}] Alerta guardada en: {ruta_archivo_alerta}")

        return 'OK', 200
    except Exception as e:
        print(f"[{datetime.now()}] Error al procesar la solicitud: {str(e)}")
        return 'Error', 500

# Endpoint para descargar el archivo de palabras clave
@app.route('/keywords', methods=['GET'])
def keywords():
    try:
        if os.path.exists(ruta_keywords):
            with open(ruta_keywords, 'r', encoding='utf-8') as file:
                print(f"[{datetime.now()}] Archivo 'keywords.txt' encontrado y enviado.")
                return file.read(), 200
        else:
            print(f"[{datetime.now()}] Archivo 'keywords.txt' no encontrado en la ruta: {ruta_keywords}")
            return 'No se encontró el archivo de palabras clave', 404
    except Exception as e:
        print(f"[{datetime.now()}] Error al servir el archivo de palabras clave: {str(e)}")
        return 'Error', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
