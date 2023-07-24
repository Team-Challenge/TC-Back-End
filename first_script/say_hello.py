import socket

def handle_request(request):
    response = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
    name = request.splitlines()[-1].decode().split('=')[-1]
    if name:
        response += f'{name} welcome to the test page Marketplase'
    else:
        response += "Hi, I don't know your name!"
    return response

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(1)

    print('Сервер запущений на http://localhost:8080/')

    while True:
        client_socket, client_address = server_socket.accept()
        request_data = client_socket.recv(1024)
        response_data = handle_request(request_data)
        client_socket.sendall(response_data.encode())
        client_socket.close()

if __name__ == '__main__':
    main()

