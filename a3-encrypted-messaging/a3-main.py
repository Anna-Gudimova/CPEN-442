__author__ = 'andrew'

# run with python 3.4.3

import argparse
from crypto import encrypt, decrypt, generate_keystream, generate_init_vector
from messenger import Messenger
import socket
from threading import Thread

MODE_CLIENT = 'c'
MODE_SERVER = 's'

MESSAGE_ENCODING = 'utf-8'
## TODO: Figure out ideal place for following lines (coming from GUI)
## IV generated for each new msg..decrypt requires same IV
key = "something Ildar will write"
keystream = generate_keystream(key)
iv = generate_init_vector()

# this class holds the state of the program
class SessionManager:
    def __init__(self, port, ip_address=None):
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port
        self.port = port
        self.ip_address = ip_address

        self._messenger = None
        self.reset_messenger()

    def reset_messenger(self):
        if self._messenger is not None:
            self._messenger.close()
            self._messenger = None

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

            self._messenger = Messenger(session_socket)
        else:
            # client init: specify ip address and port to try to ping
            s.connect((self.ip_address, self.port))

            # todo: authenticate server, start communication loop with authenticated server
            # messenger = self.authenticate_as_client(server)

            m = Messenger(s)
            self._messenger = m

    def send(self, msg):
        # if self.is_secure():
        #     encrypt(msg)
        #     self._messenger.send(msg)
        # else:
        #     raise Exception("Session not securely initialized")
        e_msg = encrypt(keystream, msg, iv)
        print("type of encrypt: "+str(type(e_msg)))
        self._messenger.send(e_msg)

    def recv(self):
        e_data = self._messenger.recv()
        raw_data = decrypt(keystream, e_data, iv)
        return raw_data

    def is_secure(self):
        return False

    def close(self):
        self._messenger.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=[MODE_CLIENT, MODE_SERVER], help='Which mode to run the program in - "%s" for '
                        'client and "%s" for server'.format(MODE_CLIENT, MODE_SERVER))
    args = parser.parse_args()

    ## TEST: connect to test_server, testing Client messenger send/receive
    host_ip = '127.0.0.1'
    port = 12345
    raw_msg = "Alice, Ra"

    if args.mode == MODE_CLIENT:
        session = SessionManager(port, host_ip)
        session.send(raw_msg)
        response = session.recv()
        print(response)
        session.close()
    elif args.mode == MODE_SERVER:
        session = SessionManager(port)
        while session is not None:  # the gui should be spamming this
            try:
                msg_in = session.recv()
                if len(msg_in) > 0:
                    print(msg_in)
                    session.send('hello {}'.format(msg_in))
                    msg_in = ""
            except Exception as e:
                print("exception: {}".format(e))
                session.reset_messenger()
    else:
        raise Exception("We should never get here! Unexpected cli mode arg %s".format(args.mode))
