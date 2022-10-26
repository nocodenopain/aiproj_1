from socket import *

if __name__ == "__main__":
    server_name = '127.0.0.1'
    server_port = 12000
    client_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        while True:
            msg = input('Input domain name:')
            msg += ","
            msg += input('Input query type: ')

            client_socket.sendto(msg.encode(), (server_name, server_port))
            modified_msg, server_addr = client_socket.recvfrom(2048)
            print(modified_msg.decode())

    except KeyboardInterrupt:
        client_socket.close()
        pass
