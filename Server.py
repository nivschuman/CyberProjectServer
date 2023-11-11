import socket
import re
import string
from random import randint
from threading import Thread
from threading import Lock
from CommunicationProtocol import CommunicationProtocol, CommunicationProtocolException
from Session import Session


# TCP Socket Server which binds to host and port given
# Each client connection is handled in different thread
# Client connections go through different handler functions
# handler functions are called in added order. Result of one handler goes to the next.
class Server:
    def __init__(self, host, port):
        self.port = port
        self.host = host

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.handlers = []  # each handler is a function which takes client_socket, client_address, prev_result

    # add handler function to deal with client connection
    def add_handler(self, handler):
        self.handlers.append(handler)

    # remove handler function
    def remove_handler(self, handler):
        self.handlers.remove(handler)

    # receive message from client. Default receives 1024 bytes from client socket.
    def receive_message(self, client_socket, client_address):
        return client_socket.recv(1024)

    # what to do on client closing. Default just closes socket.
    def close_client(self, client_socket, client_address):
        client_socket.close()

    # handle connection from client. message goes through all handler functions
    def handle_client(self, client_socket, client_address):
        message = self.receive_message(client_socket, client_address)

        prev_result = None
        for handler in self.handlers:
            prev_result = handler(client_socket, client_address, prev_result)

        self.close_client(client_socket, client_address)

    # turn server on to forever serve
    def serve_forever(self):
        self.server_socket.bind((self.host, self.port))
        while True:
            self.server_socket.listen()
            client_socket, client_address = self.server_socket.accept()
            client_thread = Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()


# Server with Storing Session capabilities
# todo session cleanup, delete unused sessions
class SessionServer(Server):
    def __init__(self, host, port, session_token_length):
        super().__init__(host, port)

        self.sessions = dict()  # key is session token, value is session object
        self.session_token_length = session_token_length

    # generate unique token for new session
    def generate_session_token(self, length):
        characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        token = ""

        while token not in self.sessions:
            token = ""
            for i in range(length):
                token += characters[randint(0, len(characters)-1)]

        return token

    # create a session and return its token
    def create_session(self):
        token = self.generate_session_token(self.session_token_length)
        self.sessions[token] = Session()

        return token

    # get session associated with token
    def get_session(self, token):
        return self.sessions.get(token)

    # close session with token
    def close_session(self, token):
        self.sessions.pop(token)


# Server which works with the Communication Protocol
class CommunicationProtocolServer(SessionServer):
    def __init__(self, host, port):
        super().__init__(host, port, 8)

        self.handlers.append(self.parse_message)
        self.handlers.append(self.session_generator)
        self.handlers.append(self.method_handler)

        self.method_handlers = dict()  # key is method name, value is function to handle method

    # if request with Method=method is received, method_function will be called
    # method_function gets req, res and session object relevant to req session token
    # res is changed in method_function
    def handle_method(self, method, method_function):
        self.method_handlers[method] = method_function

    def receive_message(self, client_socket, client_address):
        req_res = client_socket.recv(3)

        if req_res != "req".encode() and req_res != "res".encode():
            data = client_socket.recv(1)
            while data != "":
                req_res += data
                data = client_socket.recv(1)
            raise CommunicationProtocolException(req_res, "Message does not start with res or req")

        # receive headers
        header_length_bytes = client_socket.recv(6)[1:5]
        header_length = int.from_bytes(header_length_bytes, "little")
        headers = client_socket.recv(header_length-9)

        # get Content-Length header to find length of body
        headers_list = headers.decode().split[":"]
        regular_expression = re.compile(r"Content-Length=[0-9]+")
        content_length_header = list(filter(regular_expression.match, headers_list))[0]
        content_length = content_length_header.split("=")[1]

        # receive body
        body = client_socket.recv(content_length)

        # return complete byte message
        return req_res + header_length + headers + body

    # turn byte message into CommunicationProtocol object for next handler
    def parse_message(self, client_socket, client_address, message):
        return CommunicationProtocol.from_bytes(message)

    def session_generator(self, client_socket, client_address, req):
        session_value = req.get_header_value("Session")

        # create new session for use with client
        if session_value == "*":
            session_token = self.create_session()
            req.set_header_value("Session", session_token)

        return req

    # creates response to specific method and sends it to client
    def method_handler(self, client_socket, client_address, req):
        # response object. Changed in method handler.
        res = CommunicationProtocol("res", dict(), None)

        # get session object using req session token
        session = None
        session_token = req.get_header_value("Session")
        if session_token[0] == "~":
            session_token = session_token[1:]
        if session_token != "-":
            session = self.get_session(session_token)

        # set session token in response
        res.set_header_value("Session", session_token)

        # call handler to method
        method = req.get_header_value("Method")
        self.method_handlers[method](req, res, session)

        # send response to client
        client_socket.send(res.to_bytes())

        # close session if requested to
        if req.get_header_value("Session")[0] == "~":
            self.close_session(session_token)

        # return req and res for possible extra handles
        return req, res
