#!/usr/bin/env python3

import usb.core
import sys
import time

# TODO: Provide a CLI option to set dbg
dbg = False

def str2hexl(l): return [ int(s,16) for s in l ]
def pdbg(*arg):
    if dbg: print(*arg)

class usbmonq:
    def playe(self,dev,e):
        ev,ed = e
        et = ev[1]
        urbt = ev[2]
        args = ev[3:]
        if et != 'S': pdbg('skipping event type',et)
        else:
            try: player = getattr(dev,'play_'+urbt)
            except Exception as e:
                print('unhandled urbt',urbt,e)
                sys.exit()
            player(args,ed)
    def play(self,dev):
        pdbg('playing',self.flnm)
        for e in self.events: self.playe(dev,e)
    def formevents(self,lines): return [] if lines == [] else \
        [ (lines[0].split(),[]) ] if len(lines) == 1 else \
        [ (lines[0].split(),lines[1].split()) ] + self.formevents(lines[2:]) if lines[1][0] == ' ' else \
        [ (lines[0].split(),[]) ] + self.formevents(lines[1:])
    def __init__(self,flnm):
        self.flnm = flnm
        with open(flnm) as fd:
            self.events = self.formevents(list(l.rstrip() for l in fd.readlines()))

class usbdev:
    def play_Ci(self,args,ed):
        pdbg('Ci',args)
        ret = self.dev.ctrl_transfer(*str2hexl(args[1:]))
        pdbg('resp',ret)
    def play_Co(self,args,ed):
        pdbg('Co',args,ed)
        ret = self.dev.ctrl_transfer(*str2hexl(args[1:-1]),str2hexl(ed))
        pdbg('resp',ret)
    def play_Ii(self,args,ed):
        pdbg('Ii playback not hndled',args,ed)
    def dumpif(self):
        for cfg in self.dev:
            for inf in cfg:
                print(inf)
                print('-------------------------------------------')
            print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    def __init__(self,vendorid,productid,inittracefiles=[]):
        self.dev = usb.core.find(idVendor=vendorid,idProduct=productid)
        if not self.dev:
            raise(Exception('Device not found',hex(vendorid)+':'+hex(productid)))
        if self.dev.is_kernel_driver_active(0):
            pdbg('detaching kernel driver')
            self.dev.detach_kernel_driver(0)
        self.dev.reset()
        self.dev.set_configuration()
        usb.util.claim_interface(self.dev,0)
        for f in inittracefiles: usbmonq(f).play(self)

class kodakrvg5200(usbdev):
    vendorid = 0x082b
    productid = 0x000c
    def __init__(self):
        super().__init__(self.vendorid,self.productid,['dev1init'])
        time.sleep(3)

from threading import Thread
import png
import struct
class trophyrvg(usbdev):
    vendorid = 0x082b
    productid = 0x100a
    intrport = 0x81
    bulkinport = 0x82
    width = 1168
    height = 1562
    sensordepth = 12
    depth = 12 # Can set to 8 as screen's pixel depth is typically 8, but transformations may benefit from 12
    concedebits = sensordepth - depth
    bytsperpixel = 2

    # pixel size spec doesn't help get correct calibration
    # pixel_size = 19 # micrometer
    # pixels_per_meter = int( pow(10,6) / pixel_size )

    # line pairs spec doesn't help get correct calibration
    # linepairs_permm = 16
    # pixels_per_meter = 2 * linepairs_permm * pow(10,3)

    # worked out from jpeg header of image exported on windows and confirmed that with x ray of a coin
    pixels_per_meter = 52598
    bufsz = width * height * bytsperpixel
    maxpxlval = (1<<depth) - 1
    def _play_Ii(self):
        try: self.dev.read(self.intrport,2)
        except Exception as e: pdbg('playIibg:',e)
    def play_Ii(self,args,ed):
        pdbg('Playing Ii in bg',args,ed)
        self.bgthread.start()
        pdbg('launched in bg')
    @classmethod
    def buf2img(self,buf,opfile):
        negbuf = [ self.maxpxlval - ( v[0] >> self.concedebits )
            for v in struct.iter_unpack('<H',buf)
            ]
        arr2d = [ list(reversed(negbuf[ i : i + self.width ]))
            for r in range(self.height) for i in [ r * self.width ]
            ]
        with open(opfile,'wb') as fp: png.Writer(
            width = self.width,
            height = self.height,
            greyscale = True,
            bitdepth = self.depth,
            x_pixels_per_unit = self.pixels_per_meter,
            y_pixels_per_unit = self.pixels_per_meter,
            unit_is_meter = True,
            ).write(fp,arr2d)
    def shoot(self,opfile='rvg.png'):
        # TODO: For unknown reason this is to be done twice, but check if once also works
        for i in range(2):
            while True:
                try:
                    ret = self.dev.read(self.intrport,2)
                    pdbg('intr resp',ret)
                    break
                except Exception as e:
                    print('Ready to shoot...')
        # TODO: Will the reads be always 2 is not known, no issues seen till now
        buf = self.dev.read(self.bulkinport,self.bufsz) + self.dev.read(self.bulkinport,self.bufsz)
        if(True): # TODO: Later on make it if(dbg)
            with open('raw.rvg','wb') as fp: buf.tofile(fp)
        self.buf2img(buf,opfile)
    def __init__(self):
        self.bgthread = Thread(target=self._play_Ii)
        super().__init__(self.vendorid,self.productid,['dev2init'])
        self.bgthread.join()
        self.shoot()

if __name__=='__main__':
    print('Initializing, please wait for "Ready to shoot" message')
    try: kodakrvg5200()
    except Exception as e:
        print('kodakrvg5200 device may be already initialized or absent, trying trophyrvg...',e)

    try: trophyrvg()
    except Exception as e:
        print('either the device is absent or not initialized properly',e)
