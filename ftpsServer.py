# -*- coding: utf-8 -*-
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
import os
import threading
from flask import Flask, render_template_string, request
from OpenSSL import crypto

# Configuración inicial
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "ftp_uploads")
CERTS_DIR = os.path.join(BASE_DIR, "ftp_certs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CERTS_DIR, exist_ok=True)

# Generar certificados TLS automáticos
def generate_self_signed_cert():
    cert_file = os.path.join(CERTS_DIR, "cert.pem")
    key_file = os.path.join(CERTS_DIR, "key.pem")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    return cert_file, key_file

# Servidor FTPS
def run_ftps_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user(
        "testuser",
        "testpass",
        UPLOAD_DIR,
        perm="elradfmw"
    )
    
    handler = TLS_FTPHandler
    handler.certfile, handler.keyfile = generate_self_signed_cert()
    handler.authorizer = authorizer
    handler.tls_control_required = True
    handler.tls_data_required = True
    
    # Mensaje en inglés para evitar problemas de codificación
    handler.banner = "Welcome to the RenderFarm test FTPS server"
    
    server = FTPServer(("0.0.0.0", 2121), handler)
    print(f"[*] FTPS server running on port 2121. Upload dir: {UPLOAD_DIR}")
    server.serve_forever()

# Interfaz web simplificada
app = Flask(__name__)

# Template en inglés para evitar problemas de codificación
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FTPS Test - RenderFarm</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; }
        .error { background: #f8d7da; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FTPS Upload Test</h1>
        <p>Server: <code>localhost:2121</code></p>
        <p>User: testuser | Password: testpass</p>
        
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload File</button>
        </form>
        
        {% if message %}
        <div class="status {{ message_class }}">{{ message }}</div>
        {% endif %}
        
        <div>
            <h3>Files on server:</h3>
            {% for file in files %}
            <div>{{ file }}</div>
            {% else %}
            <p>No files uploaded yet</p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    message_class = None
    files = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
    
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename:
            try:
                file.save(os.path.join(UPLOAD_DIR, file.filename))
                message = f"File '{file.filename}' uploaded successfully!"
                message_class = "success"
                files = os.listdir(UPLOAD_DIR)
            except Exception as e:
                message = f"Error: {str(e)}"
                message_class = "error"
        else:
            message = "Please select a file"
            message_class = "error"
    
    return render_template_string(
        HTML_TEMPLATE,
        message=message,
        message_class=message_class,
        files=files
    )

if __name__ == "__main__":
    ftp_thread = threading.Thread(target=run_ftps_server, daemon=True)
    ftp_thread.start()
    
    print("[*] Web interface available at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)