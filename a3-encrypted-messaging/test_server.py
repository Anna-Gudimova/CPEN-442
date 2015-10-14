__author__ = 'Alshahna'

# test server, run separately from a3-main if testing messenger()

import socket

s = socket.socket()
print("Server socket creation successful")

# reserve port on local computer
port = 12345

# bind port
s.bind(('', port))
print("server socket binded to %s" %(port))

# listen on this port
s.listen()
print("socket is listening")

# run server
while True:
    c, addr = s.accept()
    print("Got connection from ", addr)

    data = c.recv(1024)
    c.send(bytes("Thank you for connecting {}".format(data), 'ascii'))

    print("server sent thank you message")
    c.close()

