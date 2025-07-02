from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
import os
import threading
from flask import Flask, render_template_string, request
from OpenSSL import cryptok

app = Flask(__name__)

@app.route('/Templates/index.html', methods=['GET', 'POST'])
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