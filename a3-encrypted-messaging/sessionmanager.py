__author__ = 'andrew'

# run with python 3.4.3

import logging
from os import urandom
import socket

from encrypter import Encrypter, create_key, generateAorB, genStr
from messenger import Messenger


MESSAGE_ENCODING = 'utf-8'

IS_SERVER = 1
IS_CLIENT = 0

IV_LENGTH = 16
CHALLENGE_LENGTH = 16
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2


class SessionManager:
    def __init__(self, port, ip_address, secret_value, continueHandler):
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port

        self.port = port
        self.ip_address = ip_address
        self.master_key = create_key(secret_value)
        self.log = logging.getLogger(__name__)
        self.continueHandler = continueHandler

        self._messenger = None
        self.reset_messenger()

    def generate_and_send_iv(self, session_socket):
        iv = urandom(16)

        self.continueHandler(iv)
        # send iv over socket first!
        sent_len = 0
        while sent_len < len(iv):
            sent = session_socket.send(iv[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent
        logging.getLogger(__name__).info("sent iv: " + str(iv))
        return iv

    def receive_iv(self, session_socket):
        iv = b''
        while len(iv) < IV_LENGTH:
            chunk = session_socket.recv(IV_LENGTH - len(iv))
            if chunk == b'':
                session_socket.close()
                raise RuntimeError("socket closed")
            iv += chunk
        logging.getLogger(__name__).info('received iv: {}'.format(str(iv)))
        return iv

    def authenticate_as_server(self, session_socket):
        # authenticates an external client connected via session_socket

        iv = self.generate_and_send_iv(session_socket) # the server should generate a random iv

        master_encrypter = Encrypter(self.master_key, iv)
        m_messenger = Messenger(session_socket, master_encrypter, self.continueHandler)

        secret_b = generateAorB()
        public_b = str(pow(g, secret_b, p))
        server_challenge = genStr(CHALLENGE_LENGTH)
        server_challenge_hash = str(create_key(server_challenge))

        response = m_messenger.recv()
        while not response:
            response = m_messenger.recv()

        client_challenge = response[:CHALLENGE_LENGTH]
        client_challenge_hash = str(create_key(client_challenge))
        public_a = response[CHALLENGE_LENGTH:]
        self.log.info('publicA is {}'.format(public_a))
        m_messenger.send(client_challenge_hash)
        m_messenger.send(server_challenge + public_b)
        session_key = create_key(str(pow(int(public_a), secret_b, p)))
        self.log.info('session key is {}'.format(session_key))

        response = m_messenger.recv()
        while not response:
            response = m_messenger.recv()

        if response != server_challenge_hash:
            self.log.warn('Client could not be authenticated. Session will be terminated!')
            m_messenger.close()
        else:
            print('Server Authentication Successful!!!')

        session_encrypter = Encrypter(session_key, iv)
        self._messenger = Messenger(session_socket, session_encrypter, self.continueHandler)

    def authenticate_as_client(self, session_socket):
        # authenticates an external server connected via session_socket

        iv = self.receive_iv(session_socket)
        master_encrypter = Encrypter(self.master_key, iv)
        m = Messenger(session_socket, master_encrypter, self.continueHandler)

        client_challenge = genStr(CHALLENGE_LENGTH)
        client_challenge_hash = str(create_key(client_challenge))
        secretA = generateAorB()
        publicA = pow(g, secretA, p)
        m.send(client_challenge + str(publicA))

        response = m.recv()
        while not response:
            response = m.recv()

        print('expected:', client_challenge_hash, response, response == client_challenge_hash)
        if response != client_challenge_hash:
            m.close()
            raise Exception('client could not authenticate')

        response = ''
        while not response:
            response = m.recv()

        server_challenge_hash = str(create_key(response[:CHALLENGE_LENGTH]))
        m.send(server_challenge_hash)
        public_b = int(response[CHALLENGE_LENGTH:])
        self.log.info('g^b mod p is {}'.format(public_b))
        session_key = create_key(str(pow(public_b, secretA, p)))
        self.log.info('Session key generated by the client is {}'.format(session_key))

        session_encrypter = Encrypter(session_key, iv)
        session_m = Messenger(session_socket, session_encrypter, self.continueHandler)

        self._messenger = session_m

    def reset_messenger(self):
        if self._messenger is not None:
            self._messenger.close()
            self._messenger = None

        # AF_INET = ipv4, SOCK_STREAM = tcp
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # assuming we can use the same "client socket" for both reading and writing
        if self.ip_address is None:  # server init
            s.bind(('', self.port))
            self.log.info("Listening for connection on port {}".format(self.port))
            s.listen(1) # listen for only one connection

            session_socket, addr = s.accept()
            self.log.info("Accepted connection from {}".format(addr))

            self.authenticate_as_server(session_socket)
            s.close()
        else:
            # client init: specify ip address and port to try to ping
            self.log.info("Trying to connect to {}:{}".format(self.ip_address, self.port))
            s.connect((self.ip_address, self.port))

            self.authenticate_as_client(s)


    def checkReceivedMessages(self):
        try:
            nextReceivedMessage = self.recv()
            # Get and Send Messages
            return nextReceivedMessage

        except Exception as e:
            self.log.warning("Session closed: {}".format(e))
            self.reset_messenger()
        # Return 0 as default
        return 0         

    def send(self, msg):
        self._messenger.send(msg)

    def recv(self):
        data_in = self._messenger.recv()
        if len(data_in) > 0:
            self.log.info('received data: ' + data_in)
        return data_in

    def close(self):
        self._messenger.close()

