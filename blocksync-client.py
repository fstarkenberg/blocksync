#!/usr/bin/env python3

import sys
import os
from datetime import datetime
import hashlib
import socket
import json

BLOCK_DEVICE = 'image'
BLOCK_SIZE = 16384

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

STARTTIME = datetime.now()

def DEVICE_SIZE(BLOCK_DEVICE):
	with open(BLOCK_DEVICE, 'rb') as f:
		f.seek(0, 2)
		SIZE = f.tell()
	return SIZE

def progress(SIZE, CURRENT):
    SIZE_GB = int(SIZE/1000000000)
    CURRENT_GB = int(CURRENT/1000000000)
    CURRENT_MB = int(CURRENT/1000000)
    CURRENT_TIME = datetime.now() - STARTTIME
    if CURRENT_TIME.seconds is 0:
        SPEED = 0
    else:
        SPEED = CURRENT_MB / CURRENT_TIME.seconds
    return "%d GB/%d GB - %d MB/s - %s" % (CURRENT_GB, SIZE_GB, SPEED, CURRENT_TIME)

if len(sys.argv) < 2:
    print("USAGE: %s --copy | --sync --sparse /dev/blkdevice" % sys.argv[0])
    sys.exit(0)

SIZE = DEVICE_SIZE(BLOCK_DEVICE)

if sys.argv[1] == '--copy':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'w') as h:
        while f.tell() < SIZE:
            p = progress(SIZE, f.tell())
            print(p, end='\r')
            read_data = f.read(BLOCK_SIZE)
            # Save block hash to a file
            m = hashlib.md5()
            m.update(read_data)
            h.write(m.hexdigest())
            h.write('\n')
            if '--sparse' in sys.argv:
                # Don't send empty blocks
                if read_data.count(read_data[0]) == len(read_data):
                    continue
            msg = {"BLOCK_START": (f.tell() - BLOCK_SIZE)}
            client.send(json.dumps(msg).encode())
            client.send(read_data)
            #client.send(read_data)
            #client.send(msg)
    print(p)

elif sys.argv[1] == '--sync':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'r') as h:
        CHANGE_COUNTER = 0
        for hash in h.readlines():
            read_data = f.read(BLOCK_SIZE)
            if '--sparse' in sys.argv:
                # Skip empty blocks
                if read_data.count(read_data[0]) == len(read_data):
                    continue
            p = progress(SIZE, f.tell())
            print(p, end='\r')
            m = hashlib.md5()
            m.update(read_data)
            if m.hexdigest() == hash.strip():
                # No change
                pass
            else:
                # f.tell has already moved on to next offset, so we need to subtract the block size
                msg = {"BLOCK_START": (f.tell() - BLOCK_SIZE)}
                client.send(json.dumps(msg).encode())
                if client.recv(1024).decode() == "ack":
                    # Send block
                    client.send(read_data)
                if not client.recv(1024).decode() == "written":
                    print("Server could not write...")
                    sys.exit(1)
                CHANGE_COUNTER += 1
    print(p)
    print("%d blocks have changed. ~%d MB." % (CHANGE_COUNTER, (CHANGE_COUNTER * BLOCK_SIZE)/1000000))

client.close()
