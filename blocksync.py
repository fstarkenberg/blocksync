#!/usr/bin/env python3

import sys
import os
import hashlib

BLOCK_DEVICE = 'disk'
BLOCK_SIZE = 4096

def DEVICE_SIZE(BLOCK_DEVICE):
	with open(BLOCK_DEVICE, 'rb') as f:
		f.seek(0, 2)
		SIZE = f.tell()
	return SIZE

def progress(SIZE, CURRENT):
    #return int(CURRENT/SIZE * 100)
	SIZE_GB = int(SIZE/1000000000)
	CURRENT_GB = int(CURRENT/1000000000)
	print("%d/%d" % (CURRENT_GB, SIZE_GB), end='\r')

if len(sys.argv) < 2:
    print("USAGE: %s --generate | --compare /dev/blkdevice" % sys.argv[0])
    sys.exit(0)

SIZE = DEVICE_SIZE(BLOCK_DEVICE)

if sys.argv[1] == '--generate':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'w') as h:
        while f.tell() < SIZE:
            progress(SIZE, f.tell())
            read_data = f.read(BLOCK_SIZE)
            m = hashlib.md5()
            m.update(read_data)
            h.write(m.hexdigest())
            h.write('\n')

elif sys.argv[1] == '--compare':
    with open(BLOCK_DEVICE, 'rb') as f, open('disk.md5', 'r') as h:
        CHANGE_COUNTER = 0
        for hash in h.readlines():
            read_data = f.read(BLOCK_SIZE)
            m = hashlib.md5()
            m.update(read_data)
            if m.hexdigest() == hash.strip():
                pass
            else:
                CHANGE_COUNTER += 1
    print("%d blocks have changed" % CHANGE_COUNTER)

