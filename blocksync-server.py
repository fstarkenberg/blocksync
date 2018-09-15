#!/usr/bin/env python3

import sys
import socket
import json

BLOCK_DEVICE = 'new-image'
BLOCK_SIZE = 4096

HOST = "127.0.0.1"
PORT = 5000

if len(sys.argv) < 2:
    print("USAGE: %s --copy | --sync /dev/blkdevice" % sys.argv[0])
    sys.exit(0)

server = socket.socket()
server.bind((HOST, PORT))
 
server.listen(1)
print("Listening...")
if sys.argv[1] == '--copy':
    while True:
        conn, addr = server.accept()
        print ("Connection from: " + str(addr))
        f = open(BLOCK_DEVICE, 'rb+')

        while True:
            data = conn.recv(BLOCK_SIZE)
            if not data: break
            f.write(data)
            print("Writing data..." , end='\r')

    f.close()
    print("Finished writing...")
    conn.close()
    print("Client disconnected...")

elif sys.argv[1] == '--sync':
    conn, addr = server.accept()
    print ("Connection from: " + str(addr))
    f = open(BLOCK_DEVICE, 'rb+')
    while True:
        data = conn.recv(BLOCK_SIZE)
        if not data: break

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
            f.seek(BLOCK_START)
            f.write(data)
            # Send ack
            conn.send("written".encode())

    f.close()
    print("Finished writing...")
    conn.close()
    print("Client disconnected...")

