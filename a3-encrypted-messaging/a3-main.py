__author__ = 'andrew'

# run with python 3.4.3

import argparse
from crypto import encrypt, decrypt, hash
from gui import Gui
from messenger import Messenger
import socket
import sys

MODE_CLIENT = 'c'
MODE_SERVER = 's'

# this class holds the state of the program
class SessionManager:
    def __init__(self):
        # define member variables here
        self.messenger = None  # some class to do network communications
        self.session_key = None
        self.master_key = None  # this doesn't really need to be a member variable, but whatever

    def start_client(self, master_key, other_networking_args):
        self.messenger = Messenger(other_networking_args)

    def start_server(self, master_key, other_networking_args):
        pass

    def send_msg(self, msg):
        if self.is_secure():
            encrypt(msg)
            self.messenger.send_msg(msg)
        else:
            raise Exception("Session not securely initialized")

    def receive_msg(self):
        pass
    
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
    messenger = Messenger(host_ip, port)

    if args.mode == MODE_CLIENT:
        print("you are a client")
        messenger.be_a_client()
        messenger.send_msg(b"Alice, Ra")
        response = messenger.receive_msg()
        print(response)
    elif args.mode == MODE_SERVER:
        print("you are a server")
        messenger.be_a_server()
    else:
        raise Exception("We should never get here! Unexpected cli mode arg %s".format(args.mode))

    #lassie = SessionManager()
    #gui = Gui(lassie)
    #gui.run()
    #print("program done.")

