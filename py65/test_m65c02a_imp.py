import unittest
import os
import sys

sys.path.append(os.getcwd())

import tempfile
from monitor import Monitor

try:
    from StringIO import StringIO
except ImportError: # Python 3
    from io import StringIO


class M65C02A_Imp_AddressingMode_Tests(unittest.TestCase):

    # php
    
    def test_push_psw_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 php')
        self.assertEqual(0x08, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x30,  mpu.memory[0x1FF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FE, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0x08, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x10,  mpu.memory[0x17F])
        self.assertEqual(0x10,  mpu.p)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17E, mpu.sp[0])

    # plp
    
    def test_pull_psw_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0xCF
        mpu.sp[1] = 0x1FE
        self.assertEqual(0xCF,  mpu.memory[0x1FF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x1FE, mpu.sp[1])
        mon.do_assemble('200 plp')
        self.assertEqual(0x28, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0xCF,  mpu.memory[0x1FF])
        self.assertEqual(0xFF,  mpu.p)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17E
        mpu.memory[0x17F] = 0xEF
        self.assertEqual(0xEF, mpu.memory[0x17F])
        self.assertEqual(0x28, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0xDF,  mpu.p)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])

    # php.s
    
    def test_push_psw_on_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on auxiliary stack
        mpu.x[0] = 0xFF
        self.assertEqual(0x00,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x08    # PHP
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x08, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x30,  mpu.memory[0x0FF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])

    # plp.s
    
    def test_pull_psw_from_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from auxiliary stack
        mpu.memory[0xFF] = 0xCF
        mpu.x[0] = 0xFE
        self.assertEqual(0xCF,  mpu.memory[0xFF])
        self.assertEqual(0x30,  mpu.p)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x28    # PLP
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x28, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xCF,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0xFF,  mpu.p)
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])

    # pha
    
    def test_push_acc_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.a[0] = 0x0055
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 pha')
        self.assertEqual(0x48, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FE, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0x48, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17E, mpu.sp[0])

    # pla
    
    def test_pull_acc_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0xAA
        mpu.sp[1] = 0x1FE
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x1FE, mpu.sp[1])
        mon.do_assemble('200 pla')
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17E
        mpu.memory[0x17F] = 0x55
        self.assertEqual(0x55, mpu.memory[0x17F])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x68, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)

    # pha.s
    
    def test_push_acc_on_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on auxiliary stack
        mpu.x[0] = 0xFF
        mpu.a[0] = 0xC3
        self.assertEqual(0x00,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0xC3,  mpu.a[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x48    # PHA
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x48, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0xC3,  mpu.memory[0x0FF])
        self.assertEqual(0xC3,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])

    # pla.s
    
    def test_pull_acc_from_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from auxiliary stack
        mpu.memory[0xFF] = 0x3C
        mpu.x[0] = 0xFE
        self.assertEqual(0x3C,  mpu.memory[0xFF])
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x68    # PLA
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x3C,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x3C,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])
        
    # pha.w
    
    def test_push_acc_word_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.a[0] = 0xAA55
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.a[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 pha')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x48, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FD, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x48, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        self.assertEqual(0x00, mpu.memory[0x17F])
        self.assertEqual(0x00, mpu.memory[0x17E])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.memory[0x17E])
        self.assertEqual(0xAA55, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17D, mpu.sp[0])

    # pla.w
    
    def test_pull_acc_word_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0x55
        mpu.memory[0x1FE] = 0xAA
        mpu.sp[1] = 0x1FD
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x1FD, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 pla')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x55AA, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17D
        mpu.memory[0x17F] = 0xAA
        mpu.memory[0x17E] = 0x55
        self.assertEqual(0xAA, mpu.memory[0x17F])
        self.assertEqual(0x55, mpu.memory[0x17E])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA55, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x68, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,    mpu.p)

    # pha.sw
    
    def test_push_acc_word_on_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on auxiliary stack
        mpu.x[0] = 0xFF
        mpu.a[0] = 0xC3C2
        self.assertEqual(0x00,   mpu.memory[0x0FF])
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0xC3C2, mpu.a[0])
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FF,  mpu.x[0])
        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0x48    # PHA
        self.assertEqual(0xCB,   mpu.memory[0x200])
        self.assertEqual(0x48,   mpu.memory[0x201])
        self.assertEqual(0x00,   mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0xC3,   mpu.memory[0x0FF])
        self.assertEqual(0xC2,   mpu.memory[0x0FE])
        self.assertEqual(0xC3C2, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FD,  mpu.x[0])

    # pla.sw
    
    def test_pull_acc_word_from_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from auxiliary stack
        mpu.memory[0xFF] = 0x3C
        mpu.memory[0xFE] = 0x2C
        mpu.x[0] = 0xFD
        self.assertEqual(0x3C,   mpu.memory[0xFF])
        self.assertEqual(0x2C,   mpu.memory[0xFE])
        self.assertEqual(0x00,   mpu.a[0])
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FD,  mpu.x[0])
        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0x68    # PLA
        self.assertEqual(0xCB,   mpu.memory[0x200])
        self.assertEqual(0x68,   mpu.memory[0x201])
        self.assertEqual(0x00,   mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x3C,   mpu.memory[0x0FF])
        self.assertEqual(0x2C,   mpu.memory[0x0FE])
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0x3C2C, mpu.a[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FF,  mpu.x[0])
        
    # phy
    
    def test_push_y_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.y[0] = 0x0055
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 phy')
        self.assertEqual(0x5A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FE, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0x5A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17E, mpu.sp[0])

    # ply
    
    def test_pull_y_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0xAA
        mpu.sp[1] = 0x1FE
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x1FE, mpu.sp[1])
        mon.do_assemble('200 ply')
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17E
        mpu.memory[0x17F] = 0x55
        self.assertEqual(0x55, mpu.memory[0x17F])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0x7A, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)

    # phy.s
    
    def test_push_y_on_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on auxiliary stack
        mpu.x[0] = 0xFF
        mpu.y[0] = 0xC3
        self.assertEqual(0x00,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0xC3,  mpu.y[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x5A    # PHY
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x5A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0xC3,  mpu.memory[0x0FF])
        self.assertEqual(0xC3,  mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])

    # ply.s
    
    def test_pull_y_from_auxiliary_stack(self):
        #
        # TODO: add tests to set/clr NZ flags
        #
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from auxiliary stack
        mpu.memory[0xFF] = 0x3C
        mpu.x[0] = 0xFE
        mpu.y[0] = 0xFF00
        self.assertEqual(0x3C,  mpu.memory[0xFF])
        self.assertEqual(0xFF00, mpu.y[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FE, mpu.x[0])
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x7A    # PLY
        self.assertEqual(0x8B, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x3C,  mpu.memory[0x0FF])
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x3C,  mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x0FF, mpu.x[0])
        
    # phy.w
    
    def test_push_y_word_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.y[0] = 0xAA55
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.y[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 phy')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x5A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FD, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x5A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        self.assertEqual(0x00, mpu.memory[0x17F])
        self.assertEqual(0x00, mpu.memory[0x17E])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.memory[0x17E])
        self.assertEqual(0xAA55, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17D, mpu.sp[0])

    # ply.w
    
    def test_pull_y_word_from_default_stack(self):
        #
        # TODO: add tests to set/clr NZ flags
        #
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0x55
        mpu.memory[0x1FE] = 0xAA
        mpu.sp[1] = 0x1FD
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x0000, mpu.y[0])
        self.assertEqual(0x1FD, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 ply')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x55AA, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17D
        mpu.memory[0x17F] = 0xAA
        mpu.memory[0x17E] = 0x55
        self.assertEqual(0xAA, mpu.memory[0x17F])
        self.assertEqual(0x55, mpu.memory[0x17E])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA55, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0x7A, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)

    # phy.sw
    
    def test_push_y_word_on_auxiliary_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on auxiliary stack
        mpu.x[0] = 0xFF
        mpu.y[0] = 0xC3C2
        self.assertEqual(0x00,   mpu.memory[0x0FF])
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0xC3C2, mpu.y[0])
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FF,  mpu.x[0])
        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0x5A    # PHA
        self.assertEqual(0xCB,   mpu.memory[0x200])
        self.assertEqual(0x5A,   mpu.memory[0x201])
        self.assertEqual(0x00,   mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0xC3,   mpu.memory[0x0FF])
        self.assertEqual(0xC2,   mpu.memory[0x0FE])
        self.assertEqual(0xC3C2, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FD,  mpu.x[0])

    # ply.sw
    
    def test_pull_y_word_from_auxiliary_stack(self):
        #
        # TODO: add tests to set/clr NZ flags
        #
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from auxiliary stack
        mpu.memory[0xFF] = 0x3C
        mpu.memory[0xFE] = 0x2C
        mpu.x[0] = 0xFD
        self.assertEqual(0x3C,   mpu.memory[0xFF])
        self.assertEqual(0x2C,   mpu.memory[0xFE])
        self.assertEqual(0x00,   mpu.y[0])
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FD,  mpu.x[0])
        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0x7A    # PLY
        self.assertEqual(0xCB,   mpu.memory[0x200])
        self.assertEqual(0x7A,   mpu.memory[0x201])
        self.assertEqual(0x00,   mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x3C,   mpu.memory[0x0FF])
        self.assertEqual(0x2C,   mpu.memory[0x0FE])
        self.assertEqual(0x00,   mpu.memory[0x1FF])
        self.assertEqual(0x3C2C, mpu.y[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0x0FF,  mpu.x[0])
        
    # phx
    
    def test_push_x_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.x[0] = 0x0055
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 phx')
        self.assertEqual(0xDA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FE, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0xDA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17E, mpu.sp[0])

    # plx
    
    def test_pull_x_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0xAA
        mpu.sp[1] = 0x1FE
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x1FE, mpu.sp[1])
        mon.do_assemble('200 plx')
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17E
        mpu.memory[0x17F] = 0x55
        self.assertEqual(0x55, mpu.memory[0x17F])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x80
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FE
        mpu.memory[0x1FF] = 0x7F
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFA, mpu.memory[0x200])
        self.assertEqual(0x00, mpu.memory[0x201])
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7D,  mpu.p)

    # phx.w
    
    def test_push_x_word_on_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # push on kernal mode stack
        mpu.x[0] = 0xAA55
        self.assertEqual(0x00,  mpu.memory[0x1FF])
        self.assertEqual(0x00,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.x[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 phx')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xDA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x1FF])
        self.assertEqual(0x55,  mpu.memory[0x1FE])
        self.assertEqual(0xAA55, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FD, mpu.sp[1])
        # push on user mode stack
        mpu.p = 0x10
        mpu.sp[0] = 0x17F
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xDA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        self.assertEqual(0x00, mpu.memory[0x17F])
        self.assertEqual(0x00, mpu.memory[0x17E])
        mon.do_goto('200')
        self.assertEqual(0xAA,  mpu.memory[0x17F])
        self.assertEqual(0x55,  mpu.memory[0x17E])
        self.assertEqual(0xAA55, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17D, mpu.sp[0])

    # plx.w
    
    def test_pull_x_word_from_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # pull from kernal mode stack
        mpu.memory[0x1FF] = 0x55
        mpu.memory[0x1FE] = 0xAA
        mpu.sp[1] = 0x1FD
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x1FD, mpu.sp[1])
        mon.do_assemble('200 siz')
        mon.do_assemble('201 plx')
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.memory[0x1FF])
        self.assertEqual(0xAA,  mpu.memory[0x1FE])
        self.assertEqual(0x55AA, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        # pull from user mode stack
        mpu.p = 0x10    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x17D
        mpu.memory[0x17F] = 0xAA
        mpu.memory[0x17E] = 0x55
        self.assertEqual(0xAA, mpu.memory[0x17F])
        self.assertEqual(0x55, mpu.memory[0x17E])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0xAA55, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x17F, mpu.sp[0])
        #
        # test NZ flags are modified appropriately when loading A from stack
        #       there are three valid combinations of NZ: 00, 01, 10. The 11
        #       is no valid; it can be generated by loading P from the stack,
        #       and there is no trap for this specific invalid combination of
        #       the NZ flags.
        #
        #       00  =>  01  : load 0
        #           =>  10  : load negative
        #           =>  00  : load non-zero, positive
        #
        #       01  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        #       10  =>  01  : load 0
        #           =>  10  : load negative 
        #           =>  00  : load non-zero, positive
        #
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x00
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x00, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x80
        mpu.memory[0x1FE] = 0x00
        self.assertEqual(0x80, mpu.memory[0x1FF])
        self.assertEqual(0x00, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0xFD,   mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.sp[1] = 0x1FD
        mpu.memory[0x1FF] = 0x7F
        mpu.memory[0x1FE] = 0xFF
        self.assertEqual(0x7F, mpu.memory[0x1FF])
        self.assertEqual(0xFF, mpu.memory[0x1FE])
        self.assertEqual(0xAB, mpu.memory[0x200])
        self.assertEqual(0xFA, mpu.memory[0x201])
        self.assertEqual(0x00, mpu.memory[0x202])
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.x[0])
        self.assertEqual(0x202,  mpu.pc)
        self.assertEqual(0x1FF,  mpu.sp[1])
        self.assertEqual(0x7D,   mpu.p)

    # clc
    
    def test_clear_carry(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x31
        self.assertEqual(0x31, mpu.p)
        mon.do_assemble('200 clc')
        self.assertEqual(0x18, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x30, mpu.p)
        
    # sec
    
    def test_set_carry(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x30
        self.assertEqual(0x30, mpu.p)
        mon.do_assemble('200 sec')
        self.assertEqual(0x38, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x31, mpu.p)

    # cli
    
    def test_clear_interrupt_flag(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x34
        self.assertEqual(0x34, mpu.p)
        mon.do_assemble('200 cli')
        self.assertEqual(0x58, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x30, mpu.p)
        
    # sei
    
    def test_set_interrupt_flag(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x30
        self.assertEqual(0x30, mpu.p)
        mon.do_assemble('200 sei')
        self.assertEqual(0x78, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x34, mpu.p)

    # clv
    
    def test_clear_overflow_flag(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x70
        self.assertEqual(0x70, mpu.p)
        mon.do_assemble('200 clv')
        self.assertEqual(0xB8, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x30, mpu.p)

    # cld
    
    def test_clear_decimal_flag(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x38
        self.assertEqual(0x38, mpu.p)
        mon.do_assemble('200 cld')
        self.assertEqual(0xD8, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x30, mpu.p)
        
    # sed
    
    def test_set_decimal_flag(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.p = 0x30
        self.assertEqual(0x30, mpu.p)
        mon.do_assemble('200 sed')
        self.assertEqual(0xF8, mpu.memory[0x200])
        mon.do_goto('200')
        self.assertEqual(0x38, mpu.p)

    # tya
    
    def test_trasfer_y_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0xFFFF
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x7FFF
        mpu.a[0] = 0x0000
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x0000
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x7FFF
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x98    # TYA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
    
    # tay
    
    def test_trasfer_a_to_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x7FFF
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.y[0] = 0x7FFF
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x7FFF
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0xFFFF
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.y[0] = 0x0000
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x0000
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x8000
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.y[0] = 0x8000
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x8000
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
    
    # txa
    
    def test_trasfer_x_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x7FFF
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0xFFFF
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x7FFF
        mpu.a[0] = 0x0000
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x0000
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x7FFF
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x8000
        mpu.memory[0x200] = 0x8A    # TXA
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.a[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
    
    # tax
    
    def test_trasfer_a_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0xFFFF
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] - 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.x[0] = 0x0000
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x0000
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)

    # txs
    
    def test_transfer_x_to_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # Transfer x to s - kernel mode
        mpu.p = 0xFD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        mpu.memory[0x200] = 0x9A    # TXS
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x000, mpu.sp[0])
        self.assertEqual(0xFD,  mpu.p)
        # Transfer x to s - kernel mode
        mpu.p = 0xDD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x8000
        mpu.memory[0x200] = 0x9A    # TXS
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.sp[1])
        self.assertEqual(0x1FF,  mpu.sp[0])
        self.assertEqual(0xDD,   mpu.p)
        
    # tsx
    
    def test_transfer_s_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        # Transfer s to x - kernel mode
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x80FF
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x7FFF
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0xFFFF
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] - 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x7FFF
        mpu.x[0] = 0x0000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x0000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x8000
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x7FFF
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0xFF55
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test transfer of s to x in user mode
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0xFF7F
        mpu.x[0] = 0x8000
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x5D,  mpu.p)

    # txu
    
    def test_transfer_x_to_u(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x9A    # TXS
        mpu.memory[0x202] = 0x00
        # Transfer x to u - kernel mode
        mpu.p = 0xFD
        mpu.x[0]  = 0x007F
        mpu.sp[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x17F, mpu.sp[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # Transfer x to u - user mode
        mpu.p = 0xDD
        mpu.x[0]  = 0x0080
        mpu.sp[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x180, mpu.sp[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xDD,  mpu.p)
        
    # tux
    
    def test_transfer_u_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0xBA    # TSX
        mpu.memory[0x202] = 0x00
        # Transfer s to x - kernel mode
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x5F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x8080
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x80,  mpu.x[0])
        self.assertEqual(0xDD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x5D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x5F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x5F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x5F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x7FFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xDD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x5F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x5D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x8000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x5F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x7FFF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0xDD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0xFF55
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x5D,  mpu.p)

    # tsa (oax tsx) [tsa (osx txa)]
    
    def test_transfer_s_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xBA    # TXS
        mpu.memory[0x202] = 0x00
        mpu.sp[0] = 0x017F
        mpu.sp[1] = 0x01FD
        # test transfer s to a in kernel mode: sp[1] => a[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0xFD,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        # test transfer s to a in user mode: sp[0] => a
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
    
    # tas (oax txs) [tas (osx tax)]
    
    def test_transfer_a_to_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0x9A    # TXS
        mpu.memory[0x202] = 0x00
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        # test transfer a to s in kernel mode: a[0] => sp[1]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x202, mpu.pc)
        # test transfer a to s in user mode: a[0] => sp[0]
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFF7F
        mon.do_goto('200')
        self.assertEqual(0x17F, mpu.sp[0])
        self.assertEqual(0x202, mpu.pc)
    
    # tua (oax ind tsx) [tua (osx ind txa)]
    
    def test_transfer_u_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0x9B    # IND
        mpu.memory[0x202] = 0xBA    # TSX
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x017F
        mpu.sp[1] = 0x01FD
        # test transfer u to a in kernel mode: sp[0] => a[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.a[0])
        self.assertEqual(0x203, mpu.pc)
    
    # tau (oax ind txs) [tau (osx ind tax)]
    
    def test_transfer_a_to_u(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0x9B    # IND
        mpu.memory[0x202] = 0x9A    # TXS
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        # test transfer a to u in kernel mode: a[0] => sp[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x1FF, mpu.sp[0])
        self.assertEqual(0x203, mpu.pc)
      
    # txy (oay txa)
    
    def test_transfer_x_to_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xFB    # OAY
        mpu.memory[0x201] = 0x8A    # TXA
        mpu.memory[0x202] = 0x00
        mpu.x[0] = 0xFFFF
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
    
    # tyx (oay tax)

    def test_transfer_y_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0x98    # TYA
        mpu.memory[0x202] = 0x00
        mpu.y[0] = 0xFFFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
    
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
