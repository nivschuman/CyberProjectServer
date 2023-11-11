from Server import CommunicationProtocolServer
import pyodbc


class PasswordManagerServer:
    def __init__(self, host, port, db_connection_string):
        self.server = CommunicationProtocolServer(host, port)
        self.db_connection = pyodbc.connect(db_connection_string)
        self.db_cursor = self.db_connection.cursor()

    def start_server(self):
        self.server.serve_forever()

    def create_user(self, req, res, session):
        pass

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
