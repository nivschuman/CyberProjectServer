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
        user_name = body_json["userName"]

        # todo remove sql injection
        # check if there already exists a user with given username
        public_key_str = f"0x{public_key_bytes.hex()}"
        self.db_cursor.execute(f"SELECT UserName, PublicKey From Users WHERE UserName=\'{user_name}\'")
        user_with_same_username = self.db_cursor.fetchall() is not None
        self.db_cursor.execute(f"SELECT UserName, PublicKey From Users WHERE PublicKey=\'{public_key_str}\'")
        user_with_same_public_key = self.db_cursor.fetchall() is not None

        if user_with_same_username:
            res.body = "User with this username already exists, choose a different username"
        elif user_with_same_public_key:
            res.body = "User with this public key already exists, choose a different public key"
        else:
            self.db_cursor.execute(f"INSERT INTO Users (UserName, PublicKey) VALUES (\'{user_name}\', \'{public_key_str}\')")
            res.body = "Successfully created user"

        res.set_header_value("Content-Length", len(res.body))
        res.set_header_value("Method", "create_user")
        res.set_header_value("Content-Type", "ascii string")

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
