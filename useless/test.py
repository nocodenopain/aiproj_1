# import asyncio
#
#
# async def dispatch(reader, writer):
#     while True:
#         data = await reader.readline()
#         message = data.decode().split(' ')
#         print(data)
#         if data == b'\r\n':
#             break
#     writer.writelines([
#         b'HTTP/1.0 200 OK\r\n',
#         b'Content-Type:text/html;charset=utf8\r\n',
#         b'Connection:close\r\n',
#         b'\r\n',
#         b'<html><body>Hello World!<body></html>\r\n',
#         b'\r\n'
#     ])
#     await writer.drain()
#     writer.close()
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
#     server = loop.run_until_complete(coro)
#     # Serve requests until Ctrl+C is pressed
#     print('Serving on {}'.format(server.sockets[0].getsockname()))
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#     # Close the server
#     server.close()
#     loop.run_until_complete(server.wait_closed())
#     loop.close()


import socket
import threading


class Echo(threading.Thread):
    def __init__(self, conn, address):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address

    def run(self):
        while True:
            data = self.conn.recv(2048)
            if data and data != b'exit\r\n':
                self.conn.send(data)
                print('{} sent: {}'.format(self.address, data))
            else:
                self.conn.close()
                return


def echo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 5555))
    sock.listen(10)
    while True:
        conn, address = sock.accept()
        Echo(conn, address).start()


if __name__ == "__main__":
    try:
        echo()
    except KeyboardInterrupt:
        pass


