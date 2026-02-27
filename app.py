from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Ruta donde el script vision.py guarda las fotos
CARPETA_FOTOS = os.path.join('static', 'capturas')

@app.route('/')
def index():
    # Comprobamos si la carpeta existe para que no de error
    if not os.path.exists(CARPETA_FOTOS):
        os.makedirs(CARPETA_FOTOS)
    
    # Listamos los archivos .jpg y los ordenamos (el más reciente primero)
    fotos = [f for f in os.listdir(CARPETA_FOTOS) if f.endswith('.jpg')]
    fotos.sort(reverse=True) 
    
    return render_template('index.html', fotos=fotos)

if __name__ == '__main__':
    # host='0.0.0.0' es fundamental para que lo veas desde tu PC
    app.run(host='0.0.0.0', port=5000, debug=True)