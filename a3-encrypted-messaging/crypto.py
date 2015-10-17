from Crypto.Cipher import AES
from os import urandom
import hashlib
import base64

Key_Master = urandom(16)

def generate_init_vector():
    iv = b'asdfaskjhgkjhgdf'# urandom(16)
    print("iv type: "+str(type(iv)))
    return iv

def encrypt(key, msg, iv):
    padded_msg = pad_message(msg)
    print("padded_msg len: "+str(len(padded_msg)))
    encrypter = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = encrypter.encrypt(padded_msg)
    print("encrypt bytes: "+str(len(cipher_text)))
    print("sending ", cipher_text)
    return cipher_text

def decrypt(key, cipher, iv):
    # covert string tp bytes for AES
    if len(cipher) > 0:
        print("decrypt bytes: "+str(len(cipher)))
    decrypter = AES.new(key, AES.MODE_CBC, iv)
    plain_text = decrypter.decrypt(cipher)
    return plain_text

def pad_message(msg):
    pad_len = 16-len(msg)%16
    print("strlen: "+str(len(msg)))
    pad_msg = msg.zfill(pad_len+len(msg))
    return pad_msg

def generate_keystream(key):
    ## if key<16 bytes, generate keystream using sha256
    s = hashlib.sha256()
    s.update(key.encode('utf-8'))
    keystream = s.digest()
    return keystream

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
