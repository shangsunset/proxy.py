import sys
import errno
import socket
import thread

PORT = 8001
MAX_CONNECTIONS = 3
BUFFER_SIZE = 4096


def start():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', PORT))
        s.listen(MAX_CONNECTIONS)
        print 'proxy server started on {}...'.format(PORT)

    except Exception:
        print 'unable to initialize socket...'

    while True:
        try:
            connection, address = s.accept()
            print 'connection {}'.format(address)
            data = connection.recv(BUFFER_SIZE)
            if data:
                thread.start_new_thread(
                    parse_request, (connection, address, data)
                )
        except KeyboardInterrupt:
            s.close()
            print 'proxy server shutting down...'
            sys.exit()


def parse_request(connection, address, data):
    request_line = data.splitlines()
    request_line = request_line[0]
    request_line = request_line.rstrip('\r\n')
    (request_method, path, request_version) = request_line.split()
    path = path[len('http://'):]
    host = path[:path.find('/')]

    proxy_server(connection, address, data, host)


def proxy_server(connection, address, data, host, port=80):
    print 'host: {}'.format(host)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(data)

    while True:
        reply = s.recv(BUFFER_SIZE)
        try:
            connection.send(reply)
        except socket.error as e:
            if e.errno == errno.EPIPE:
                print "Detected disconnection"
    s.close()
    connection.close()


if __name__ == '__main__':
    start()
