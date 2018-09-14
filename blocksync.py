#!/usr/bin/env python3

import sys
import os
from datetime import datetime
import hashlib

STARTTIME = datetime.now()
BLOCK_DEVICE = '/dev/vda'
BLOCK_SIZE = 16384

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
    print("USAGE: %s --generate | --compare /dev/blkdevice" % sys.argv[0])
    sys.exit(0)

SIZE = DEVICE_SIZE(BLOCK_DEVICE)

if sys.argv[1] == '--generate':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'w') as h:
        while f.tell() < SIZE:
            p = progress(SIZE, f.tell())
            print(p, end='\r')
            read_data = f.read(BLOCK_SIZE)
            m = hashlib.md5()
            m.update(read_data)
            h.write(m.hexdigest())
            h.write('\n')
    print(p)

elif sys.argv[1] == '--compare':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'r') as h:
        CHANGE_COUNTER = 0
        for hash in h.readlines():
            read_data = f.read(BLOCK_SIZE)
            p = progress(SIZE, f.tell())
            print(p, end='\r')
            m = hashlib.md5()
            m.update(read_data)
            if m.hexdigest() == hash.strip():
                pass
            else:
                CHANGE_COUNTER += 1
    print(p)
    print("%d blocks have changed. ~%d MB." % (CHANGE_COUNTER, (CHANGE_COUNTER * BLOCK_SIZE)/1000000))

