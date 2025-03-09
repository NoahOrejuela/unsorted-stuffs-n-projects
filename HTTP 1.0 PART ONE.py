# this is a basic server using HTTP 1.0 using tutorial by Joao Ventura with some modifications by Noah Orejuela

import socket

SERVER_HOST = "0.0.0.0"
SERVER_PORT = "8080"

server_socket = socket.socket(socket.AF_INET, socket.SOCKSTREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen (1)

print(f'Listening on port %s ...' % SERVER_PORT)
      
while True:
    client_connection, client_address = server_socket.accept()

    request = client_connection.recv(1024).decode()
    print(request)
    
    response = 'HTTP/1.0 200 OK\n\nHELLO WORLD'
    client_connection.sendall(response.encode())
    client_connection.close()

    server_socket.close()



