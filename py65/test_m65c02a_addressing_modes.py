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


class M65C02A_Addressing_Mode_Tests(unittest.TestCase):
    
    rtnVal = 0
    
    # imm (flags: siz)
    
    def test_imm(self):
        def op(val):
            self.rtnVal = val
        
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.pc = 0x200
        
        mpu.memory[0x200] = 0xAA
        mpu.memory[0x201] = 0x55
        mpu.memory[0x202] = 0xC3
        
        mpu.imm(op)
                
        self.assertEqual(self.rtnVal, mpu.memory[0x200])
        self.assertEqual(0x201, mpu.pc)
        
        mpu.imm(op)
        
        self.assertEqual(self.rtnVal, mpu.memory[0x201])
        self.assertEqual(0x202, mpu.pc)

        mpu.siz = True; mpu.pc = 0x201
        
        mpu.imm(op)
        wrdData = mpu.wordMask & ( (mpu.memory[0x202] << 8) \
                                  + mpu.memory[0x201]      )
        self.assertEqual(self.rtnVal, wrdData)
        self.assertEqual(0x203, mpu.pc)
        

    # ro_zp (flags: {osx, ind, siz})
    
    def test_ro_zp(self):
        def op(val):
            self.rtnVal = val
        
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.pc = 0x200

        # zp pointers
        mpu.memory[0x200] = 0xAA    # test 0
        mpu.memory[0x201] = 0x55    # test 1 (w/o wrap around)
        mpu.memory[0x202] = 0xFF    # test 1 (w/  wrap around)
        mpu.memory[0x203] = 0x80    # test 2 (w/o wrap around)
        mpu.memory[0x204] = 0xFF    # test 2 (w/  wrap around)
        mpu.memory[0x205] = 0x82    # test 3 (w/o wrap around)
        # zero page 
        mpu.memory[0x0AA] = 0x96    # test 0
        mpu.memory[0x055] = 0xC3    # test 1 (w/o wrap around)
        mpu.memory[0x056] = 0x3C    
        mpu.memory[0x0FF] = 0x7F    # test 1, 2 (w/  wrap around)
        mpu.memory[0x000] = 0x01
        mpu.memory[0x080] = 0x80    # test 1, 2 (w/o wrap around)
        mpu.memory[0x081] = 0x01    
        mpu.memory[0x080] = 0x82    # test 3 (w/o wrap around)
        mpu.memory[0x081] = 0x01    
        # indirect memory
        mpu.memory[0x17F] = 0x33
        mpu.memory[0x180] = 0x66
        mpu.memory[0x181] = 0x99
        mpu.memory[0x182] = 0x55
        mpu.memory[0x183] = 0xAA
        mpu.memory[0x1FF] = 0xAA
        mpu.memory[0x100] = 0x55
        

        # test 0: {siz, ind, osx} = (0, 0, 0) -- read byte from page 0

        mpu.siz = False; mpu.ind = False; mpu.osx = False
        zp = mpu.memory[mpu.pc]
        data = mpu.byteMask & mpu.memory[zp]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # test 1: {siz, ind, osx} = (1, 0, 0) -- read word from page 0

        mpu.siz = True; mpu.ind = False; mpu.osx = False
        zp = mpu.memory[mpu.pc]
        data = mpu.wordMask & ( (mpu.memory[mpu.byteMask & (zp + 1)] << 8) \
                               + mpu.memory[zp]                           )
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
        
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # wrap word read around page boundary
        
        zp = mpu.memory[mpu.pc]
        data = mpu.wordMask & ( (mpu.memory[mpu.byteMask & (zp + 1)] << 8) \
                               + mpu.memory[zp]                           )
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
        
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # test 2: {siz, ind, osx} = (0, 1, 0) -- read byte indirect from page 0

        mpu.siz = False; mpu.ind = True; mpu.osx = False
        zp = mpu.memory[mpu.pc]
        addr = mpu.wordMask & ( (mpu.memory[mpu.byteMask & (zp + 1)] << 8) \
                               + mpu.memory[zp]                           )
        data = mpu.byteMask & mpu.memory[addr]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
        
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # wrap pointer read around page boundary
        
        zp = mpu.memory[mpu.pc]
        addr = mpu.wordMask & ( (mpu.memory[mpu.byteMask & (zp + 1)] << 8) \
                               + mpu.memory[zp]                           )
        data = mpu.byteMask & mpu.memory[addr]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
        
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # test 3: {siz, ind, osx} = (1, 1, 0) -- read word indirect from page 0

        # wrap pointer read around page boundary
        
        mpu.siz = False; mpu.ind = True; mpu.osx = False
        zp = mpu.memory[mpu.pc]
        addr = mpu.wordMask & ( (mpu.memory[mpu.byteMask & (zp + 1)] << 8) \
                               + mpu.memory[zp]                           )
        data = mpu.byteMask & mpu.memory[addr]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
        
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
                
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
