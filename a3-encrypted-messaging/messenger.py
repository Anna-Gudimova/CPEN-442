__author__ = 'andrew'

import logging
import math
from crypto import BLOCK_SIZE
from select import select

STRING_ENCODING = 'utf-8'
HEADER_SUFFIX = b'|'

def add_header(bmsg):
    # header contains padding to make message a multiple of BLOCK SIZE
    # num blocks includes block containing header.. need this because it's encrpyted
    num_blocks = math.ceil(len(bmsg) / BLOCK_SIZE)
    header = bytes(str(num_blocks), STRING_ENCODING) + HEADER_SUFFIX
    while num_blocks != math.ceil(len(header + bmsg) / BLOCK_SIZE):
        num_blocks = math.ceil(len(header + bmsg) / BLOCK_SIZE)
        header = bytes(str(num_blocks), STRING_ENCODING) + HEADER_SUFFIX

    bmsg = header + bmsg
    pad_len = BLOCK_SIZE - len(bmsg) % BLOCK_SIZE
    pad_bmsg = bmsg.zfill(pad_len + len(bmsg))
    return pad_bmsg

class HeaderError(Exception):
    pass

def read_header(bmsg):
    header_idx = bmsg.find(HEADER_SUFFIX)
    if header_idx == -1:
        raise HeaderError('header suffix not found')
    num_blocks = int(bmsg[:header_idx])
    bmsg = bmsg[header_idx + len(HEADER_SUFFIX):]
    return num_blocks, bmsg

class Messenger:
    # sends/receives messages of text with encoded header describing message size

    def __init__(self, socket, encrypter):
        self._s = socket
        self._encrypter = encrypter
        self.log = logging.getLogger(__name__)

        self._raw_received = b''
        self._blocks_remaining = -1
        self._msg_out = []

    def send(self, msg):
        bmsg = msg.encode(STRING_ENCODING)
        bmsg = add_header(bmsg)
        bmsg = self._encrypter.encrypt(bmsg)

        total_len = len(bmsg)
        sent_len = 0
        while sent_len < total_len:
            sent = self._s.send(bmsg[sent_len:])
            if sent == 0:
                raise RuntimeError("socket send connection issue")
            sent_len += sent  # how much of the message we have sent
        self.log.info("sent " + str(bmsg))

    def recv(self):
        # read in any data to self._raw_received (non blocking)
        rlist, _, _ = select([self._s], [], [], 0.01)
        if len(rlist) > 0:
            chunk = rlist[0].recv(BLOCK_SIZE * 16)
            if chunk == b'':
                rlist[0].close()
                raise RuntimeError("socket closed")
            self._raw_received += chunk

        while len(self._raw_received) >= BLOCK_SIZE:
            # read one block of data
            if self._blocks_remaining < 0:
                # try to read a header
                blocks_available = len(self._raw_received) // BLOCK_SIZE
                bmsg = self._encrypter.decrypt(self._raw_received[:blocks_available * BLOCK_SIZE])
                try:
                    num_blocks, msg_start = read_header(bmsg)
                except HeaderError as e:
                    # incomplete header.. try again next time
                    break

                self._msg_out = [msg_start.decode(STRING_ENCODING)]
                self._blocks_remaining = num_blocks - blocks_available
                self._raw_received = self._raw_received[BLOCK_SIZE * blocks_available:]
            elif self._blocks_remaining > 0:  # body of a message
                bmsg = self._encrypter.decrypt(self._raw_received[:BLOCK_SIZE])
                self._msg_out.append(bmsg.decode(STRING_ENCODING))
                self._blocks_remaining -= 1
                self._raw_received = self._raw_received[BLOCK_SIZE:]

        if self._blocks_remaining == 0:
            next_msg = ''.join(self._msg_out)
            self.log.info("msg received: " + next_msg)
            self._blocks_remaining = -1
            return next_msg

        return ''

    def close(self):
        self._s.close()
