from Crypto.Cipher import AES
from os import urandom
import random
import hashlib
from logging import getLogger


def pad_message(msg):
    pad_len = 16-len(msg)%16
    pad_msg = msg.zfill(pad_len+len(msg))
    return pad_msg


def generate_init_vector():
    # TODO Replace with urandom
    iv = b'asdfaskjhgkjhgdf'  # urandom(16)
    return iv


class Encrypter:
    def __init__(self, key, iv):
        self._AES = AES.new(key, AES.MODE_CBC, iv)

        # init the logger with a name based on the key
        self.log = getLogger(__name__ + "." + str(key)[:5])

    def encrypt(self, msg):
        padded_msg = pad_message(msg)
        cipher_msg = self._AES.encrypt(padded_msg)
        self.log.debug("encrypted {} chars: {} to {}".format(len(padded_msg), str(padded_msg), str(cipher_msg)))
        return cipher_msg

    def decrypt(self, cipher_msg):
        # covert string tp bytes for AES
        if len(cipher_msg) > 0:
            plain_text = self._AES.decrypt(cipher_msg)
            self.log.debug("decrypted {} chars: {} to {}".format(len(cipher_msg), str(cipher_msg), str(plain_text)))
        else:
            plain_text = b''
        return plain_text


def generate_keystream(key):
    ## if key<16 bytes, generate keystream using sha256
    s = hashlib.sha256()
    s.update(key.encode('utf-8'))
    keystream = s.digest()
    return keystream
	
def generateAorB():
	return random.randint(2048,4096)

def quick_test():

    IV = generate_init_vector()
    print("Injection Vector: "+ str(IV))

    key = "test**965"
    keystream = generate_keystream(key)

    plain = "Hello I am Alice!"
    print("Plain text: "+plain)

    cipher = encrypt(keystream, plain, IV)
    #print("Cipher text: "+cipher.decode('utf-8'))

    decipher = decrypt(keystream, cipher, IV)
    print("Decrypted: %s"%(decipher))

if __name__ == "__main__":
    quick_test()
