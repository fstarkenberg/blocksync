#!/usr/bin/env python3

import sys
import socket
import json

BLOCK_DEVICE = 'new-image'
BLOCK_SIZE = 16384

HOST = "127.0.0.1"
PORT = 5000

#if len(sys.argv) < 2:
#    print("USAGE: %s /dev/blkdevice" % sys.argv[0])
#    sys.exit(0)

server = socket.socket()
server.bind((HOST, PORT))
 
server.listen(1)
print("Listening...")
conn, addr = server.accept()
print ("Connection from: " + str(addr))
f = open(BLOCK_DEVICE, 'rb+')
while True:
    data = conn.recv(BLOCK_SIZE)
    if not data: break

    try:
        msg = json.loads(data.decode())
        BLOCK_START = msg['BLOCK_START']
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        continue

    # Send ack
    #conn.send("ack".encode())

    # Block
    if BLOCK_START:
        print("Writing block %d" % BLOCK_START, end='\r')
        f.seek(BLOCK_START)
        f.write(data)

f.close()
print("Finished writing...")
conn.close()
print("Client disconnected...")

