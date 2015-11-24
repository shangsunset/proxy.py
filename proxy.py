import sys
import socket
import thread

PORT = 8001
MAX_CONNECTIONS = 3
BUFFER_SIZE = 4096


def start():

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', PORT))
        s.listen(MAX_CONNECTIONS)
        print 'server started on {}...'.format(PORT)

    except Exception:
        print 'unable to initialize socket...'

    while True:
        try:
            connection, address = s.accept()
            print 'connection {}'.format(address)
            data = connection.recv(BUFFER_SIZE)
            thread.start_new_thread(parse_request, (connection, address, data))
        except KeyboardInterrupt:
            s.close()
            print 'proxy server shutting down...'
            sys.exit()


def parse_request(connection, address, data):
    request_line = data.splitlines()[0]
    request_line = request_line.rstrip('\r\n')
    print data
    (request_method, path, request_version) = request_line.split()


if __name__ == '__main__':
    start()
