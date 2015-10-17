__author__ = 'andrew'

import re
from select import select

# provides a queue of messages for the
class Messenger:
    # sends/receives messages of text with encoded header describing message size
    BUFFER_SIZE = 16
    ENCODING = 'utf-8'
    # todo: add escape sequence to not confuse HEADER_SUFFIX found in messages
    HEADER_SUFFIX = '|'  # expressed in regex

    def __init__(self, socket):
        self._s = socket
        self._raw_received = b''
#         self._next_msg_size = -1

    def send(self, msg):
        if len(msg) % self.BUFFER_SIZE:
            raise Exception('message length must be a multiple of {}'.format(self.BUFFER_SIZE))
        # msg is some string (not bytes)
        # header describes message length
        # header = str(len(msg)) + self.HEADER_SUFFIX
#        raw_msg = (header + msg).encode(self.ENCODING)
        # raw_msg = header.encode(self.ENCODING) + msg

        total_len = len(msg)
        sent_len = 0
        while sent_len < total_len:
            sent = self._s.send(msg[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent

    def recv(self):
        # read in any data to self._raw_received (non blocking)
        rlist, _, _ = select([self._s], [], [], 0.01)
        if len(rlist) > 0:
            chunk = rlist[0].recv(self.BUFFER_SIZE * 16)
            if chunk == b'':
                rlist[0].close()
                raise RuntimeError("socket closed")
            self._raw_received += chunk

        # return as many full blocks of data as we have
        msg = []
        while len(self._raw_received) >= self.BUFFER_SIZE:
            msg.append(self._raw_received[:self.BUFFER_SIZE])
            self._raw_received = self._raw_received[self.BUFFER_SIZE:]
        return b''.join(msg)

    def close(self):
        self._s.close()
