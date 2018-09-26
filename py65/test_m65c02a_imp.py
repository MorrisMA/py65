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


class M65C02A_Implicit_AddressingMode_Tests(unittest.TestCase):

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
        mon.memory[0x200] = 0x8B    # OSX
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

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
