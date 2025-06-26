from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.servers import FTPServer
from OpenSSL import crypto
import os

#==============================================================
# Configuration 
#==============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'server_uploads')
CERTS_DIR = os.path.join(BASE_DIR, 'server_certs')

#Crear Directorios necesarios
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CERTS_DIR, exist_ok=True)

#==============================================================
# SSL Certificate Generation
#==============================================================
def generate_self_signed_cert():
    cert_file = os.path.join(CERTS_DIR, 'cert.pem')
    key_file = os.path.join(CERTS_DIR, 'key.pem')

    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("SSL certificate already exists.")
        return cert_file, key_file

    #crear clave privada
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    #crear certificado autofirmado
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # 10 years
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    #guardar certificado
    with open(cert_file, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    #guardar clave privada
    with open(key_file, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    return cert_file, key_file
