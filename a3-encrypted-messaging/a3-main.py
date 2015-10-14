__author__ = 'andrew'

# run with python 3.4.3

import argparse
from crypto import encrypt, decrypt, hash
from messenger import Messenger
import socket
from threading import Thread

MODE_CLIENT = 'c'
MODE_SERVER = 's'

MESSAGE_ENCODING = 'utf-8'

# this class holds the state of the program
class SessionManager:
    def __init__(self, port, ip_address=None):
        self.port = port
        self.ip_address = ip_address
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port

        self._messenger = self._get_messenger()

    def _get_messenger(self):
        # AF_INET = ipv4, SOCK_STREAM = tcp
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # assuming we can use the same "client socket" for both reading and writing
        if self.ip_address is None:
            # server init: listen to port for a connection
            s.bind(('', port))
            s.listen(1) # listen for only one connection

            session_socket, addr = s.accept()

            print("Accepted connection from ", addr)

            # todo: authenticate client, start communication loop with authenticated client
            # messenger = self.authenticate_as_server(client)

            m = Messenger(session_socket)
        else:
            # client init: specify ip address and port to try to ping
            s.connect((self.ip_address, self.port))

            # todo: authenticate server, start communication loop with authenticated server
            # messenger = self.authenticate_as_client(server)

            m = Messenger(s)

        return m

    def send(self, msg):
        # if self.is_secure():
        #     encrypt(msg)
        #     self._messenger.send(msg)
        # else:
        #     raise Exception("Session not securely initialized")
        self._messenger.send(msg)

    def recv(self):
        return self._messenger.recv()

    def is_secure(self):
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=[MODE_CLIENT, MODE_SERVER], help='Which mode to run the program in - "%s" for '
                        'client and "%s" for server'.format(MODE_CLIENT, MODE_SERVER))
    args = parser.parse_args()

    ## TEST: connect to test_server, testing Client messenger send/receive
    host_ip = '127.0.0.1'
    port = 12345

    if args.mode == MODE_CLIENT:
        session = SessionManager(port, host_ip)
        session.send("Alice, Ra")
        response = session.recv()
        print(response)
    elif args.mode == MODE_SERVER:
        session = SessionManager(port)
        while session is not None:  # the gui should be spamming this
            msg_in = session.recv()
            if msg_in is not None:
                session.send('hello {}'.format(msg_in))
    else:
        raise Exception("We should never get here! Unexpected cli mode arg %s".format(args.mode))
