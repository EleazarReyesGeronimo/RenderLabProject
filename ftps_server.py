# ftps_server.py
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from OpenSSL import crypto
import config  # Importamos nuestra configuración

def generate_self_signed_cert():
    """Genera certificados TLS autofirmados si no existen."""
    cert_file = os.path.join(config.CERTS_DIR, "cert.pem")
    key_file = os.path.join(config.CERTS_DIR, "key.pem")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file
    
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    return cert_file, key_file

def run_ftps_server():
    """Inicializa y corre el servidor FTPS."""
    authorizer = DummyAuthorizer()
    authorizer.add_user(
        config.FTP_USER,
        config.FTP_PASS,
        config.UPLOAD_DIR,
        perm="elradfmw"  # Permisos completos: Listar, Subir, Leer, etc.
    )
    
    handler = TLS_FTPHandler
    handler.certfile, handler.keyfile = generate_self_signed_cert()
    handler.authorizer = authorizer
    handler.tls_control_required = True
    handler.tls_data_required = True
    handler.banner = "Welcome to the TlacuaTech RenderFarm FTPS server"
    
    server = FTPServer((config.FTP_HOST, config.FTP_PORT), handler)
    print(f"[*] Servidor FTPS corriendo en el puerto {config.FTP_PORT}. Directorio de subida: {config.UPLOAD_DIR}")
    server.serve_forever()