class CommunicationProtocol:
    def __init__(self, req_res, headers: dict, body):
        self.req_res = req_res
        self.headers = headers  # dictionary in which key is header_name, value is header_value as strings
        self.body = body  # should be in bytes

    def get_header_value(self, header_name):
        return self.headers.get(header_name)

    def set_header_value(self, header_name, header_value):
        self.headers[header_name] = header_value

    def to_bytes(self):
        params_list = self.get_params_list()

        params_length = 0
        for param in params_list:
            params_length += len(param)+1

        header_length = 6 + len(self.req_res) + params_length

        body_length = 0 if self.body is None else len(self.body)
        byte_arr = bytearray(header_length + body_length)

        byte_arr[0:3] = self.req_res.encode()
        byte_arr[3:4] = ":".encode()
        byte_arr[4:8] = header_length.to_bytes(4, 'little')
        byte_arr[8:9] = ":".encode()

        i = 9

        for param in params_list:
            byte_arr[i:i+len(param)+1] = f"{param}:".encode()
            i = i+len(param)+1

        if self.body is not None:
            byte_arr[i:] = self.body

        return byte_arr

    @staticmethod
    def from_bytes(byte_arr):
        req_res = byte_arr[0:3].decode()

        if req_res != "req" and req_res != "res":
            raise CommunicationProtocolException(byte_arr, "Message does not start with res or req")

        header_length = int.from_bytes(byte_arr[4:8], "little")

        i = 9
        params = []
        param = ""
        while i < header_length:
            if byte_arr[i] == ord(":"):
                params.append(param)
                param = ""
            else:
                param += chr(byte_arr[i])
            i += 1

        return CommunicationProtocol(req_res, CommunicationProtocol.params_list_to_dict(params), byte_arr[i:])

    @staticmethod
    def params_list_to_dict(params_list):
        param_dict = dict()
        for param in params_list:
            split_param = param.split("=")
            header_name = split_param[0]
            header_value = split_param[1]

            param_dict[header_name] = header_value

        return param_dict

    def get_params_list(self):
        params_list = []

        for header_name in self.headers.keys():
            param = f"{header_name}={self.headers[header_name]}"

            params_list.append(param)

        return params_list


class CommunicationProtocolException(Exception):
    def __init__(self, byte_arr, message):
        super.__init__(message)

        self.byte_arr = byte_arr
        self.message = message
