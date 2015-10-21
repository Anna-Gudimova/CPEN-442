from Crypto.Cipher import AES
from os import urandom
import random
import string
import hashlib
from logging import getLogger

BLOCK_SIZE = 16

def generate_keystream(key):
    # improve key security by generating keystream using sha256. Good if key is short
    s = hashlib.sha256()
    s.update(key.encode('utf-8'))
    keystream = s.digest()
    return keystream

def generate_init_vector():
    # TODO Replace with urandom
    iv = b'asdfaskjhgkjhgdf'  # urandom(16)
    return iv

class Encrypter:
    def __init__(self, key, iv):
        self._AES = AES.new(key, AES.MODE_CBC, iv)

        # init the logger with a name based on the key
        # self.log = getLogger(__name__ + "." + str(key)[:5])

    def encrypt(self, bmsg):
        # encrypts plain text string to cipher bytes
        if len(bmsg) % BLOCK_SIZE:
            raise Exception("msg length must be a multiple of {}: {}".format(BLOCK_SIZE, bmsg))

        cipher_bmsg = self._AES.encrypt(bmsg)
        # self.log.debug("encrypted {} chars: {} to {}".format(len(bmsg), str(bmsg), str(cipher_bmsg)))
        return cipher_bmsg

    def decrypt(self, cipher_bmsg):
        # decrypts cipher bytes to plain text string
        if len(cipher_bmsg) > 0:
            bmsg = self._AES.decrypt(cipher_bmsg)
            # self.log.debug("decrypted {} chars: {} to {}".format(len(cipher_bmsg), str(cipher_bmsg), bmsg))
        else:
            bmsg = b''
        return bmsg

def generateAorB():
	# return random.randint(2048,4096)
    #return random.randint(16,32)
	return random.getrandbits(16)

def genStr(size=15, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))
	
def quick_test():

    IV = generate_init_vector()
    print("Injection Vector: "+ str(IV))

    key = "test**965"
    keystream = generate_keystream(key)

    encrypter = Encrypter(keystream, IV)

    plain = "Hello I am Alice!"
    print("Plain text: "+plain)

    cipher = encrypter.encrypt(plain)
    #print("Cipher text: "+cipher.decode('utf-8'))

    decipher = encrypter.decrypt(cipher)
    print("Decrypted: %s"%(decipher))

if __name__ == "__main__":
    # quick_test()
    g=gToPower(generateAorB(),2)
    print('gToPower output is ',g,' \n')
