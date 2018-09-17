#!/usr/bin/env python3
import sys
import socket
import json

BLOCK_SIZE = 16384
HOST = "127.0.0.1"
PORT = 5000

if len(sys.argv) < 2:
    print("USAGE: %s /dev/blkdevice" % sys.argv[0])
    sys.exit(0)

BLOCK_DEVICE = sys.argv[1]

server = socket.socket()
server.bind((HOST, PORT))
 
server.listen(1)
print("Listening...")
conn, addr = server.accept()
print ("Connection from: " + str(addr))
f = open(BLOCK_DEVICE, 'rb+')
BUF_SIZE = BLOCK_SIZE + 14

while True:
    data = conn.recv(BUF_SIZE)
    if not data: break

    # Unpack block, first two bytes are block start number
    BLOCK_START, BLOCK = data[:14], data[14:]

    try:
        BLOCK_START = int(BLOCK_START)
    except ValueError:
        continue

    f.seek(BLOCK_START)
    f.write(BLOCK)

f.close()
print("Finished writing...")
conn.close()
print("Client disconnected...")
sys.exit(0)
