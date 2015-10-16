__author__ = 'andrew'

import re
from select import select
from crypto import encrypt, decrypt, generate_keystream, generate_init_vector

## TODO: Figure out ideal place for following lines (coming from GUI)
## IV generated for each new msg..decrypt requires same IV
key = "something Ildar will write"
keystream = generate_keystream(key)
iv = generate_init_vector()


# provides a queue of messages for the
class Messenger:
    # sends/receives messages of text with encoded header describing message size
    BUFFER_SIZE = 2048
    ENCODING = 'utf-8'
    # todo: add escape sequence to not confuse HEADER_SUFFIX found in messages
    HEADER_SUFFIX = '|'  # expressed in regex

    def __init__(self, socket):
        self._s = socket
        self._raw_received = ''
        self._next_msg_size = -1

    def send(self, msg):
        # msg is some string (not bytes)
        # header describes message length
        header = str(len(msg)) + self.HEADER_SUFFIX
        raw_msg = (header + msg).encode(self.ENCODING)
        cipher_msg = encrypt(keystream, raw_msg, iv)

        total_len = len(cipher_msg)
        sent_len = 0
        while sent_len < total_len:
            sent = self._s.send(cipher_msg[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent

    def recv(self):
        # read in any data
        rlist, _, _ = select([self._s], [], [], 0.01)
        if len(rlist) > 0:
            chunk = rlist[0].recv(self.BUFFER_SIZE)
            if chunk == b'':
                rlist[0].close()
                raise RuntimeError("socket closed")
            self._raw_received += chunk.decode(self.ENCODING)

        # still looking for a header
        if self._next_msg_size < 0:
            # TODO: parse self._raw_received for header and extract expected message size..
            match = re.search('(?P<length>[\d]+)' + self.HEADER_SUFFIX, self._raw_received)
            if match.group('length') is not None:
                self._next_msg_size = int(match.group('length'))
                self._raw_received = self._raw_received[match.end() + 1:]
        # waiting to receive the full message body
        if len(self._raw_received) >= self._next_msg_size:
            msg = self._raw_received[:self._next_msg_size]
            self._raw_received = self._raw_received[self._next_msg_size:]
            self._next_msg_size = -1
            ##TODO send extrating header and decrypt requires msg that is multiple of 16bytes..how to address this?
            return msg
        return None

    def close(self):
        self._s.close()
