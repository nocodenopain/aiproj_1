from socket import *
import dns.resolver
import dns.rdatatype

if __name__ == "__main__":

    server_port = 12000
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('', server_port))
    print("The server is ready to receive")
    try:
        while True:
            message, client_addr = server_socket.recvfrom(2048)  # ?
            message = message.decode()
            queries = message.split(',')
            modified_msg = ""
            a = dns.resolver.query(queries[0], queries[1])
            for i in a.response.answer:
                modified_msg += dns.rdatatype.to_text(i.rdtype)
                modified_msg += "\n"
                for j in i.items:
                    modified_msg += str(j)
                    modified_msg += "\n"
            server_socket.sendto(modified_msg.encode(), client_addr)
    except KeyboardInterrupt:
        pass
