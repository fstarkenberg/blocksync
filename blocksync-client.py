#!/usr/bin/env python3
import sys
import os
from datetime import datetime
import hashlib
import socket
import json


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

# Todo: fix
if sys.argv[2] == '--sparse':
    BLOCK_DEVICE = sys.argv[3]
else:
    BLOCK_DEVICE = sys.argv[2]

SIZE = DEVICE_SIZE(BLOCK_DEVICE)

i = 0
if sys.argv[1] == '--copy':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'w') as h:
        while f.tell() < SIZE:
            p = progress(SIZE, f.tell())
            if i % 10000 is 0:
                # Only print progress every nth loop
                print(p, end='\r')
            read_data = f.read(BLOCK_SIZE)
            # Save block hash to a file
            m = hashlib.md5()
            m.update(read_data)
            h.write(m.hexdigest())
            h.write('\n')
            if '--sparse' in sys.argv:
                # Skip empty blocks
                if read_data.count(read_data[0]) == len(read_data):
                    continue
            # First two bytes contain start block number
            BLOCK_START = str(f.tell() - BLOCK_SIZE).zfill(14)
            BLOCK = b"".join([bytes(BLOCK_START, encoding='utf-8'), read_data])
            client.send(BLOCK)
            i += 1

    print(p)
    client.close()

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
                continue
            else:
                # First two bytes contain start block number
                BLOCK_START = str(f.tell() - BLOCK_SIZE).zfill(14)
                BLOCK = b"".join([bytes(BLOCK_START, encoding='utf-8'), read_data])
                client.send(BLOCK)
                CHANGE_COUNTER += 1
    print(p)
    print("%d blocks have changed. ~%d MB." % (CHANGE_COUNTER, (CHANGE_COUNTER * BLOCK_SIZE)/1000000))

