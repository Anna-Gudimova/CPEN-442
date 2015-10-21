from __future__ import print_function
__author__ = 'andrew'

# run with python 3.4.3


import argparse
import logging
from crypto import encrypt, decrypt, generate_keystream, generate_init_vector, generateAorB
from messenger import Messenger
import socket
import sys
from threading import Thread
from threading import Timer
import ctypes
import queue



print = lambda x: sys.stdout.write("%s\n" % x)

MESSAGE_ENCODING = 'utf-8'

IS_SERVER = 1
IS_CLIENT = 0

MODE_CLIENT = 'c'
MODE_SERVER = 's'

## IV generated for each new msg..decrypt requires same IV
iv = generate_init_vector()

class SessionManager:
    def __init__(self, port, ip_address, key):
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port

        self.port = port
        self.ip_address = ip_address
        self.keystream = generate_keystream(key)

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
            self.operationMode = IS_SERVER

            s.bind(('', self.port))
            self.log.info("Listening for connection on port {}".format(self.port))
            s.listen(1) # listen for only one connection

            session_socket, addr = s.accept()

            self.log.info("Accepted connection from {}".format(addr))

            # todo: authenticate client, start communication loop with authenticated client
            # messenger = self.authenticate_as_server(client)

            self._messenger = Messenger(session_socket)
            #s.close()

        else:
            # client init: specify ip address and port to try to ping
            self.operationMode = IS_CLIENT

            self.log.info("Trying to connect to {}:{}".format(self.ip_address, self.port))
            s.connect((self.ip_address, self.port))

            # todo: authenticate server, start communication loop with authenticated server
            # messenger = self.authenticate_as_client(server)

            m = Messenger(s)
            self._messenger = m


    def checkReceivedMessages(self):
        try:
            nextReceivedMessage = self.recv()
            # Get and Send Messages
            return nextReceivedMessage

        except Exception as e:
            self.log.exception("Session closed: {}".format(e))
            if self.operationMode is IS_SERVER:
                session.reset_messenger()   
        # Return 0 as default
        return 0         

    def send(self, msg):
        e_msg = encrypt(self.keystream, msg, iv)
        self._messenger.send(e_msg)

    def recv(self):
        e_data = self._messenger.recv()
        raw_data = decrypt(self.keystream, e_data, iv)
        return raw_data


    def close(self):
        self._messenger.close()

