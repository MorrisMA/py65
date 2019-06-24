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
    outVal = 0
    rmwVal = 0
    
    mask = 0
    
    def op(self, val):
        self.rtnVal = val

    def reg(self):
        return self.outVal

    def rmw(self, data):
        tmp = -data             # negate operand; not available 6502/65C02 ISA
        return self.mask & tmp

    # imm (flags: siz)
    
    def test_imm(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu
        mpu.pc = 0x200
        
        mpu.memory[0x200] = 0xAA
        mpu.memory[0x201] = 0x55
        mpu.memory[0x202] = 0xC3
        
        mpu.imm(self.op)
                
        self.assertEqual(self.rtnVal, mpu.memory[0x200])
        self.assertEqual(0x201, mpu.pc)
        
        mpu.imm(self.op)
        
        self.assertEqual(self.rtnVal, mpu.memory[0x201])
        self.assertEqual(0x202, mpu.pc)

        mpu.siz = True;
        mpu.pc = 0x201
        
        mpu.imm(self.op)

        wrdData = mpu.wordMask & ( (mpu.memory[0x202] << 8) \
                                  + mpu.memory[0x201]      )
        self.assertEqual(self.rtnVal, wrdData)
        self.assertEqual(0x203, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {0, 0, 0})
    
    def test_ro_zp_byte(self):
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
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {0, 0, 1})
    
    def test_ro_zp_word(self):
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
        
        mpu.ro_zp(self.op)
                
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
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {0, 1, 0})
    
    def test_ro_zp_indirect_byte(self):
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
        
        mpu.ro_zp(self.op)
                
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
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
                
    # ro_zp (flags: {osx, ind, siz} = {0, 1, 1})
    
    def test_ro_zp_indirect_word(self):
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
        
        mpu.ro_zp(self.op)
                
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
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(data, 0x6633)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zp (flags: {osx, ind, siz} = {1, 0, 0})
    
    def test_ro_zp_stk_relative_byte(self):
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
        
        mpu.ro_zp(self.op)
                
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
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(data, 0xAA)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # ro_zp (flags: {osx, ind, siz} = {1, 0, 1})
    
    def test_ro_zp_stk_relative_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = True;
        
        # stack relative byte read using page 1 kernel stack w/o wrap-around
        
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0xAA
        mpu.memory[mpu.sp[1] + 2] = 0x55

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[1] + 2]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        sk = mpu.sp[1]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(data, 0x55AA)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        self.assertEqual(self.rtnVal, data)
        
        # stack relative byte read using page 1 user stack w/o wrap-around
        
        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0x33
        mpu.memory[mpu.sp[0] + 2] = 0x66

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[0] + 2]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        su = mpu.sp[0]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(data, 0x6633)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        self.assertEqual(self.rtnVal, data)
                
    # ro_zp (flags: {osx, ind, siz} = {1, 1, 0})
    
    def test_ro_zp_stk_relative_indirect_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = False;

        # stack relative indirect byte read using page 1 kernel stack w/o wrap
        
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0x02
        mpu.memory[mpu.sp[1] + 2] = 0x02
        mpu.memory[0x202] = 0x55

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[1] + 2]
        ptr = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        data = mpu.byteMask & mpu.memory[ptr]
        pc = mpu.pc + 1
        sk = mpu.sp[1]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(ptr, 0x0202)
        self.assertEqual(data, 0x55)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # stack relative indirect byte read using page 1 user stack w/o wrap
        
        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0x04
        mpu.memory[mpu.sp[0] + 2] = 0x02
        mpu.memory[0x204] = 0x66

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[0] + 2]
        ptr  = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        data = mpu.byteMask & mpu.memory[ptr]
        pc = mpu.pc + 1
        su = mpu.sp[0]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(ptr, 0x0204)
        self.assertEqual(data, 0x66)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # ro_zp (flags: {osx, ind, siz} = {1, 1, 1})
    
    def test_ro_zp_stk_relative_indirect_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = True;
        
        # stack relative indirect word read using page 1 kernel stack w/o wrap
        
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0x01
        mpu.memory[mpu.sp[1] + 2] = 0x02
        mpu.memory[0x201] = 0xAA
        mpu.memory[0x202] = 0x55

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[1] + 2]
        ptr = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        tmp1 = mpu.byteMask & mpu.memory[ptr]
        tmp2 = mpu.byteMask & mpu.memory[ptr + 1]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        sk = mpu.sp[1]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(ptr, 0x0201)
        self.assertEqual(data, 0x55AA)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # stack relative indirect word read using page 1 user stack w/o wrap
        
        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0x03
        mpu.memory[mpu.sp[0] + 2] = 0x02
        mpu.memory[0x203] = 0x33
        mpu.memory[0x204] = 0x66

        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[0] + 2]
        ptr = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        tmp1 = mpu.byteMask & mpu.memory[ptr]
        tmp2 = mpu.byteMask & mpu.memory[ptr + 1]
        data = mpu.wordMask & ( (tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        su = mpu.sp[0]
        
        mpu.ro_zp(self.op)
                
        self.assertEqual(ptr, 0x0203)
        self.assertEqual(data, 0x6633)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # wo_zp (flags: {osx, ind, siz} = {0, 0, 0})
    
    def test_wo_zp_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = False;
        
        mpu.pc = 0x200
        self.outVal = 0x55
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[zp]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        
    # wo_zp (flags: {osx, ind, siz} = {0, 0, 1})
    
    def test_wo_zp_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = True;
        
        # zero page word write w/o wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x55AA
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[zp + 1]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        
        # zero page word write w/ wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x6633
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[mpu.byteMask & (zp + 1)]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        
    # wo_zp (flags: {osx, ind, siz} = {0, 1, 0})
    
    def test_wo_zp_indirect_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = False;
        
        # zero page indirect byte write w/o wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x55
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x01
        mpu.memory[zp + 1] = 0x02
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[0x201]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect byte write w/ wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x66
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x03
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[0x203]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)

    # wo_zp (flags: {osx, ind, siz} = {0, 1, 1})
    
    def test_wo_zp_indirect_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = True;
        
        # zero page indirect word write w/o wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x55AA
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x01
        mpu.memory[zp + 1] = 0x02
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[0x201]
        tmp2 = mpu.byteMask & mpu.memory[0x202]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect word write w/ wrap-around
        
        mpu.pc = 0x200
        self.outVal = 0x6633
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x03
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02
        pc = mpu.pc + 1

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[0x203]
        tmp2 = mpu.byteMask & mpu.memory[0x204]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)

    # wo_zp (flags: {osx, ind, siz} = {1, 0, 0})
    
    def test_wo_zp_stk_relative_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = False;
        
        # write kernel stack relative byte 

        mpu.p = mpu.p | 0x20    # set Mode bit
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FE
        self.outVal = 0x55
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        pc = mpu.pc + 1
        sk = mpu.sp[1]

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # write user stack relative byte 

        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17E
        self.outVal = 0x66
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        pc = mpu.pc + 1
        su = mpu.sp[0]

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # wo_zp (flags: {osx, ind, siz} = {1, 0, 1})
    
    def test_wo_zp_stk_relative_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = True;
        
        # write kernel stack relative word

        mpu.p = mpu.p | 0x20    # set Mode bit
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.outVal = 0x55AA
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        pc = mpu.pc + 1
        sk = mpu.sp[1]

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[1] + 2]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # write user stack relative word 

        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.outVal = 0x6633
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        pc = mpu.pc + 1
        su = mpu.sp[0]

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[0] + 2]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # wo_zp (flags: {osx, ind, siz} = {1, 1, 0})
    
    def test_wo_zp_stk_relative_indirect_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = False;
        
        # write kernel stack relative indirect byte 

        mpu.p = mpu.p | 0x20    # set Mode bit
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.outVal = 0x55
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0x01
        mpu.memory[mpu.sp[1] + 2] = 0x02
        pc = mpu.pc + 1
        sk = mpu.sp[1]

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[0x201]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # write user stack relative indirect byte 

        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.outVal = 0x66
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0x03
        mpu.memory[mpu.sp[0] + 2] = 0x02
        pc = mpu.pc + 1
        su = mpu.sp[0]

        mpu.wo_zp(self.reg)
                
        data = mpu.byteMask & mpu.memory[0x203]

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # wo_zp (flags: {osx, ind, siz} = {1, 1, 1})
    
    def test_wo_zp_stk_relative_indirect_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = True;
        
        # write kernel stack relative indirect byte 

        mpu.p = mpu.p | 0x20    # set Mode bit
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.outVal = 0x55AA
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[1] + 1] = 0x01
        mpu.memory[mpu.sp[1] + 2] = 0x02
        pc = mpu.pc + 1
        sk = mpu.sp[1]

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[0x201]
        tmp2 = mpu.byteMask & mpu.memory[0x202]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(sk, mpu.sp[1])
        
        # write user stack relative indirect byte 

        mpu.p = mpu.p & 0xDF    # clr Mode bit
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.outVal = 0x66
        sp = 0x01
        mpu.memory[mpu.pc] = sp
        mpu.memory[mpu.sp[0] + 1] = 0x03
        mpu.memory[mpu.sp[0] + 2] = 0x02
        pc = mpu.pc + 1
        su = mpu.sp[0]

        mpu.wo_zp(self.reg)
                
        tmp1 = mpu.byteMask & mpu.memory[0x203]
        tmp2 = mpu.byteMask & mpu.memory[0x204]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.outVal)
        self.assertEqual(pc, mpu.pc)
        self.assertEqual(su, mpu.sp[0])
        
    # rmw_zp (flags: {osx, ind, siz} = {0, 0, 0})
    
    def test_rmw_zp_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = False;
        
        mpu.pc = 0x200
        self.rmwVal = 0x55
        self.rtnVal = 0xAB
        self.mask = mpu.byteMask
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = self.rmwVal

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[zp]

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # rmw_zp (flags: {osx, ind, siz} = {0, 0, 1})
    
    def test_rmw_zp_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = True;

        # rmw zero page word w/o wrap-around

        mpu.pc = 0x200
        self.rmwVal = 0x55AA
        self.rtnVal = 0xAA56
        self.mask = mpu.wordMask
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0xAA
        mpu.memory[zp + 1] = 0x55

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[zp + 1]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # rmw zero page word w/ wrap-around

        mpu.pc = 0x200
        self.rmwVal = 0x6633
        self.rtnVal = 0x99CD
        self.mask = mpu.wordMask
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[zp] = 0x33
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x66

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[zp]
        tmp2 = mpu.byteMask & mpu.memory[mpu.byteMask & (zp + 1)]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {0, 1, 0})
    
    def test_rmw_zp_indirect_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = False;
        
        # zero page indirect rmw byte w/o wrap-around
        
        mpu.pc = 0x200
        self.rmwVal = 0x55
        self.rtnVal = 0xAB
        self.mask = mpu.byteMask
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x201] = self.rmwVal
        mpu.memory[zp] = 0x01
        mpu.memory[zp + 1] = 0x02
        
        pc = mpu.pc + 1

        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[0x201]

        self.assertEqual(data, self.rtnVal)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect rmw byte w/ wrap-around
        
        mpu.pc = 0x200
        self.rmwVal = 0x66
        self.rtnVal = 0x9A
        self.mask = mpu.byteMask
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x203] = self.rmwVal
        mpu.memory[zp] = 0x03
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02
        pc = mpu.pc + 1

        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[0x203]

        self.assertEqual(data, self.rtnVal)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {0, 1, 1})
    
    def test_rmw_zp_indirect_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = True; mpu.siz = True;
        
        # zero page indirect rmw byte w/o wrap-around
        
        mpu.pc = 0x200
        self.rmwVal = 0x55AA
        self.rtnVal = 0xAA56
        self.mask = mpu.wordMask
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x201] = 0xAA
        mpu.memory[0x202] = 0x55
        mpu.memory[zp] = 0x01
        mpu.memory[zp + 1] = 0x02
        
        pc = mpu.pc + 1

        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[0x201]
        tmp2 = mpu.byteMask & mpu.memory[0x202]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.rtnVal)
        self.assertEqual(pc, mpu.pc)
        
        # zero page indirect rmw byte w/ wrap-around
        
        mpu.pc = 0x200
        self.rmwVal = 0x6633
        self.rtnVal = 0x99CD
        self.mask = mpu.wordMask
        zp = 0xFF
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x203] = 0x33
        mpu.memory[0x204] = 0x66
        mpu.memory[zp] = 0x03
        mpu.memory[mpu.byteMask & (zp + 1)] = 0x02
        pc = mpu.pc + 1

        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[0x203]
        tmp2 = mpu.byteMask & mpu.memory[0x204]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(data, self.rtnVal)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {1, 0, 0})
    
    def test_rmw_zp_stk_relative_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = False;
        
        # kernel stk relative rmw byte

        mpu.p = mpu.p | 0x20        # set M flag
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FE
        self.rmwVal = 0x55
        self.rtnVal = 0xAB
        self.mask = mpu.byteMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[1] + 1] = self.rmwVal

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # user stk relative rmw byte

        mpu.p = mpu.p & 0xDF        # clr M flag
        mpu.pc = 0x200
        mpu.sp[0] = 0x17E
        self.rmwVal = 0x33
        self.rtnVal = 0xCD
        self.mask = mpu.byteMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[0] + 1] = self.rmwVal

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {1, 0, 1})
    
    def test_rmw_zp_stk_relative_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = False; mpu.siz = True;
        
        # kernel stk relative rmw word

        mpu.p = mpu.p | 0x20        # set M flag
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.rmwVal = 0x55AA
        self.rtnVal = 0xAA56
        self.mask = mpu.wordMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[1] + 1] = 0xAA
        mpu.memory[mpu.sp[1] + 2] = 0x55

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[1] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[1] + 2]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # user stk relative rmw byte

        mpu.p = mpu.p & 0xDF        # clr M flag
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.rmwVal = 0x6633
        self.rtnVal = 0x99CD
        self.mask = mpu.wordMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[0] + 1] = 0x33
        mpu.memory[mpu.sp[0] + 2] = 0x66

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[mpu.sp[0] + 1]
        tmp2 = mpu.byteMask & mpu.memory[mpu.sp[0] + 2]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {1, 1, 0})
    
    def test_rmw_zp_stk_relative_indirect_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = False;
        
        # kernel stk relative indirect rmw word

        mpu.p = mpu.p | 0x20        # set M flag
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.rmwVal = 0x55
        self.rtnVal = 0xAB
        self.mask = mpu.byteMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[1] + 1] = 0x01
        mpu.memory[mpu.sp[1] + 2] = 0x02
        mpu.memory[0x201] = 0x55

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[0x201]

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # user stk relative rmw byte

        mpu.p = mpu.p & 0xDF        # clr M flag
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.rmwVal = 0x33
        self.rtnVal = 0xCD
        self.mask = mpu.byteMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[0] + 1] = 0x03
        mpu.memory[mpu.sp[0] + 2] = 0x02
        mpu.memory[0x203] = 0x33

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        data = mpu.byteMask & mpu.memory[0x203]

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)

    # rmw_zp (flags: {osx, ind, siz} = {1, 1, 1})
    
    def test_rmw_zp_stk_relative_indirect_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = True; mpu.ind = True; mpu.siz = True;
        
        # kernel stk relative rmw word

        mpu.p = mpu.p | 0x20        # set M flag
        mpu.pc = 0x200
        mpu.sp[1] = 0x1FD
        self.rmwVal = 0x55AA
        self.rtnVal = 0xAA56
        self.mask = mpu.wordMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[1] + 1] = 0x01
        mpu.memory[mpu.sp[1] + 2] = 0x02
        mpu.memory[0x201] = 0xAA
        mpu.memory[0x202] = 0x55

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[0x201]
        tmp2 = mpu.byteMask & mpu.memory[0x202]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # user stk relative rmw byte

        mpu.p = mpu.p & 0xDF        # clr M flag
        mpu.pc = 0x200
        mpu.sp[0] = 0x17D
        self.rmwVal = 0x6633
        self.rtnVal = 0x99CD
        self.mask = mpu.wordMask
        zp = 0x01
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.sp[0] + 1] = 0x03
        mpu.memory[mpu.sp[0] + 2] = 0x02
        mpu.memory[0x203] = 0x33
        mpu.memory[0x204] = 0x66

        pc = mpu.pc + 1
        
        mpu.rmw_zp(self.rmw)
                
        tmp1 = mpu.byteMask & mpu.memory[0x203]
        tmp2 = mpu.byteMask & mpu.memory[0x204]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)

        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)

    # ro_zpX (flags: {osx, ind, siz} = {0, 0, 0})
    
    def test_ro_zpX_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = False;
        
        # index < 512, index + unsigned offset read byte w/o wrap-around
        
        mpu.pc = 0x200
        mpu.x[0] = 0x80
        zp = 0x7F
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.byteMask & (mpu.x[0] + zp)] = 0x55

        data = mpu.byteMask & mpu.memory[0xFF]
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0x55, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # index < 512, index + unsigned offset read byte w/ wrap-around
        
        mpu.pc = 0x200
        mpu.x[0] = 0x80
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[mpu.byteMask & (mpu.x[0] + zp)] = 0xAA

        data = mpu.byteMask & mpu.memory[0x00]
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0xAA, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # index > 511, index + signed offset read byte, no wrap-around

        mpu.pc = 0x200
        mpu.x[0] = 0x281
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x201] = 0x66

        data = mpu.wordMask & mpu.memory[0x201]
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0x66, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
    # ro_zpX (flags: {osx, ind, siz} = {0, 0, 1})
    
    def test_ro_zpX_word(self):
        stdout = StringIO()
        mon = Monitor(stdout = stdout)
        mpu = mon._mpu

        mpu.osx = False; mpu.ind = False; mpu.siz = True;
        mpu.oax = True
        
        # index < 512, index + unsigned offset read byte w/o wrap-around
        
        mpu.pc = 0x200
        mpu.a[0] = 0x7F
        zp = 0x7F
        mpu.memory[mpu.pc] = zp
        mpu.memory[0xFE] = 0xAA
        mpu.memory[0xFF] = 0x55

        tmp1 = mpu.byteMask & mpu.memory[0xFE]
        tmp2 = mpu.byteMask & mpu.memory[0xFF]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0x55AA, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # index < 512, index + unsigned offset read byte w/ wrap-around
        
        mpu.pc = 0x200
        mpu.a[0] = 0x80
        zp = 0x7F
        mpu.memory[mpu.pc] = zp
        mpu.memory[0xFF] = 0x33
        mpu.memory[0x00] = 0x66

        tmp1 = mpu.byteMask & mpu.memory[0xFF]
        tmp2 = mpu.byteMask & mpu.memory[0x00]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0x6633, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
        # index > 511, index + signed offset read byte, no wrap-around

        mpu.pc = 0x200
        mpu.a[0] = 0x281
        zp = 0x80
        mpu.memory[mpu.pc] = zp
        mpu.memory[0x201] = 0x56
        mpu.memory[0x202] = 0xAA

        tmp1 = mpu.byteMask & mpu.memory[0x201]
        tmp2 = mpu.byteMask & mpu.memory[0x202]
        data = mpu.wordMask & ((tmp2 << 8) + tmp1)
        pc = mpu.pc + 1
        
        mpu.ro_zpX(self.op)
                
        self.assertEqual(0xAA56, data)
        self.assertEqual(self.rtnVal, data)
        self.assertEqual(pc, mpu.pc)
        
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
