# config.py
import os

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Configuración de Directorios ---
UPLOAD_DIR = os.path.join(BASE_DIR, "ftp_uploads")
CERTS_DIR = os.path.join(BASE_DIR, "ftp_certs")

# --- Configuración del Servidor FTPS ---
FTP_HOST = "0.0.0.0"
FTP_PORT = 2121
FTP_USER = "testuser"
FTP_PASS = "testpass"

# --- Configuración de la Aplicación Web (Flask) ---
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000