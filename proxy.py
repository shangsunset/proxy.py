import sys
import socket
import select
import threading

BUFFER_SIZE = 4096


class Proxy(object):

    def __init__(self, connection):

        self.client = connection
        self.client_buffer = ''
        self.target = None
        method, path, protocol = self.parse_request()
        self.handle_http_methods(method, path, protocol)

    def parse_request(self):
        """return a tuple of (method, path, protocol) from received message"""

        while '\n' not in self.client_buffer:
            self.client_buffer += self.client.recv(BUFFER_SIZE)
        (data, _, self.client_buffer) = self.client_buffer.partition('\n')
        print data
        return data.split()

    def handle_http_methods(self, method, path, protocol):

        path = path[len('http://'):]
        (host, _, path) = path.partition('/')
        path = '/{}'.format(path)
        self.connect_to_target(host)
        self.target.send('{method} {path} {protocol}\n{client_buffer}'.format(
            method=method,
            path=path,
            protocol=protocol,
            client_buffer=self.client_buffer))
        self.client_buffer = ''
        self.read_write()

    def connect_to_target(self, host):
        """connect to desired host server"""
        port = 80
        if ':' in host:
            (host, _, port) = host.partition(':')
        (socket_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(socket_family)
        self.target.connect(address)

    def read_write(self):
        """read data from client and send to host"""
        sockets = [self.client, self.target]
        try:
            while True:
                (ready_to_receive, _, error) = select.select(
                    sockets, [], sockets, 10)
                if error:
                    break
                elif ready_to_receive:
                    for receiver in ready_to_receive:
                        reply = receiver.recv(BUFFER_SIZE)
                        if not reply:
                            return
                        if receiver is self.target:
                            sender = self.client
                        else:
                            sender = self.target
                        sender.sendall(reply)
        finally:
            self.client.close()
            self.target.close()


def start_proxy_server():

    host = 'localhost'
    port = 8001

    try:
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening_socket.bind((host, port))
        listening_socket.listen(5)
        print 'proxy server started on {}...'.format(port)
    except Exception:
        print 'unable to initialize socket...'

    while True:
        try:
            connection, address = listening_socket.accept()
            print 'got connection from {}'.format(address)
            print connection
            threading.Thread(target=Proxy, args=(connection,)).run()
        except KeyboardInterrupt:
            listening_socket.close()
            print 'proxy server shutting down...'
            sys.exit()

if __name__ == '__main__':
    start_proxy_server()
