from Crypto.Cipher import AES
from os import urandom
import hashlib
import base64

Key_Master = urandom(16)

def generate_init_vector():
    iv = urandom(16)
    return iv

def encrypt(key, msg, iv):
    padded_msg = pad_message(msg)
    encrypter = AES.new(key, AES.MODE_CBC, iv)
    # base64 to convert bytes to string. Messenger.send expects string
    cipher_text = base64.b64encode(iv + encrypter.encrypt(padded_msg))
    return cipher_text

def decrypt(key, cipher, iv):
    print("decrypt: "+str(len(cipher)))
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
    padded_msg = pad_message(plain)

    cipher = encrypt(keystream, padded_msg, IV)
    print("Cipher text: "+str(cipher))

    decipher = decrypt(keystream, cipher, IV)
    print("Decrypted: "+str(decipher))




