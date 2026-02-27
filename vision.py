import os
import sqlite3
import cv2
import time
from datetime import datetime

# --- CONFIGURACIÓN ---
CARPETA_CAPTURA = "static/capturas"
if not os.path.exists(CARPETA_CAPTURA):
    os.makedirs(CARPETA_CAPTURA)

def guardar_en_db(nombre_archivo):
    try:
        conn = sqlite3.connect('vigilancia.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO capturas (fecha, archivo) VALUES (?, ?)", 
                       (datetime.now().isoformat(), nombre_archivo))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error en BD: {e}")

def obtener_frame_hibrido():
    # Usamos el comando oficial para capturar una imagen temporal
    temp_file = "temp_capture.jpg"
    # --immediate: sin preview, --nopreview: no abre ventana, --width/height: para velocidad
    comando = f"rpicam-still -o {temp_file} --immediate --nopreview --width 640 --height 480 -n"
    os.system(comando)
    
    frame = cv2.imread(temp_file)
    if frame is None:
        return False, None, None
    
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (21, 21), 0)
    return True, gris, frame

print("🛰️ Iniciando Sistema de Vigilancia Híbrido...")

# 1. Tomamos la primera imagen de referencia
exito, frame_anterior, _ = obtener_frame_hibrido()
if not exito:
    print("❌ Error: No se pudo obtener imagen de la cámara. Revisa el cable flex.")
    exit()

print("✅ Cámara lista. Buscando movimiento...")

try:
    while True:
        # 2. Capturar frame actual
        ret, gris, frame_color = obtener_frame_hibrido()
        if not ret:
            continue

        # 3. Calcular diferencia (Movimiento)
        resta = cv2.absdiff(frame_anterior, gris)
        umbral = cv2.threshold(resta, 30, 255, cv2.THRESH_BINARY)[1]
        umbral = cv2.dilate(umbral, None, iterations=2)

        # 4. Detectar si el cambio es importante
        if cv2.countNonZero(umbral) > 10000: 
            ahora = datetime.now()
            nombre_foto = ahora.strftime("foto_%Y%m%d_%H%M%S.jpg")
            ruta_completa = os.path.join(CARPETA_CAPTURA, nombre_foto)
            
            # Guardamos la imagen real
            cv2.imwrite(ruta_completa, frame_color)
            guardar_en_db(nombre_foto)
            
            print(f"📸 ¡MOVIMIENTO! Guardada: {nombre_foto}")
            
            # Pausa para no saturar y actualizar referencia
            time.sleep(2)
            _, frame_anterior, _ = obtener_frame_hibrido()
        
        # Pequeña pausa para que la CPU respire
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 Vigilante desactivado.")