# Uncomment this to pass the first stage
import socket
from typing import Dict, List


class WrongRequestFormatError(Exception):
    def __init__(self, message: str = "Wrong request format"):
        """
        An error type to indicate wrong request format
        :type message: error msg
        """
        self.message: str = message
        super().__init__(self.message)


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    # stage 2
    client_socket, client_address = server_socket.accept()
    # client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")

    # stage 3
    req = client_socket.recv(4096).decode("utf-8")
    req_dict = parse_req(req)
    # process in stage 4
    if req_dict["Path"].startswith("/echo/"):
        stage_4(client_socket, req_dict)
    # process in stage 2 or 3
    else:
        stage_2_3(client_socket, req_dict)
        

def parse_req(req: str) -> Dict[str, str]:
    """
    parse request and return dict
    :param req:
    :return:
    """
    req_dict: Dict[str, str] = {}
    req_lines: List[str] = req.split("\r\n")

    # start line
    start_line: str = req_lines[0]
    try:
        req_dict["Method"], req_dict["Path"], req_dict["Protocol"] = start_line.split(" ")
    except ValueError:
        raise WrongRequestFormatError

    # content
    req_dict["Content"] = req_lines[-1]

    # header
    for line in req_lines[1:-1]:
        if len(line) < 1:
            continue
        try:
            k, v = line.split(":")
        except ValueError:
            raise WrongRequestFormatError
        req_dict[k.strip()] = v.strip()

    return req_dict


def stage_2_3(client_socket: socket, req_dict: Dict[str, str]):
    if req_dict["Path"] == "/":
        client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        client_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


def stage_4(client_socket: socket, req_dict: Dict[str, str]):
    res_body = req_dict["Path"][len("/echo/"):]
    client_socket.send(
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: "
        + str(len(res_body)).encode()
        + b"\r\n\r\n"
        + res_body.encode()
    )


if __name__ == "__main__":
    main()
