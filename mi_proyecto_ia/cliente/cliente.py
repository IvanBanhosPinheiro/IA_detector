import os
import configparser
import time
import pyautogui
import requests
from datetime import datetime
import pygetwindow as gw
from io import BytesIO
import pytesseract

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Configuración
config = configparser.ConfigParser()
config_path = os.path.join(os.getcwd(), 'config.ini')
#config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
config.read(config_path)

# Configuración del cliente
url_servidor = config['Cliente']['url_servidor']

# URL para descargar el archivo de palabras clave del servidor
url_keywords = f"{url_servidor}/keywords"

# Generar un identificador único para cada cliente usando el nombre del equipo
cliente_id = os.environ.get('COMPUTERNAME', 'unknown_client')

# Variable para almacenar la ventana activa anterior
ventana_activa_anterior = None

# Función para descargar el archivo de palabras clave del servidor
def descargar_keywords():
    try:
        print(f"[{datetime.now()}] Intentando descargar las palabras clave desde: {url_keywords}")
        response = requests.get(url_keywords)
        if response.status_code == 200:
            with open('keywords.txt', 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"[{datetime.now()}] Archivo de palabras clave descargado exitosamente.")
        else:
            print(f"[{datetime.now()}] Error al descargar el archivo de palabras clave: {response.status_code}")
            print(f"[{datetime.now()}] Respuesta del servidor: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] Error al descargar el archivo de palabras clave: {str(e)}")


# Función para tomar captura de pantalla
def tomar_captura_pantalla():
    # Tomar captura de pantalla
    screenshot = pyautogui.screenshot()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Guardar la captura en un objeto BytesIO en lugar de guardarla en disco
    screenshot_bytes_io = BytesIO()
    screenshot.save(screenshot_bytes_io, format='PNG')
    screenshot_bytes_io.seek(0)
    return screenshot_bytes_io, screenshot, timestamp

# Función para enviar una alerta al servidor
def enviar_alerta_servidor(screenshot_bytes_io, txt_data, timestamp, mensaje):
    try:
        files = {
            'screenshot': ('screenshot.png', screenshot_bytes_io, 'image/png'),
            'data': ('alerta.txt', txt_data, 'text/plain')
        }
        data = {"cliente_id": cliente_id, "timestamp": timestamp, "mensaje": mensaje}
        response = requests.post(f"{url_servidor}/uploads", files=files, data=data)
        if response.status_code == 200:
            print(f"[{datetime.now()}] Alerta enviada exitosamente: {mensaje}")
        else:
            print(f"[{datetime.now()}] Error al enviar la alerta: {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] Error al enviar la alerta: {str(e)}")

# Función para realizar OCR en la captura de pantalla y detectar uso de IA
def detectar_uso_ia_pantalla():
    screenshot_bytes_io, screenshot, timestamp = tomar_captura_pantalla()
    # Extraer texto usando OCR
    text = pytesseract.image_to_string(screenshot)
    
    # Cargar palabras clave del archivo
    with open('keywords.txt', 'r', encoding='utf-8') as file:
        keywords = [line.strip().lower() for line in file]
    
    # Buscar palabras clave relacionadas con IA
    if any(keyword in text.lower() for keyword in keywords):
        print(f"[{datetime.now()}] Posible uso de IA detectado en la pantalla: {text[:50]}...")
        txt_data = f"Fecha: {timestamp}\nCliente: {cliente_id}\nVentana: {ventana_activa_anterior}\nTexto detectado: {text}...\n"
        enviar_alerta_servidor(screenshot_bytes_io, txt_data, timestamp, "Posible uso de IA detectado en la pantalla")

# Bucle principal para monitorear el cambio de ventana activa
if __name__ == "__main__":
    # Descargar archivo de palabras clave del servidor al iniciar
    descargar_keywords()

    while True:
        try:
            # Obtener la ventana activa actual
            ventana_activa = gw.getActiveWindow()
            nombre_ventana = ventana_activa.title if ventana_activa else "Unknown"

            # Verificar si la ventana activa ha cambiado
            if ventana_activa_anterior != nombre_ventana:
                ventana_activa_anterior = nombre_ventana
                print(f"[{datetime.now()}] Cambio de ventana detectado: {nombre_ventana}")

                # Capturar pantalla y verificar uso de IA mediante OCR
                detectar_uso_ia_pantalla()

            # Esperar un corto intervalo antes de verificar nuevamente
            time.sleep(1)
        except Exception as e:
            print(f"[{datetime.now()}] Error en el monitoreo de ventana activa: {str(e)}")
