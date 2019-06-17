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
        
    # ro_zp (flags: {osx, ind, siz} = {0, 0, 0})
    
    def test_ro_zp_byte(self):
        def op(val):
            self.rtnVal = val

        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = False;
        
        mpu.pc = 0x200
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x55

        data = mpu.byteMask & mpu.memory[zp]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {0, 0, 1})
    
    def test_ro_zp_word(self):
        def op(val):
            self.rtnVal = val

        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = True;
        
        # zero page word access w/o wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0xAA
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x55
        
        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[mpu.byteMask & (zp + 1)]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # zero page word access w/ wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x33
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x66

        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[mpu.byteMask & (zp + 1)]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {0, 1, 0})
    
    def test_ro_zp_indirect_byte(self):
        def op(val):
            self.rtnVal = val

        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = False;
        
        # zero page indirect byte access w/o wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.pc + 1] = 0x55
        mpu.memory[zp] = 0x01
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02

        data = mpu.byteMask & mpu.memory[mpu.pc + 1]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect byte access w/ wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.pc + 1] = 0x55
        mpu.memory[zp] = 0x01
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02

        data = mpu.byteMask & mpu.memory[mpu.pc + 1]
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
                
    # ro_zp (flags: {osx, ind, siz} = {0, 1, 1})
    
    def test_ro_zp_indirect_word(self):
        def op(val):
            self.rtnVal = val

        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = True;
        
        # zero page indirect word access w/o wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.pc + 1] = 0xAA
        mpu.memory[mpu.pc + 2] = 0x55
        mpu.memory[zp] = 0x01
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02

        tmp1 = mpu.byteMask & mpu.memory[mpu.pc + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.pc + 2]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(data, 0x55AA)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect word access w/ wrap-around at page boundary
        
        mpu.pc = 0x200
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.pc + 1] = 0x33
        mpu.memory[mpu.pc + 2] = 0x66
        mpu.memory[zp] = 0x01
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02

        tmp1 = mpu.byteMask & mpu.memory[mpu.pc + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.pc + 2]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zp(op)
                
        self.assertEqual(data, 0x6633)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {1, 0, 0})
    
    def test_ro_zp_stk_relative_byte(self):
        def op(val):
            self.rtnVal = val

        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = False;
        
        # stack relative byte read using page 1 kernel stack w/o wrap-around
        
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FE
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0x55

        data = mpu.byteMask & mpu.memory[mpu.sp[1] + sp]
        pc = mpu.pc + 1
        sk = mpu.sp[1]
        
        mpu.ro_zp(op)
                
        self.assertEqual(data, 0x55)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # stack relative byte read using page 1 user stack w/o wrap-around
        
        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17E
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0xAA

        data = mpu.byteMask & mpu.memory[mpu.sp[0] + sp]
        pc = mpu.pc + 1
        su = mpu.sp[0]
        
        mpu.ro_zp(op)
                
        self.assertEqual(data, 0xAA)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # ro_zp (flags: {osx, ind, siz} = {1, 0, 1})
    
    def test_ro_zp_stk_relative_word(self):
        def op(val):
            self.rtnVal = val
        pass
        
    # ro_zp (flags: {osx, ind, siz} = {1, 1, 0})
    
    def test_ro_zp_stk_relative_indirect_byte(self):
        def op(val):
            self.rtnVal = val
        pass
        
    # ro_zp (flags: {osx, ind, siz} = {1, 1, 1})
    
    def test_ro_zp_stk_relative_indirect_word(self):
        def op(val):
            self.rtnVal = val
        pass
        
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
