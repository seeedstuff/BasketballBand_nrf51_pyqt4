#!/usr/bin/python

#import pexpect
#from pexpect.popen_spawn import PopenSpawn
import subprocess
import os
import tempfile

class Printer(object):
    
    def __init__(self):
        pass
        
    def print_text(self, text):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('SIZE 40 mm, 10 mm\r\n')
        f.write('GAP 2 mm, 0 mm\r\n')
        f.write('CLS\r\n')
        f.write('TEXT 0,0,"3",0,1,1, "%s"\r\n' % text)
        f.write('PRINT 1,1\r\n')
        f.flush()
        f.close()
        os.system('copy ' + f.name + ' \\\\127.0.0.1\\printer')
        os.unlink(f.name)
        #os.system('copy C:\\Users\\ant\\Desktop\\basketball\\print_text.txt \\\\127.0.0.1\\printer')
        
    def print_qrcode(self, text):
        f = tempfile.NamedTemporaryFile(delete=False)
        f.write('SIZE 40 mm, 10 mm\r\n')
        f.write('GAP 2 mm, 0 mm\r\n')
        f.write('CLS\r\n')
        # f.write('QRCODE 4,16,L,2,A,0,1,1,"%s"\r\n' % text)
        f.write('QRCODE 180,16,L,2,A,0,1,1,"%s"\r\n' % text)
        f.write('PRINT 1,1\r\n')
        f.flush()
        f.close()
        os.system('copy ' + f.name + ' \\\\127.0.0.1\\printer')
        os.unlink(f.name)

if __name__ == '__main__':
    printer = Printer()
    printer.print_qrcode('mac: 00-01-02-03-04-05 uuid:0123456789012345')