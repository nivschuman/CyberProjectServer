from Server import CommunicationProtocolServer


class PasswordManagerServer:
    def __init__(self, host, port):
        self.server = CommunicationProtocolServer(host, port)

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
