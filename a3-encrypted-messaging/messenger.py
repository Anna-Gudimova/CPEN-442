__author__ = 'andrew'

import socket


class Messenger:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address  # the the ip/port to message to
        self.port = port
        self.buffer_size = 1024
        # AF_INET = ipv4, SOCK_STREAM = tcp
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("socket creation successful")
        except socket.error as err:
            print("socket creation failed: %s" %(err))

    def send_msg(self, msg):
        # return True if message is successfully sent
        msg_len = len(msg)
        sent_len = 0
        while sent_len < msg_len: #still have stuff in send buffer
            # socket.send returns bytes sent
            sent = self.s.send(msg[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent
        return True

    def receive_msg(self):
        # return a new message, if received.
        # TODO: first char of message should be size. Use this in a recv loop
        chunks = []
        chunk = self.s.recv(self.buffer_size)
        chunks.append(chunk)
        return b''.join(chunks)

    def be_a_server(self):
        self.s.bind(('', self.port))
        self.s.listen()
        # TODO: create accept loop. Once a "secure" client mutual authenticates, then become_a_client
        while True:
            c, addr = self.s.accept()
            print("Got connection from ", addr)

            data = c.recv(1024)
            c.send(b"Thank you for connecting %s" %(data))

            print("server sent thank you message")
            c.close()

    def be_a_client(self):
        try:
            self.s.connect((self.ip_address, self.port))
        except socket.error as err:
            print("socket connect failed %s" %(err))


    def tear_down(self):
        self.close()
