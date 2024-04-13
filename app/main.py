import argparse
import socket
from typing import Dict, List
import asyncio
import sys
import os


class WrongRequestFormatError(Exception):
    def __init__(self, message: str = "Wrong request format"):
        """
        An error type to indicate wrong request format
        :type message: error msg
        """
        self.message: str = message
        super().__init__(self.message)


def main(args):
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server = Server(directory=args.directory)
    asyncio.run(server.start())


class Server:
    def __init__(
        self, host: str = "localhost", port: int = 4221, concurrency: int = 128, directory: str = None
    ):
        self._concurrency: int = concurrency
        self._server_socket: socket.socket = socket.create_server((host, port), reuse_port=True)
        self._directory = directory

    async def start(self):
        loop = asyncio.get_event_loop()
        [loop.create_task(self.worker()) for _ in range(self._concurrency)]
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            sys.exit()

    async def worker(self):
        while True:
            await asyncio.to_thread(self.handler)
    
    def handler(self):
        client_socket, client_address = self._server_socket.accept()
        req = client_socket.recv(4096).decode("utf-8")
        self._process_req(client_socket, client_address, req)

    def _process_req(self, client_socket: socket.socket, client_address, req: str):
        req_dict: dict[str, str] = self.parse_req(req)

        # process in stage 4
        if req_dict["Path"].startswith("/echo/"):
            self._stage_4(client_socket, req_dict)
        # process in stage 5
        elif req_dict["Path"].startswith("/user-agent"):
            self._stage_5(client_socket, req_dict)
        # process in stage 7
        elif req_dict["Path"].startswith("/file"):
            self._stage_7(client_socket, req_dict)
        # process in stage 2 or 3
        else:
            self._stage_2_3(client_socket, req_dict)
        

    @staticmethod
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
            req_dict["Method"], req_dict["Path"], req_dict["Protocol"] = (
                start_line.split(" ")
            )
        except ValueError:
            raise WrongRequestFormatError

        # header
        for line in req_lines[1:]:
            if len(line) < 1:
                continue
            try:
                sep_idx = line.index(":")
            except ValueError:
                raise WrongRequestFormatError
            else:
                req_dict[line[:sep_idx]] = line[sep_idx + 2 :]

        return req_dict

    @staticmethod
    def _stage_2_3(client_socket: socket.socket, req_dict: Dict[str, str]):
        if req_dict["Path"] == "/":
            client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
        else:
            client_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")

    @staticmethod
    def _stage_4(client_socket: socket.socket, req_dict: Dict[str, str]):
        res_body = req_dict["Path"][len("/echo/") :]
        client_socket.send(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: "
            + str(len(res_body)).encode()
            + b"\r\n\r\n"
            + res_body.encode()
        )

    @staticmethod
    def _stage_5(client_socket: socket.socket, req_dict: Dict[str, str]):
        res_body = req_dict["User-Agent"]
        client_socket.send(
            b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: "
            + str(len(res_body)).encode()
            + b"\r\n\r\n"
            + res_body.encode()
        )

    @staticmethod
    def _stage_7(self, client_socket: socket.socket, req_dict: Dict[str, str]):
        file_name = req_dict["Path"][len("/file/"):]
        file_path = os.path.join(self._directory, file_name)
        if not os.path.exists(file_path):
            client_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        with open(file_path, "rb") as f:
            file_content = f.read()
        client_socket.send(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: "
            + str(len(file_content)).encode()
            + b"\r\n\r\n"
            + file_content
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str)

    args = parser.parse_args()
    main(args)
