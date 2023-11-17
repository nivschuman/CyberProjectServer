from Server import CommunicationProtocolServer
import pyodbc
import json
import base64
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


class PasswordManagerServer:
    def __init__(self, host, port, db_connection_string):
        self.server = CommunicationProtocolServer(host, port)
        self.db_connection = pyodbc.connect(db_connection_string)
        self.db_cursor = self.db_connection.cursor()

        self.server.handle_method("create_user", self.create_user)

    def start_server(self):
        self.server.serve_forever()

    def create_user(self, req, res, session):
        body_str = req.body.decode()
        body_json = json.loads(body_str)

        public_key_bytes = base64.b64decode(body_json["publicKey"])

        res.set_header_value("Content-Length", 0)

    def login_request(self, req, res, session):
        pass

    def login_test(self, req, res, session):
        pass

    def get_password(self, req, res, session):
        pass

    def set_password(self, req, res, session):
        pass

    def delete_password(self, req, res, session):
        pass
