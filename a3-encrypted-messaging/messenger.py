__author__ = 'andrew'

import logging
import re
from select import select


# provides a queue of messages for the
class Messenger:
    # sends/receives messages of text with encoded header describing message size
    BUFFER_SIZE = 2048
    ENCODING = 'utf-8'
    HEADER_SUFFIX = '|'  # expressed in regex

    def __init__(self, socket):
        self._s = socket
        self._raw_received = ''
        self._next_msg_size = -1
        self.log = logging.getLogger(__name__)

    def send(self, msg):
        # msg is some string (not bytes)
        # header describes message length
        header = str(len(msg)) + self.HEADER_SUFFIX
        raw_msg = (header + msg).encode(self.ENCODING)

        total_len = len(raw_msg)
        sent_len = 0
        while sent_len < total_len:
            sent = self._s.send(raw_msg[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent
        self.log.info("sent " + raw_msg.decode(self.ENCODING))

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
            match = re.search('(?P<length>[\d]+)' + self.HEADER_SUFFIX, self._raw_received)
            if match.group('length') is not None:
                self._next_msg_size = int(match.group('length'))
                self._raw_received = self._raw_received[match.end() + 1:]
        # waiting to receive the full message body
        if len(self._raw_received) >= self._next_msg_size:
            msg = self._raw_received[:self._next_msg_size]
            self._raw_received = self._raw_received[self._next_msg_size:]
            self._next_msg_size = -1
            self.log.info("recv " + msg)
            return msg
        return None

    def close(self):
        self._s.close()
