# Uncomment this to pass the first stage
import socket
from typing import Dict, List
from threading import Thread
import asyncio

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

    server = Server()
    # server.start()
    asyncio.run(server.a_start())


class Server:
    def __init__(
        self, host: str = "localhost", port: int = 4221, concurrency: int = 8
    ):
        self._concurrency = concurrency
        self._server_socket = socket.create_server((host, port), reuse_port=True)

    def start(self):
        threads = []
        for _ in range(self._concurrency):
            thread = Thread(target=self.worker)
            threads.append(thread)
            thread.start()
        [thread.join() for thread in threads]
        self._server_socket.close()

    async def a_start(self):
        await asyncio.wait_for(asyncio.gather(*[self.a_worker() for _ in range(self._concurrency)]), timeout=120)
        self._server_socket.close()

    def worker(self):
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


if __name__ == "__main__":
    main()
