import unittest
import os
import sys
import copy

sys.path.append(os.getcwd())

import tempfile
from monitor import Monitor

try:
    from StringIO import StringIO
except ImportError: # Python 3
    from io import StringIO


class M65C02A_Imp_AddressingMode_Tests(unittest.TestCase):

    # rti
    
    def test_return_from_interrupt_using_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        self.assertEqual(0x30, mpu.p)    # Interrupts Kernel Mode Only
        mpu.sp = {0 : 0x1FF, 1 : 0x1FC}

        mpu.memory[0x200] = 0x40    # RTI
        mpu.memory[0x201] = 0xEA    # NOP
        mpu.memory[0x202] = 0x00

        mpu.memory[0x1FF] = 0x02    # PCH
        mpu.memory[0x1FE] = 0x00    # PCL
        mpu.memory[0x1FD] = 0xD3    # P

        p = 0xD3
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x1FF, 1 : 0x1FF}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        
        mon.do_goto('200')
        
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
        mpu.p = 0x30                # Interrupts Kernel Mode Only
        mpu.sp = {0 : 0x1FF, 1 : 0x1FD}

        mpu.memory[0x100] = 0x02    # PCH
        mpu.memory[0x1FF] = 0x00    # PCL
        mpu.memory[0x1FE] = 0xDF    # P

        p = 0xDF
        s = {0 : 0x1FF, 1 : 0x100}
        
        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

    # rts

    def test_return_from_subroutine_using_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.sp = {0 : 0x1FF, 1 : 0x1FD}

        mpu.memory[0x200] = 0x60    # RTS
        mpu.memory[0x201] = 0xEA    # NOP
        mpu.memory[0x202] = 0x00

        mpu.memory[0x1FF] = 0x02    # PCH
        mpu.memory[0x1FE] = 0x00    # PCL

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x1FF, 1 : 0x1FF}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        
        mon.do_goto('200')
        
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
        mpu.p = 0x10
        mpu.sp = {0 : 0x2FE, 1 : 0x1FF}

        mpu.memory[0x300] = 0x02    # PCH
        mpu.memory[0x2FF] = 0x00    # PCL

        p = 0x10
        s = {0 : 0x300, 1 : 0x1FF}
        
        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
    
    # rsv1

    def test_reserved_1(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x22    # RSV1
        mpu.memory[0x201] = 0x01
        mpu.memory[0x202] = 0x00
        
        mon.do_goto('200')
        
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rsv2

    def test_reserved_2(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x42    # RSV2
        mpu.memory[0x201] = 0x02
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rsv3

    def test_reserved_3(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x62    # RSV3
        mpu.memory[0x201] = 0x03
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rsv4

    def test_reserved_4(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x82    # RSV4
        mpu.memory[0x201] = 0x04
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

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

    # dey [NZ]

    def test_decrement_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = {0 : 0x00FF, 1 : 0x0000, 2 : 0x0000}
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x88    # DEY
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.y = {0 : 0x0001, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(y[j], mpu.y[j])

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
        mpu.memory[0x200] = 0xA8    # TAY
        mpu.memory[0x201] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.y[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
    
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

    # iny [NZ]

    def test_increment_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.y = {0 : 0x007F, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = {0 : 0x0080, 1 : 0x0000, 2 : 0x0000}
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xC8    # INY
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.y = {0 : 0x01FF, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(y[j], mpu.y[j])

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
        
    # inx [NZ]

    def test_increment_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.x = {0 : 0x007F, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = {0 : 0x0080, 1 : 0x0000, 2 : 0x0000}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xE8    # INX
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.x = {0 : 0x01FF, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        x = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])

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
    
    # txs
    
    def test_transfer_x_to_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0x9A    # TXS
        mpu.memory[0x201] = 0x00
        # Transfer x to s - kernel mode
        mpu.p = 0xFD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x01FF, mpu.sp[1])
        self.assertEqual(0x0000, mpu.sp[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # Transfer x to s - kernel mode
        mpu.p = 0xDD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.sp[1])
        self.assertEqual(0x01FF, mpu.sp[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xDD, mpu.p)
        
    # tax
    
    def test_trasfer_a_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAA    # TAX
        mpu.memory[0x201] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)

    # tsx
    
    def test_transfer_s_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xBA    # TSX
        mpu.memory[0x201] = 0x00
        # Transfer s to x - kernel mode
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x80FF
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x7FFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x8000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x00,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7F,  mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x7FFF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFF,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0xFF55
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x55,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x7D,  mpu.p)
        # test transfer of s to x in user mode
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0xFF7F
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x7F,  mpu.x[0])
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x5D,  mpu.p)

    # dex [NZ] 

    def test_decrement_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.x = {0 : 0x0200, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = {0 : 0x00FF, 1 : 0x0000, 2 : 0x0000}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xCA    # DEX
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.x = {0 : 0x0101, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        x = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])

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

    # nop

    def test_nop(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.memory[0x200] = 0xEA    # NOP
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

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

    # nxt

    def test_Forth_VM_next(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        codeFieldPtr = 0x202
        mpu.ip = codeFieldPtr       # Codefield Pointer

        mpu.memory[0x200] = 0x3B    # NXT
        mpu.memory[0x201] = 0x00
        mpu.memory[0x202] = 0x04    # Pointer to codeField
        mpu.memory[0x203] = 0x02
        mpu.memory[0x204] = 0xEA    # codeField: NOP
        mpu.memory[0x205] = 0x00

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = mpu.ip + 2
        w = mpu.wordMask & ( (mpu.memory[codeFieldPtr+1] << 8) \
                            + mpu.memory[codeFieldPtr])

        mon.do_goto('200')
        
        self.assertEqual(0x205, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
    # phi
    
    def test_push_word_ip_to_default_stack_X(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x = {0 : 0x17F, 1 : 0x4444, 2 : 0x2222}
        mpu.ip = 0x5AA5

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x017D, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x4B    # PHI
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(0x5A, mpu.memory[0x17F])
        self.assertEqual(0xA5, mpu.memory[0x17E])
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    #ini
    
    def test_word_increment_ip(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.ip = 0xFFFF

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = mpu.wordMask & (mpu.ip + 1)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x5B    # INI
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    #pli
    
    def test_pull_word_ip_from_default_stack_X(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x = {0 : 0x17D, 1 : 0x4444, 2 : 0x2222}
        mpu.ip = 0x0000
        mpu.memory[0x17F] = 0x5A
        mpu.memory[0x17E] = 0xA5

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x017F, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x5AA5
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x6B    # PLI
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ent
    
    def test_Forth_VM_enter_using_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        codeFieldPtr = 0x202
        mpu.ip = codeFieldPtr       # Codefield Pointer
        mpu.x = {0 : 0x17F, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x200] = 0x3B    # NXT - Primary Forth WORD Exit (pli nxt)
        mpu.memory[0x201] = 0x00
        # Forth WORD - Secondary Code Field
        mpu.memory[0x202] = 0x05    # Pointer to header #1
        mpu.memory[0x203] = 0x02
        mpu.memory[0x204] = 0x00    # Pointer to header #2 (partial)
        # Forth WORD - Secondary
        mpu.memory[0x205] = 0x7B    # header: ENT (Secondary WORD)
        mpu.memory[0x206] = 0x00
        mpu.memory[0x207] = 0x0D    # Pointer to header #1
        mpu.memory[0x208] = 0x02
        mpu.memory[0x209] = 0x00    # Pointer to header #2 (not implemented)
        mpu.memory[0x20A] = 0x00
        mpu.memory[0x20B] = 0x00    # Pointer to header #3 (not implemented)
        mpu.memory[0x20C] = 0x00
        # Forth WORD - Primitive
        mpu.memory[0x20D] = 0x80    # header: bra $+2
        mpu.memory[0x20E] = 0x00
        mpu.memory[0x20F] = 0x00 

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x17D, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x209
        w = 0x20D

        mon.do_goto('200')
        
        self.assertEqual(0x20F, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # osx

    def test_osx(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.oax = True
        mpu.oay = True
        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(True, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ind

    def test_ind(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.ind)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.ind)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # siz

    def test_siz(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.memory[0x200] = 0xAB    # IND
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.siz)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.siz)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # isz

    def test_isz(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.memory[0x200] = 0xBB    # ISZ
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.ind)
        self.assertEqual(True, mpu.siz)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.ind)
        self.assertEqual(False, mpu.siz)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # osz

    def test_osz(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.oax = True
        mpu.oay = True
        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.osx)
        self.assertEqual(True, mpu.siz)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(True, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.siz)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ois

    def test_ois(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.oax = True
        mpu.oay = True
        mpu.memory[0x200] = 0xDB    # OSZ
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.osx)
        self.assertEqual(True, mpu.ind)
        self.assertEqual(True, mpu.siz)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(True, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.ind)
        self.assertEqual(False, mpu.siz)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # oax

    def test_oax(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.osx = True
        mpu.oay = True
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(True,  mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # oay

    def test_oay(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        mpu.osx = False
        mpu.oax = True
        mpu.memory[0x200] = 0xFB    # OAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(True, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        
        mpu.osx = True
        mpu.oax = False
        mpu.memory[0x200] = 0xFB    # OAY
        mpu.memory[0x201] = 0x00
        mon.do_goto('200')
        self.assertEqual(True, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(True, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        mpu.memory[0x200] = 0xEA    # NOP
        mon.do_goto('200')
        self.assertEqual(False, mpu.osx)
        self.assertEqual(False, mpu.oax)
        self.assertEqual(False, mpu.oay)
        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
    # txu (ind txs)
    
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
        
    # tux (ind tsx)
    
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

    # tai (ind dup)

    def test_word_transfer_a_to_ip(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}
        mpu.ip = 0x5555
        p = copy.copy(mpu.p)
        a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x8888
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x0B    # DUP A
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # bsw (ind swp)

    def test_byte_swap_TOS_register_stack_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x7FFF, 1 : 0x4444, 2 : 0x2222}
        p = copy.copy(mpu.p)
        a = {0 : 0xFF7F, 1 : 0x4444, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x1B    # SWP A
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rev (ind rot)

    def test_reverse_TOS_register_stack_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8CAE, 1 : 0x4444, 2 : 0x2222}
        p = copy.copy(mpu.p)
        a = {0 : 0x7531, 1 : 0x4444, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x2B    # ROT A
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # inxt (ind nxt)

    def test_Forth_VM_indirect_next(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        codeFieldPtr = 0x203
        mpu.ip = codeFieldPtr       # Codefield Pointer

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x3B    # NXT
        mpu.memory[0x202] = 0x00
        mpu.memory[0x203] = 0x05    # Pointer to pointer to codeField
        mpu.memory[0x204] = 0x02
        mpu.memory[0x205] = 0x06    # Pointer to codeField
        mpu.memory[0x206] = 0x02
        mpu.memory[0x207] = 0xEA    # codeField: NOP
        mpu.memory[0x208] = 0x00

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = mpu.ip + 2
        w = mpu.wordMask & ( (mpu.memory[codeFieldPtr+1] << 8) \
                            + mpu.memory[codeFieldPtr])

        mon.do_goto('200')
        
        self.assertEqual(0x208, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
    
    # phw (ind phi)
    
    def test_push_word_wp_to_default_stack_X(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x = {0 : 0x17F, 1 : 0x4444, 2 : 0x2222}
        mpu.wp = 0x5AA5

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x017D, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x4B    # PHI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x5A, mpu.memory[0x17F])
        self.assertEqual(0xA5, mpu.memory[0x17E])
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # inw (ind ini)
    
    def test_word_increment_wp(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.wp = 0xFFFF

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = mpu.wordMask & (mpu.wp + 1)

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x5B    # INI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    #plw (ind pli)
    
    def test_pull_word_wp_from_default_stack_X(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x = {0 : 0x17D, 1 : 0x4444, 2 : 0x2222}
        mpu.wp = 0x0000
        mpu.memory[0x17F] = 0x5A
        mpu.memory[0x17E] = 0xA5

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x017F, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = 0x5AA5

        mpu.memory[0x200] = 0x9B    # IND
        mpu.memory[0x201] = 0x6B    # PLI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ient (ind ent)

    def test_Forth_VM_indirect_enter_using_default_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x[0] = 0x17D

        # ITC Forth Exit
        mpu.memory[0x200] = 0x6B    # PLI - Forth WORD Indirect Exit (ind inxt)
        # ITC Forth Next
        mpu.memory[0x201] = 0x9B    # IND
        mpu.memory[0x202] = 0x3B    # NXT
        # ITC Forth Enter
        mpu.memory[0x203] = 0x9B    # IND - Forth WORD Indirect Enter (ind ent)
        mpu.memory[0x204] = 0x7B    # ENT
        # Forth WORD - Secondary Code Field
        mpu.memory[0x205] = 0x07    # Pointer to header #1
        mpu.memory[0x206] = 0x02
        # Forth WORD - Secondary
        mpu.memory[0x207] = 0x03    # header: IND (Secondary WORD)
        mpu.memory[0x208] = 0x02    # header: ENT (Secondary WORD)
        mpu.memory[0x209] = 0x0D    # Pointer to header #1
        mpu.memory[0x20A] = 0x02
        mpu.memory[0x20B] = 0x00    # Pointer to header #2 (not implemented)
        mpu.memory[0x20C] = 0x00
        # Forth WORD - Primitive
        mpu.memory[0x20D] = 0x0F    # header: pointer to code field
        mpu.memory[0x20E] = 0x02
        mpu.memory[0x20F] = 0x00 
        # Forth Return Stack
        mpu.memory[0x17D] = 0x00
        mpu.memory[0x17E] = 0x05    # header: pointer to code field
        mpu.memory[0x17F] = 0x02 

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x20B
        w = 0x20D

        mon.do_goto('200')
        
        self.assertEqual(0x07, mpu.memory[0x17E])
        self.assertEqual(0x02, mpu.memory[0x17F])
        self.assertEqual(0x20F, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
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

    # dey.w (siz dey) [NZ]

    def test_word_decrement_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = {0 : 0xFFFF, 1 : 0x0000, 2 : 0x0000}
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0x88    # DEY
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.y = {0 : 0x0001, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(y[j], mpu.y[j])

    # tya.w (siz tya)
    
    def test_word_trasfer_y_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0x98    # TYA
        mpu.memory[0x202] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.a[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x0000
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0xFFFF
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.y[0] = 0x5555
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
    
    # tay.w (siz tay)
    
    def test_word_trasfer_a_to_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xA8    # TAY
        mpu.memory[0x202] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.y[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.y[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
    
    # iny.w (siz iny) [NZ]

    def test_word_increment_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.y = {0 : 0x7FFF, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = {0 : 0x8000, 1 : 0x0000, 2 : 0x0000}
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xC8    # INY
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.y = {0 : 0xFFFF, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        y = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(y[j], mpu.y[j])

    # inx.w (siz inx) [NZ]

    def test_word_increment_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.x = {0 : 0x7FFF, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = {0 : 0x8000, 1 : 0x0000, 2 : 0x0000}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xE8    # INX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.x = {0 : 0xFFFF, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        x = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])

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

    # txa.w (siz txa)
    
    def test_word_trasfer_x_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0x8A    # TXA
        mpu.memory[0x202] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.a[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x0000
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000,  mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0xFFFF
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.x[0] = 0x5555
        mpu.a[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.a[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
    
    # txs.w (siz txs)
    
    def test_word_transfer_x_to_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0x9A    # TXS
        mpu.memory[0x202] = 0x00
        # Transfer x to s - kernel mode
        mpu.p = 0xFD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x00FF, mpu.sp[1])
        self.assertEqual(0x0000, mpu.sp[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # Transfer x to s - kernel mode
        mpu.p = 0xDD
        mpu.x[0]  = 0x00FF
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x8000, mpu.sp[1])
        self.assertEqual(0x00FF, mpu.sp[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xDD, mpu.p)
        
    # tax.w (siz tax)
    
    def test_word_trasfer_a_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xAA    # TAX
        mpu.memory[0x202] = 0x00
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x0000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xFFFF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x5555
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)

    # tsx.w (siz tsx)
    
    def test_transfer_s_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xBA    # TSX
        mpu.memory[0x202] = 0x00
        # Transfer s to x - kernel mode
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x80FF
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x80FF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0xFFFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x0000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0xFFFF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[1] = 0x7F55
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x7F55, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test transfer of s to x in user mode
        mpu.p = 0xDD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x07FF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x07FF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x5D, mpu.p)

    # dex.w (siz dex) [NZ]

    def test_word_decrement_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.x = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = {0 : 0xFFFF, 1 : 0x0000, 2 : 0x0000}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0xCA    # DEX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.x = {0 : 0x0001, 1 : 0x0000, 2 : 0x0000}
        p = psw | mpu.ZERO
        x = {0 : 0x0000, 1 : 0x0000, 2 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])

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

    # tia (siz dup)

    def test_word_transfer_ip_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}
        mpu.ip = 0x5555
        p = copy.copy(mpu.p)
        a = {0 : 0x5555, 1 : 0x4444, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x5555
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xAB    # SIZ
        mpu.memory[0x201] = 0x0B    # DUP A
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # txu.w (isz txs)
    
    def test_word_transfer_x_to_u(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xBB    # ISZ
        mpu.memory[0x201] = 0x9A    # TXS
        mpu.memory[0x202] = 0x00
        # Transfer x to u - kernel mode
        mpu.p = 0xFD
        mpu.x[0]  = 0x007F
        mpu.sp[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x007F, mpu.sp[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD,  mpu.p)
        # Transfer x to u - user mode
        mpu.p = 0xDD
        mpu.x[0]  = 0x0080
        mpu.sp[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x0080, mpu.sp[0])
        self.assertEqual(0x1FF, mpu.sp[1])
        self.assertEqual(0xDD, mpu.p)
        
    # tux.w (isz tsx)
    
    def test_word_transfer_u_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xBB    # ISZ
        mpu.memory[0x201] = 0xBA    # TSX
        mpu.memory[0x202] = 0x00
        # Transfer u to x - kernel mode
        # test NZ 00 => 01 when loading 0
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x0000
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 00 => 10 when loading negative
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x8080
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x8080, mpu.x[0])
        self.assertEqual(0xFD, mpu.p)
        # test NZ 00 => 00 when loading non-zero, positive
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x5555
        mpu.x[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 01 => 01 when loading 0
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x0000
        mpu.x[0] = 0xFFFF
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 01 => 10 when loading negative
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0xEFFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xEFFF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 01 => 00 when loading non-zero, positive
        mpu.p = 0x7F    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x5555
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)
        # test NZ 10 => 01 when loading 0
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x0000
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x0000, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7F, mpu.p)
        # test NZ 10 => 10 when loading negative
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x80FF
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x80FF, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xFD, mpu.p)
        # test NZ 10 => 00 when loading non-zero, positive
        mpu.p = 0xFD    # P.4 not physically implemented, do not set to 0
        mpu.sp[0] = 0x5555
        mpu.x[0] = 0x8000
        mon.do_goto('200')
        self.assertEqual(0x5555, mpu.x[0])
        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0x7D, mpu.p)

    # xai (isz dup)

    def test_word_exchange_a_and_ip(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}
        mpu.ip = 0x5555
        p = copy.copy(mpu.p)
        a = {0 : 0x5555, 1 : 0x4444, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x8888
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xBB    # ISZ
        mpu.memory[0x201] = 0x0B    # DUP A
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rti.s (osx rti)
    
    def test_return_from_interrupt_using_alternate_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        self.assertEqual(0x30, mpu.p)    # Interrupts Kernel Mode Only
        mpu.x = {0 : 0x1FC, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x40    # RTI
        mpu.memory[0x202] = 0xEA    # NOP
        mpu.memory[0x203] = 0x00

        mpu.memory[0x1FF] = 0x02    # PCH
        mpu.memory[0x1FE] = 0x01    # PCL
        mpu.memory[0x1FD] = 0xD3    # P

        p = 0xD3
        a = copy.copy(mpu.a)
        x = {0 : 0x1FF, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        
        mon.do_goto('200')
        
        self.assertEqual(0x203, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
        mpu.p = 0x30
        mpu.x = {0 : 0x1FD, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x100] = 0x02    # PCH
        mpu.memory[0x1FF] = 0x01    # PCL
        mpu.memory[0x1FE] = 0xDF    # P

        p = 0xDF
        x = {0 : 0x100, 1 : 0x4444, 2 : 0x2222}
        
        mon.do_goto('200')
        
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])

    # rts.s (osx rts)
    
    def test_return_from_subroutine_using_alternate_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x = {0 : 0x1FD, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x60    # RTS
        mpu.memory[0x202] = 0xEA    # NOP
        mpu.memory[0x203] = 0x00

        mpu.memory[0x1FF] = 0x02    # PCH
        mpu.memory[0x1FE] = 0x01    # PCL

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = {0 : 0x1FF, 1 : 0x4444, 2 : 0x2222}
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)
        
        mon.do_goto('200')
        
        self.assertEqual(0x203, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
        mpu.p = 0x10
        mpu.x = {0 : 0x2FE, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x300] = 0x02    # PCH
        mpu.memory[0x2FF] = 0x01    # PCL

        p = copy.copy(mpu.p)
        x = {0 : 0x300, 1 : 0x4444, 2 : 0x2222}
        
        mon.do_goto('200')
        
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(x[j], mpu.x[j])
    
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
        
    # ins (osx ins) [NZ]

    def test_increment_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.sp = {0 : 0x01FF, 1 : 0x017F}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x0180}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0xE8    # INX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.sp = {0 : 0x01FF, 1 : 0x01FF}
        p = psw | mpu.ZERO
        s = {0 : 0x01FF, 1 : 0x0100}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.p = 0x10    # Set User Mode
        
        mpu.sp = {0 : 0x01FF, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.ZERO
        s = {0 : 0x0100, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.sp = {0 : 0x017F, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.NEGATIVE
        s = {0 : 0x0180, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

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
        
    # tas (oax txs)
    
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
    
    # tsa (oax tsx)
    
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
    
    # des (osx dex) [NZ]

    def test_decrement_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.sp = {0 : 0x01FF, 1 : 0x0100}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x01FF}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0xCA    # DEX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.sp = {0 : 0x01FF, 1 : 0x0101}
        p = psw | mpu.ZERO
        s = {0 : 0x01FF, 1 : 0x0100}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.p = 0x10    # Set User Mode
        
        mpu.sp = {0 : 0x0101, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.ZERO
        s = {0 : 0x0100, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.sp = {0 : 0x0100, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.NEGATIVE
        s = {0 : 0x01FF, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

    # phi.s (osx phi)
    
    def test_push_word_ip_to_alternate_stack_S(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.sp = {0 : 0x01FF, 1 : 0x01FF}
        mpu.ip = 0xA55A

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x01FD}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x8B    # OSX
        mpu.memory[0x201] = 0x4B    # PHI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xA5, mpu.memory[0x1FF])
        self.assertEqual(0x5A, mpu.memory[0x1FE])
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # pli.s (osx pli)
    
    def test_pull_word_ip_from_alternate_stack_S(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.sp = {0 : 0x01FF, 1 : 0x01FD}
        mpu.ip = 0x0000
        mpu.memory[0x1FF] = 0xA5
        mpu.memory[0x1FE] = 0x5A

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x01FF}
        i = 0xA55A
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x8B    # 0SX
        mpu.memory[0x201] = 0x6B    # PLI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ent.s (osx ent)

    def test_Forth_VM_enter_using_alternate_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        codeFieldPtr = 0x202
        mpu.ip = codeFieldPtr       # Codefield Pointer
        mpu.x = {0 : 0x17F, 1 : 0x4444, 2 : 0x2222}

        mpu.memory[0x200] = 0x3B    # NXT - Primary Forth WORD Exit (pli nxt)
        mpu.memory[0x201] = 0x00
        # Forth WORD - Secondary Code Field
        mpu.memory[0x202] = 0x08    # Pointer to header #1
        mpu.memory[0x203] = 0x02
        mpu.memory[0x204] = 0x00    # Pointer to header #2
        mpu.memory[0x205] = 0x00    
        mpu.memory[0x206] = 0x00    # Pointer to header #3
        mpu.memory[0x207] = 0x00    
        # Forth WORD - Secondary
        mpu.memory[0x208] = 0x8B    # OSX
        mpu.memory[0x209] = 0x7B    # ENT
        mpu.memory[0x20A] = 0x0D    # Pointer to header #1
        mpu.memory[0x20B] = 0x02
        mpu.memory[0x20C] = 0x00    # Pointer to Header #2 (partial)
        # Forth WORD - Primitive
        mpu.memory[0x20D] = 0x80    # Branch $+2
        mpu.memory[0x20E] = 0x00
        mpu.memory[0x20F] = 0x00 

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x1FF, 1 : 0x1FD}
        i = 0x20C
        w = 0x20D

        mon.do_goto('200')
        
        self.assertEqual(0x20F, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
    
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
        
    # ins.w (osz inx) [NZ]

    def test_word_increment_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.sp = {0 : 0x01FF, 1 : 0x7FFF}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x8000}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0xE8    # INX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.sp = {0 : 0x01FF, 1 : 0xFFFF}
        p = psw | mpu.ZERO
        s = {0 : 0x01FF, 1 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.p = 0x10    # Set User Mode
        
        mpu.sp = {0 : 0xFFFF, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.ZERO
        s = {0 : 0x0000, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.sp = {0 : 0x7FFF, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.NEGATIVE
        s = {0 : 0x8000, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

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
        
    # tas.w (oax siz txs)
    
    def test_word_transfer_a_to_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xAB    # SIZ
        mpu.memory[0x202] = 0x9A    # TXS
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        # test transfer a to s in kernel mode: a[0] => sp[1]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x7FFF
        mon.do_goto('200')
        self.assertEqual(0x7FFF, mpu.sp[1])
        self.assertEqual(0x203, mpu.pc)
        # test transfer a to s in user mode: a[0] => sp[0]
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0x047F
        mon.do_goto('200')
        self.assertEqual(0x47F, mpu.sp[0])
        self.assertEqual(0x203, mpu.pc)
    
    # tsa.w (oax siz tsx)
    
    def test_word_transfer_s_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xAB    # SIZ
        mpu.memory[0x202] = 0xBA    # TXS
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x017F
        mpu.sp[1] = 0x01FF
        # test transfer s to a in kernel mode: sp[1] => a[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0x1FF, mpu.a[0])
        self.assertEqual(0x203, mpu.pc)
        # test transfer s to a in user mode: sp[0] => a
        mpu.p = 0x5D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0x17F, mpu.a[0])
        self.assertEqual(0x203, mpu.pc)
    
    # des.w (osz dex) [NZ]

    def test_word_decrement_s(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        psw = copy.copy(mpu.p)
        mpu.sp = {0 : 0x01FF, 1 : 0x0000}

        p = psw | mpu.NEGATIVE
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0xFFFF}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xCB    # OSZ
        mpu.memory[0x201] = 0xCA    # DEX
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)
        
        mpu.sp = {0 : 0x01FF, 1 : 0x0001}
        p = psw | mpu.ZERO
        s = {0 : 0x01FF, 1 : 0x0000}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.p = 0x10    # Set User Mode
        
        mpu.sp = {0 : 0x0001, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.ZERO
        s = {0 : 0x0000, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])

        mpu.sp = {0 : 0x0000, 1 : 0x01FF}
        p = (psw & ~mpu.MODE) | mpu.NEGATIVE
        s = {0 : 0xFFFF, 1 : 0x01FF}

        mon.do_goto('200')

        self.assertEqual(p, mpu.p)
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
    
    # tua.w (oax isz tsx)
    
    def test_word_transfer_u_to_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xBB    # ISZ
        mpu.memory[0x202] = 0xBA    # TSX
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x017F
        mpu.sp[1] = 0x01FD
        # test transfer u to a in kernel mode: sp[0] => a[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mon.do_goto('200')
        self.assertEqual(0x17F, mpu.a[0])
        self.assertEqual(0x203, mpu.pc)
    
    # tau.w (oax isz txs)
    
    def test_word_transfer_a_to_u(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xBB    # ISZ
        mpu.memory[0x202] = 0x9A    # TXS
        mpu.memory[0x203] = 0x00
        mpu.sp[0] = 0x0000
        mpu.sp[1] = 0x0000
        # test transfer a to u in kernel mode: a[0] => sp[0]
        mpu.p = 0x7D    # P.4 not physically implemented, do not set to 0
        mpu.a[0] = 0xEFFF
        mon.do_goto('200')
        self.assertEqual(0xEFFF, mpu.sp[0])
        self.assertEqual(0x203, mpu.pc)
      
    # tau (oax ind txs)
    
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

    # phw.s (ois phi)
    
    def test_push_word_wp_to_alternate_stack_S(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.sp = {0 : 0x01FF, 1 : 0x01FF}
        mpu.wp = 0xA55A

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x01FD}
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0xDB    # OIS
        mpu.memory[0x201] = 0x4B    # PHI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(0xA5, mpu.memory[0x1FF])
        self.assertEqual(0x5A, mpu.memory[0x1FE])
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # plw.s (ois pli)
    
    def test_pull_word_wp_from_alternate_stack_S(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.sp = {0 : 0x01FF, 1 : 0x01FD}
        mpu.wp = 0x0000
        mpu.memory[0x1FF] = 0xA5
        mpu.memory[0x1FE] = 0x5A

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = {0 : 0x01FF, 1 : 0x01FF}
        i = copy.copy(mpu.ip)
        w = 0xA55A

        mpu.memory[0x200] = 0xDB    # OIS
        mpu.memory[0x201] = 0x6B    # PLI
        mpu.memory[0x202] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x202, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # ient.s (ois ent)

    def test_Forth_VM_indirect_enter_using_alternate_stack(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.x[0] = 0x17D

        # ITC Forth Exit
        mpu.memory[0x200] = 0x6B    # PLI - Forth WORD Indirect Exit (ind inxt)
        # ITC Forth Next
        mpu.memory[0x201] = 0x9B    # IND
        mpu.memory[0x202] = 0x3B    # NXT
        # ITC Forth Enter
        mpu.memory[0x203] = 0xDB    # OIS - Forth WORD Indirect Enter (ois ent)
        mpu.memory[0x204] = 0x7B    # ENT
        # Forth WORD - Secondary Code Field
        mpu.memory[0x205] = 0x07    # Pointer to header #1
        mpu.memory[0x206] = 0x02
        # Forth WORD - Secondary
        mpu.memory[0x207] = 0x03    # header: IND (Secondary WORD)
        mpu.memory[0x208] = 0x02    # header: ENT (Secondary WORD)
        mpu.memory[0x209] = 0x0D    # Pointer to header #1
        mpu.memory[0x20A] = 0x02
        mpu.memory[0x20B] = 0x00    # Pointer to header #2 (not implemented)
        mpu.memory[0x20C] = 0x00
        # Forth WORD - Primitive
        mpu.memory[0x20D] = 0x0F    # header: pointer to code field
        mpu.memory[0x20E] = 0x02
        mpu.memory[0x20F] = 0x00 
        # Forth Return Stack
        mpu.memory[0x17D] = 0x00
        mpu.memory[0x17E] = 0x05    # header: pointer to code field
        mpu.memory[0x17F] = 0x02 
        # Forth Parameter Stack
        mpu.memory[0x1FD] = 0x00
        mpu.memory[0x1FE] = 0x00    # header: pointer to code field
        mpu.memory[0x1FF] = 0x00 

        p = copy.copy(mpu.p)
        a = copy.copy(mpu.a)
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = 0x20B; w = 0x20D
        x[0] = 0x17F; s[1] = 0x1FD

        mon.do_goto('200')
        
        self.assertEqual(0x07, mpu.memory[0x1FE])
        self.assertEqual(0x02, mpu.memory[0x1FF])
        self.assertEqual(0x20F, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

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
    
    # txy.w (oay siz txa)
    
    def test_word_transfer_x_to_y(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xFB    # OAY
        mpu.memory[0x201] = 0xAB    # SIZ
        mpu.memory[0x202] = 0x8A    # TXA
        mpu.memory[0x203] = 0x00
        mpu.x[0] = 0xFFFF
        mpu.y[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.y[0])
        self.assertEqual(0x203, mpu.pc)
    
    # tyx (oax tya)

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
    
    # tyx.w (oax siz tya)

    def test_word_transfer_y_to_x(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.memory[0x200] = 0xEB    # OAX
        mpu.memory[0x201] = 0xAB    # SIZ
        mpu.memory[0x202] = 0x98    # TYA
        mpu.memory[0x203] = 0x00
        mpu.y[0] = 0xFFFF
        mpu.x[0] = 0x0000
        mon.do_goto('200')
        self.assertEqual(0xFFFF, mpu.x[0])
        self.assertEqual(0x203, mpu.pc)
    
    # dup a

    def test_duplicate_TOS_register_stack_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}

        p = copy.copy(mpu.p)
        a = {0 : 0x8888, 1 : 0x8888, 2 : 0x4444}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x0B    # DUP A
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # swp a

    def test_swap_TOS_and_NOS_register_stack_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}

        p = copy.copy(mpu.p)
        a = {0 : 0x4444, 1 : 0x8888, 2 : 0x2222}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x1B    # SWP A
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # rot a

    def test_rotate_register_stack_a(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.a = {0 : 0x8888, 1 : 0x4444, 2 : 0x2222}

        p = copy.copy(mpu.p)
        a = {0 : 0x4444, 1 : 0x2222, 2 : 0x8888}
        x = copy.copy(mpu.x)
        y = copy.copy(mpu.y)
        s = copy.copy(mpu.sp)
        i = copy.copy(mpu.ip)
        w = copy.copy(mpu.wp)

        mpu.memory[0x200] = 0x2B    # ROT A
        mpu.memory[0x201] = 0x00

        mon.do_goto('200')

        self.assertEqual(0x201, mpu.pc)
        self.assertEqual(p, mpu.p)
        for j in range(3):
            self.assertEqual(a[j], mpu.a[j])
            self.assertEqual(x[j], mpu.x[j])
            self.assertEqual(y[j], mpu.y[j])
        for j in range(2):
            self.assertEqual(s[j], mpu.sp[j])
        self.assertEqual(i, mpu.ip)
        self.assertEqual(w, mpu.wp)

    # inu (osx ind ins) [NZ]
    # inu.w (ois inx) [NZ]
    # deu (osx ind dex) [NZ]
    # deu.w (ois dex) [NZ]

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
