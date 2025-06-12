import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.servers import FTPServer

auth = DummyAuthorizer()
def run_server():
    # Define a user with full permissions
    auth.add_user("RendAdmin", "C6mEyc:qcy", os.getcwd(), perm="elradfmwMT")
    # Define an anonymous user with read-only permissions
    auth.add_anonymous(os.getcwd(), perm="elr")

    handler = TLS_FTPHandler
    handler.authorizer = auth

    server = FTPServer(("0.0.0.0", 21), handler)  
    server.max_cons = 25

    handler.banner = "A user is sending a project"

    handler.masquerade_address = '151.25.42.11'
    handler.passive_ports = range(60000, 65535)

    # start ftp server
    server.serve_forever()