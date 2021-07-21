# Utility for development purpose, to covert a usbmon log, filtered for the
# trophy device to a raw image buffer, for example to compare the raw data with
# the same gathered from proprietary software. (For usbmon details see README.
# Make sure to use a buffer length of 65536 in usbmon.c)

import sys
from rvg5200 import trophyrvg

def log2buf(flnm):
    with open(flnm) as fp:
        isdata = False
        buf = []
        for l in fp.readlines():
            toks = l.split()
            if isdata:
                buf = buf + [ bytes.fromhex(t)  for t in toks ]
                isdata = False
            elif toks[1] == 'C' and toks[2] == 'Bi' and toks[-1] == 'OK':
                isdata = True
        return b''.join(buf)

if __name__=='__main__':
    trophyrvg.buf2img( log2buf(sys.argv[1]), 'fromlog.png' )
