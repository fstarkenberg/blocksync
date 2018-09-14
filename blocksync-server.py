#!/usr/bin/env python3

import socket
import json

BLOCK_DEVICE = 'new-image'
BLOCK_SIZE = 16384

HOST = "127.0.0.1"
PORT = 5000
 
server = socket.socket()
server.bind((HOST, PORT))
 
server.listen(1)
conn, addr = server.accept()
print ("Connection from: " + str(addr))
f = open(BLOCK_DEVICE, 'rb+')
while True:
    data = conn.recv(BLOCK_SIZE)
    if not data:
        break

    if len(data) < 100:
        # Message
        msg = json.loads(data.decode())
        BLOCK_SIZE = msg['BLOCK_SIZE']
        BLOCK_START = msg['BLOCK_START']
        # Send ack
        conn.send("ack".encode())
    elif len(data) == BLOCK_SIZE:
        # Block
        print("Writing block %d" % BLOCK_START, end='\r')
        f.seek(BLOCK_START, 0)
        f.write(data)
        # Send ack
        conn.send("written".encode())
         
conn.close()
f.close()
