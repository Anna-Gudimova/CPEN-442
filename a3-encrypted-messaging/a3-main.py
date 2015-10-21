__author__ = 'andrew'

# run with python 3.4.3

import argparse
import logging
from crypto import Encrypter, generate_keystream, generate_init_vector, generateAorB, genStr
from messenger import Messenger
import socket
import sys

MODE_CLIENT = 'c'
MODE_SERVER = 's'
CHALLENGE_LENGTH = 16
p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
g = 2

class SessionManager:
    def __init__(self, master_key, port, ip_address=None):
        # can be either a server or client. if ip_address=None, be a server on port. Otherwise, try to connect to
        # ip_address:port

        # networking config
        self.port = port
        self.ip_address = ip_address

        # security config
        self.master_key = generate_keystream(master_key)  # if the master key is too short, make it longer

        # initialized when communication is established in reset_messenger()
        self._messenger = None

        self.log = logging.getLogger(__name__)
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

            iv = generate_init_vector() # the server should generate a random iv
            master_encrypter = Encrypter(self.master_key, iv)
            m_messenger = Messenger(session_socket, master_encrypter)

            secret_b = generateAorB()
            public_b = str(pow(g, secret_b, p))
            server_challenge = genStr(CHALLENGE_LENGTH)
            server_challenge_hash = str(generate_keystream(server_challenge))

            response = m_messenger.recv()
            while not response:
                response = m_messenger.recv()

            client_challenge = response[:CHALLENGE_LENGTH]
            public_a = response[CHALLENGE_LENGTH:]
            self.log.info('publicA is {}'.format(public_a))
            m_messenger.send(client_challenge + server_challenge + public_b)
            session_key = generate_keystream(str(pow(int(public_a), secret_b, p)))
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
            self._messenger = Messenger(session_socket, session_encrypter)
            s.close()
        else:
            # client init: specify ip address and port to try to ping
            self.log.info("Trying to connect to {}:{}".format(self.ip_address, self.port))
            s.connect((self.ip_address, self.port))

            # TODO read the iv during first message passing
            iv = generate_init_vector() # the server should send a randomly generated iv
            master_encrypter = Encrypter(self.master_key, iv)

            m = Messenger(s, master_encrypter)

            clientChallenge = genStr(CHALLENGE_LENGTH)
            secretA = generateAorB()
            publicA = pow(g, secretA, p)
            m.send(clientChallenge + str(publicA))

            response = m.recv()
            while not response:
                response = m.recv()

            if response[:CHALLENGE_LENGTH] != clientChallenge:
                m.close()
                raise Exception('client could not authenticate')
            else:
                server_challenge_hash = str(generate_keystream(response[CHALLENGE_LENGTH:2 * CHALLENGE_LENGTH]))
                m.send(server_challenge_hash)
                public_b = int(response[2 * CHALLENGE_LENGTH:])
                self.log.info('g^b mod p is {}'.format(public_b))
                session_key = generate_keystream(str(pow(public_b, secretA, p)))
                self.log.info('Session key generated by the client is {}'.format(session_key))

                session_encrypter = Encrypter(session_key, iv)
                session_m = Messenger(s, session_encrypter)

                self._messenger = session_m

    def send(self, msg):
        self._messenger.send(msg)

    def recv(self):
        data_in = self._messenger.recv()
        if len(data_in) > 0:
            self.log.info('received data: ' + data_in)
        return data_in

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

    # todo: get these from GUI
    host_ip = '127.0.0.1'
    port = 16100
    master_key = "is ildar illuminati?"

    raw_msg = "Alice, Ra"
    p=0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF
    g=2

    if args.mode == MODE_CLIENT:
        session = SessionManager(master_key, port, host_ip)
        raw_msg = "Alissse, Ra"
        session.send(raw_msg)
        raw_in = session.recv()
        while not raw_in:
            raw_in = session.recv()

    elif args.mode == MODE_SERVER:
        session = SessionManager(master_key, port)
        while session is not None:
            try:
                msg_in = session.recv()
                if len(msg_in) > 0:
                    print(msg_in)
                    session.send('hello {}'.format(msg_in))
                    msg_in = ''
            except Exception as e:
                log.warning(e)
                session.reset_messenger()

