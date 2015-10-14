__author__ = 'andrew'

# run with python 3.4.3

import argparse
from crypto import encrypt, decrypt, hash
import logging
from messenger import Messenger
import socket
import sys
from threading import Thread

MODE_CLIENT = 'c'
MODE_SERVER = 's'


class SessionManager:
    def __init__(self, port, ip_address=None):
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port
        self.port = port
        self.ip_address = ip_address
        self.log = logging.getLogger(__name__)

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
            self.log.info("Listening for connection on port {}".format(port))
            s.listen(1) # listen for only one connection

            session_socket, addr = s.accept()

            self.log.info("Accepted connection from {}".format(addr))

            # todo: authenticate client, start communication loop with authenticated client
            # messenger = self.authenticate_as_server(client)

            self._messenger = Messenger(session_socket)
            s.close()
        else:
            # client init: specify ip address and port to try to ping
            self.log.info("Trying to connect to {}:{}".format(self.ip_address, self.port))
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
        self._messenger.send(msg)

    def recv(self):
        return self._messenger.recv()

    def is_secure(self):
        return False

    def close(self):
        self._messenger.close()


def init_logger(file_name=None):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # log to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    # log to file
    if file_name is not None:
        fh = logging.FileHandler(file_name)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

    # todo: add GUI handler (INFO level)!


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=[MODE_CLIENT, MODE_SERVER], help='Which mode to run the program in - "%s" for '
                        'client and "%s" for server'.format(MODE_CLIENT, MODE_SERVER))
    parser.add_argument('log_file', nargs='?', help="specify a file to write logs to.")
    args = parser.parse_args()

    # set up logging, create a logger for the local scope
    init_logger(args.log_file)
    log = logging.getLogger(__name__)

    # todo: get from GUI
    host_ip = '127.0.0.1'
    port = 12345

    if args.mode == MODE_CLIENT:
        session = SessionManager(port, host_ip)
        session.send("Alice, Ra")
        response = session.recv()
        session.close()
    elif args.mode == MODE_SERVER:
        session = SessionManager(port)
        while session is not None:  # the gui should be spamming this
            try:
                msg_in = session.recv()
                if msg_in is not None:
                    session.send('hello {}'.format(msg_in))
            except Exception as e:
                log.exception("Session closed: {}".format(e))
                session.reset_messenger()
    else:
        raise Exception("We should never get here! Unexpected cli mode arg %s".format(args.mode))
