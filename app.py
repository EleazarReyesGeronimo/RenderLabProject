import os
import threading
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import config
from ftps_server import run_ftps_server

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Asegurarse de que los directorios necesarios existan
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.CERTS_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    message_class = None
    
    if request.method == 'POST':
        # 1. Validación de la entrada del archivo
        if 'file' not in request.files:
            message = "Error: No se encuentra el campo del archivo en el formulario."
            message_class = "error"
        else:
            file = request.files['file']
            if file.filename == '':
                message = "Error: No se selecciono ningun archivo."
                message_class = "error"
            elif not file.filename.endswith('.blend'):
                message = "Error: Por favor, sube un archivo con extension .blend"
                message_class = "error"
            else:
                try:
                    # 2. Sanitización del nombre del archivo
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(config.UPLOAD_DIR, filename)
                    file.save(save_path)
                    
                    # 3. Recopilar datos de configuración del render
                    render_settings = {
                        'file_path': save_path,
                        'engine': request.form.get('render_engine'),
                        'resolution_x': request.form.get('resolution_x'),
                        'resolution_y': request.form.get('resolution_y'),
                        'frame_start': request.form.get('frame_start'),
                        'frame_end': request.form.get('frame_end')
                    }
                    
                    # Aquí es donde integrarías la lógica de la cola de renderizado.
                    # Por ahora, solo imprimimos la configuración para verificar.
                    print("--> Nueva tarea de render agregada a la cola:")
                    print(render_settings)

                    message = f"Exito! El archivo '{filename}' se ha subido y la tarea de render ha sido agregada a la cola."
                    message_class = "success"

                except Exception as e:
                    message = f"Error al procesar el archivo: {str(e)}"
                    message_class = "error"

    # Siempre listar los archivos actuales en el directorio de subida
    files = os.listdir(config.UPLOAD_DIR) if os.path.exists(config.UPLOAD_DIR) else []
    
    return render_template(
        'index.html',
        message=message,
        message_class=message_class,
        files=files,
        ftp_port=config.FTP_PORT,
        ftp_user=config.FTP_USER,
        ftp_pass=config.FTP_PASS
    )

if __name__ == "__main__":
    # Iniciar el servidor FTPS en un hilo separado para no bloquear la app web
    ftp_thread = threading.Thread(target=run_ftps_server, daemon=True)
    ftp_thread.start()
    
    print(f"[*] Interfaz web disponible en http://{config.WEB_HOST}:{config.WEB_PORT}")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=True)