from Crypto.Cipher import AES
from os import urandom
import hashlib

Key_Master = urandom(16)

def generate_init_vector():
    iv = urandom(16)
    return iv

def encrypt(key, msg, iv):
    encrypter = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = encrypter.encrypt(msg)
    return cipher_text

def decrypt(key, cipher, iv):
    decrypter = AES.new(key, AES.MODE_CBC, iv)
    plain_text = decrypter.decrypt(cipher)
    return plain_text

def pad_message(msg):
    pad_len = 16-len(msg)%16
    print("strlen: "+str(len(msg)))
    pad_msg = msg.zfill(pad_len+len(msg))
    print("Padded msg: "+pad_msg)
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
    padded_msg = pad_message(plain)

    cipher = encrypt(keystream, padded_msg, IV)
    print("Cipher text: "+str(cipher))

    decipher = decrypt(keystream, cipher, IV)
    print("Decrypted: "+str(decipher))

quick_test()



