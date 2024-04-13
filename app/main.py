# Uncomment this to pass the first stage
import socket


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
    req_lines = req.split("\r\n")
    req_start_line = req_lines[0]
    req_path = req_start_line.split(" ")[1]
    if req_path.startswith("/echo/"):
        # process in stage 4
        pass
    elif req_path == "/":
        client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")
    else:
        client_socket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")

    # stage 4
    res_body = req_path[len("/echo/"):]
    client_socket.send(
        b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\n\r\n"
        + res_body.encode()
    )


if __name__ == "__main__":
    main()
