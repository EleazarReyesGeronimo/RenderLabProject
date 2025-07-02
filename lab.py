from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
import os
from OpenSSL import crypto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "ftp_uploads")
CERTS_DIR = os.path.join(BASE_DIR, "ftp_certs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CERTS_DIR, exist_ok=True)


#Certificados SSL para Entorno de pruebas

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