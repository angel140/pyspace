# -*- coding:utf-8 -*-

from socket import *

# Address and Port 
HOST = 'lua.yinyst.com'
PORT = 8888
ADDR = (HOST, PORT)

# BufferSize
BUFSIZ = 1024

#build socket 
tcpCliSocket = socket(AF_INET, SOCK_STREAM)
tcpCliSocket.connect(ADDR)

while True:
    data = input('> ')
    if not data:
        break
    # send data
    tcpCliSocket.sendall(data.encode())
    # recv data
    data = tcpCliSocket.recv(BUFSIZ)
    if not data:
        break
    # show data
    print ((' %s' % ( data)))
tcpCliSocket.close()