from utils.conversions import itoa
from utils.devices import make_instruction_decorator

class MPU():
    # vectors

    IRQ   = 0xFFFE
    RESET = 0xFFFC
    NMI   = 0xFFFA

    # processor flags

    NEGATIVE  = 128
    OVERFLOW  = 64
    MODE      = 32
    BREAK     = 16
    DECIMAL   = 8
    INTERRUPT = 4
    ZERO      = 2
    CARRY     = 1

    BYTE_WIDTH  = 8
    BYTE_FORMAT = "%02X"
    WORD_WIDTH  = 16
    WORD_FORMAT = "%04X"
    ADDR_WIDTH  = 16
    ADDR_FORMAT = "%04X"

    # declare registers

    a  = dict()
    b  = dict()
    c  = dict()
    sp = dict()
    ip = int()
    wp = int()
    pc = int()
    p  = int()

    # declare Prefix Byte Boolean Flags Registers

    osx  = False
    oax  = False
    oay  = False
    ind  = False
    siz  = False
    
    lscx = False  # override osx for the LDX/STX/CPX zp/abs instructions

    dbg  = False

    def __init__(self, memory=None, pc=0x0200):
        # config
        self.name = 'M65C02A'
        self.byteMask = ((1 << self.BYTE_WIDTH) - 1)
        self.wordMask = ((1 << self.WORD_WIDTH) - 1)
        self.addrMask = ((1 << self.ADDR_WIDTH) - 1)
        self.hiByteMask   = (self.byteMask << self.BYTE_WIDTH)
        self.addrHighMask = self.hiByteMask
        self.spBase = 1 << self.BYTE_WIDTH

        # vm status
        self.excycles = 0
        self.addcycles = False
        self.processorCycles = 0
        self.numInstructions = 0
        self.pgmMemRdCycles  = 0
        self.datMemRdCycles  = 0
        self.datMemWrCycles  = 0
        self.dummyCycles     = 0

        self.start_pc = pc

        # Initialize Memory
        #   Set RESET Vector

        if memory is None:
            memory = 0x10000 * [0x00]

        self.memory = memory
        self.memory[self.RESET    ] = self.byteMask & self.start_pc
        self.memory[self.RESET + 1] = self.byteMask & \
                                      (self.start_pc >> self.BYTE_WIDTH)

        # Reset Processor State

        self.reset()

    def reprformat(self):
        return ("%s PC   AC   XR   YR   SP   VM  NVMBDIZC\n"
                "%s: %04X %04X %04X %04X %04X %04X %s\n"
                "%s  %04X %04X %04X %04X %04X\n"
                "%s  %04X %04X %04X")

    def __repr__(self):
        flags = itoa(self.p, 2).rjust(self.BYTE_WIDTH, '0')
        indent = [' ' * (len(self.name) + 2),
                  ' ' * (len(self.name) + 5),
                  ' ' * (len(self.name) + 5)]

        return self.reprformat() % (indent[0],
                                    self.name,
                                    self.pc,    # Program Counter
                                    self.a[0],  # ATOS
                                    self.x[0],  # XTOS - Aux Stk Ptr, Base Ptr
                                    self.y[0],  # YTOS
                                    self.sp[1], # System Stk Ptr
                                    self.ip,    # FORTH VM Interpretive Pointer
                                    flags,      # Processor Status Word
                                    indent[1],
                                    self.a[1],  # ANOS
                                    self.x[1],  # XNOS
                                    self.y[1],  # YNOS
                                    self.sp[0], # User Stk Ptr
                                    self.wp,    # FORTH VM Workspace Pointer
                                    indent[2],
                                    self.a[2],  # ABOS
                                    self.x[2],  # XBOS
                                    self.y[2] ) # YBOS

    # Fetch and Execute instruction

    def step(self):
        def getInstruction(self):
            instructCode = self.byteMask & self.memory[self.addrMask & self.pc]
            print('   IR:', '%02X <= mem[%04X]' % (instructCode, self.pc))
            pc = self.addrMask & (self.pc + 1)
#            if instructCode in (139, 155, 171, 187, 203, 219, 235, 251):
            if instructCode in (0x8B, 0x9B, 0xAB, 0xBB, 0xCB, 0xDB, 0xEB, 0xFB):
                pass 
            else: self.numInstructions += 1
            self.processorCycles += 1
            self.pgmMemRdCycles += 1
            return pc, instructCode

        self.pc, instructCode = getInstruction(self)
        self.excycles = 0
        self.addcycles = self.extracycles[instructCode]
        self.instruct[instructCode](self)               # execute instruction
        return self

    # Function to clear the Prefix Instruction Flags
    # - used after all non-prefix instructions

    def clrPrefixFlags(self):
        self.osx = self.oax = self.oay = self.ind = self.siz = self.lscx = False

    def reset(self):
        def psh(self, z):
            self.memory[self.sp[self.sel]] = self.byteMask & z 
            tmp = self.sp[self.sel] - 1
            if self.sp[self.sel] < 512:
              tmp &= self.byteMask
              self.sp[self.sel] = (self.hiByteMask & self.sp[self.sel]) | tmp

        def pshW(self, z):
            psh(self, self.byteMask & (z >> 8))
            psh(self, self.byteMask & z)

        self.sp[1] = (self.addrHighMask & self.spBase) + 0x02
        self.sp[0] = (self.addrHighMask & self.spBase) + self.byteMask
        
        self.sel = 1
        
        self.a  = {0: 0, 1: 0, 2: 0}
        self.x  = {0: 0, 1: 0, 2: 0}
        self.y  = {0: 0, 1: 0, 2: 0}
        self.ip = 0
        self.wp = 0

        self.clrPrefixFlags()

        # Initialize Memory
        #   Set RESET Vector

        self.memory[self.RESET    ] = self.byteMask & self.start_pc
        self.memory[self.RESET + 1] = self.byteMask & \
                                      (self.start_pc >> self.BYTE_WIDTH)

        psh(self, self.p)
        pshW(self, self.pc)

        self.pc = self.start_pc
        self.p  = self.BREAK | self.MODE

        self.processorCycles = 0
        self.pgmMemRdCycles  = 0
        self.datMemRdCycles  = 0
        self.datMemWrCycles  = 0
        self.dummyCycles     = 0

    # Helpers for accessing memory

    def rdPM(self):
        tmp = self.byteMask & self.memory[self.addrMask & self.pc]
        if self.dbg:
            print(' rdPM:', '%02X <= mem[%04X]' % (tmp, self.pc))
        self.pc = self.addrMask & (self.pc + 1)
        self.processorCycles += 1; self.pgmMemRdCycles += 1
        return tmp

    def rdDM(self, addr):
        tmp = self.byteMask & self.memory[addr]
        if self.dbg:
            print(' rdDM:', '%02X <= mem[%04X]' % (tmp, addr))
        self.processorCycles += 1; self.datMemRdCycles += 1
        return tmp

    def wrDM(self, addr, data):
        if self.dbg:
            print(' wrDM:', '%02X => mem[%04X]' % (self.byteMask & data, addr))
        self.memory[addr] = self.byteMask & data
        self.processorCycles += 1; self.datMemWrCycles += 1

    def rwDM(self, addr):
        if self.dbg:
            print(' rwDM:', '-- <> mem[%04X]' % (addr))
        self.processorCycles += 1; self.dummyCycles += 1

    def WordAt(self, addr):
        addr = self.addrMask & addr
        tmp1 = self.byteMask & self.memory[addr]
        tmp2 = self.byteMask & self.memory[self.addrMask & (addr + 1)]
        return self.wordMask & ((tmp2 << 8) + tmp1)

    # Addressing modes

    def imm(self, op):
        data = self.rdPM()
        if self.siz:
            data += self.rdPM() << 8
        return op(data)

    def ro_zp(self, op):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        
        data = self.rdDM(addr)
        if self.siz:
            data += self.rdDM(hiAddr + (mask & (addr + 1))) << 8
        op(data)

    def wo_zp(self, reg):
        addr = self.rdPM()
        data = reg()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(hiAddr + (mask & (addr + 1)), data >> 8)

    def rmw_zp(self, op):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        #read memory
        data = self.rdDM(addr)
        if self.siz:
            data += self.rdDM(hiAddr + (mask & (addr + 1))) << 8
        # modify
        data = op(data)
        # write memory
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(hiAddr + (mask & (addr + 1)), data >> 8)

    def ro_zpX(self, op):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        addr = self.rdPM()
        if index < 512:                     # page 0/1 + unsigned(offset)
            hiAddr = (self.addrHighMask & index)
            addr = hiAddr + (mask & (index + addr))
            mask = self.byteMask
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
                addr = (tmp2 << 8) + tmp1
                mask = self.addrMask
                hiAddr = 0
        else:                               # base + signed(offset)
            hiAddr = 0
            mask = self.addrMask
            if addr & self.NEGATIVE:
                addr += self.addrHighMask   # sign extend
            addr = mask & (index + addr)
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(mask & (addr + 1))
                addr = (tmp2 << 8) + tmp1
        
        data = self.rdDM(addr)
        if self.siz:
            data += self.rdDM(hiAddr + (mask & (addr + 1))) << 8
        op(data)

    def wo_zpX(self, reg):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        addr = self.rdPM()
        if index < 512:                     # page 0/1 + unsigned(offset)
            hiAddr = (self.addrHighMask & index)
            mask = self.byteMask
            addr = hiAddr + (mask & (index + addr))
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
                addr = (tmp2 << 8) + tmp1
                mask = self.addrMask
                hiAddr = 0
        else:                               # base + signed(offset)
            hiAddr = 0
            mask = self.addrMask
            if addr & self.NEGATIVE:
                addr += self.addrHighMask   # sign extend
            addr = mask & (index + addr)
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(mask & (addr + 1))
                addr = (tmp2 << 8) + tmp1
        
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(hiAddr + (mask & (addr + 1)), data >> 8)

    def rmw_zpX(self, op):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = self.addrHighMask & index
        if index < 512:                     # page 0/1 + unsigned(offset)
            addr = hiAddr + (mask & (index + addr))
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
                addr = (tmp2 << 8) + tmp1
                mask = self.addrMask
                hiAddr = 0
        else:                               # base + signed(offset)
            mask = self.addrMask
            hiAddr = 0
            if addr & self.NEGATIVE:
                addr += self.addrHighMask   # sign extend
            addr = hiAddr + (mask & (index + addr))
            if self.ind:
                # first indirect
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
                addr = (tmp2 << 8) + tmp1
        # read memory
        data = self.rdDM(addr)
        if self.siz:
            data += self.rdDM(hiAddr + (mask & (addr + 1))) << 8
        # modify
        data = op(data)
        # write memory
        self.wrDM(addr, data)
        if self.siz:
           self.wrDM(hiAddr + (mask & (addr + 1)),  data >> 8)

    def ro_zpY(self, op):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.ind:
            if self.osx and not self.lscx:
                if self.MODE & self.p:
                    base = self.sp[1]
                else:
                    base = self.sp[0]
                if base < 512:
                    hiAddr = self.addrHighMask & base
                else:
                    mask = self.addrMask
                addr = hiAddr + (mask & (addr + base))
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        if index < 512:                     # page 0/1 + unsigned(offset)
            if not self.ind:
                hiAddr = (self.addrHighMask & index)
            addr = hiAddr + (mask & (index + addr))
        else:                               # base + signed(offset)
            addr = mask & (index + addr)
        
        data = self.rdDM(addr)
        if self.siz:
            data += self.rdDM(hiAddr + (mask & (addr + 1))) << 8
        op(data)

    def wo_zpY(self, reg):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.ind:
            if self.osx and not self.lscx:
                if self.MODE & self.p:
                    base = self.sp[1]
                else:
                    base = self.sp[0]
                if base < 512:
                    hiAddr = self.addrHighMask & base
                else:
                    mask = self.addrMask
                addr = hiAddr + (mask & (addr + base))
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        if index < 512:                     # page 0/1 + unsigned(offset)
            if not self.ind:
                hiAddr = (self.addrHighMask & index)
            addr = hiAddr + (mask & (index + addr))
        else:             # base + signed(offset)
            mask = self.addrMask
            if addr & self.NEGATIVE:
                addr += self.addrHighMask   # sign extend
            addr = mask & (index + addr)
        
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(hiAddr + (mask & (addr + 1)), data >> 8)

    def ro_zpI(self, op):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        # first indirect
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
        addr = (tmp2 << 8) + tmp1
        hiAddr = 0
        mask = self.addrMask
        if self.ind:
            # second indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        op(data)

    def wo_zpI(self, reg):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        # first indirect
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        hiAddr = 0
        if self.ind:
            # second indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(self.addrMask & (addr + 1), data >> 8)
        op(data)

    def ro_zpXI(self, op):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        addr = self.rdPM()
        mask = self.byteMask
        if index < 512:                     # stk/zero page + unsigned(offset)
            hiAddr = (index & self.addrHighMask)
            addr = hiAddr + (mask & (index + addr))
            # first indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
            if self.ind:
                # second indirection
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
                addr = (tmp2 << 8) + tmp1
        else:                               # base + signed(offset)
            mask = self.addrMask
            if addr & self.NEGATIVE:
                addr += self.addrHighMask   # sign extend
            addr = mask & (index + addr)
            # first indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
            if self.ind:
                # second indirection
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(mask & (addr + 1))
                addr = (tmp2 << 8) + tmp1
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        op(data)

    def wo_zpXI(self, reg):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        addr = self.rdPM()
        mask = self.byteMask
        if index < 512:                   # stk/zero page + unsigned(offset)
            hiAddr = (index & self.addrHighMask)
            addr = hiAddr + (mask & (index + addr))
            # first indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
            if self.ind:
                # second indirection
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(mask & (addr + 1))
                addr = (tmp2 << 8) + tmp1
        else:                             # base + signed(offset)
            mask = self.addrMask
            if addr & self.NEGATIVE:
                addr += self.addrHighMask  # sign extend
            addr = mask & (index + addr)
            # first indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
            if self.ind:
                # second indirection
                tmp1 = self.rdDM(addr)
                tmp2 = self.rdDM(mask & (addr + 1))
                addr = (tmp2 << 8) + tmp1

        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def ro_zpIY(self, op):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        # first indirection
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        hiAddr = 0
        if self.ind:
            # second indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        addr = mask & (index + addr)
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        op(data)

    def wo_zpIY(self, reg):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        # first indirection
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        hiAddr = 0
        if self.ind:
            # second indirection
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        addr = mask & (index + addr)

        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def ro_abs(self, op):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            addr = mask & (addr + base)
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        op(data)

    def wo_abs(self, reg):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            addr = mask & (addr + base)
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def rmw_abs(self, op):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            addr = mask & (addr + base)
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        # read memory
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        # modify
        data = op(data)
        #write memory
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def ro_absX(self, op):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        mask = self.addrMask
        addr = mask & (index + ((tmp2 << 8) + tmp1))
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        op(data)

    def wo_absX(self):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        mask = self.addrMask
        addr = mask & (index + ((tmp2 << 8) + tmp1))
        data = reg()
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)
        return

    def rmw_absX(self, op):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        mask = self.addrMask
        addr = mask & (index + ((tmp2 << 8) + tmp1))
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        # read memory
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        # modify
        data = op(data)
        # write memory
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def ro_absY(self, op):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.ind:
            if self.osx and not self.lscx:
                if self.MODE & self.p:
                    base = self.sp[1]
                else:
                    base = self.sp[0]
                addr = mask & (addr + base)
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        addr = mask & (index + addr)
        data = self.rdDM(addr)
        if self.siz:
            data = (self.rdDM(mask & (addr + 1)) << 8) + data
        return op(data)

    def wo_absY(self, reg):
        if self.oay:
            index = self.a[0]
        else:
            index = self.y[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.ind:
            if self.osx and not self.lscx:
                if self.MODE & self.p:
                    base = self.sp[1]
                else:
                    base = self.sp[0]
                addr = mask & (addr + base)
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        addr = self.addrMask & (index + addr)
        
        data = reg()
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def ro_ipp(self, op):
        self.rdPM()   # skip immediate operand, unused.
        
        addr = self.ip
        mask = self.addrMask
        if self.ind:
            tmp1 = self.rdDM(self.ip)
            self.ip = mask & (self.ip + 1)
            tmp2 = self.rdDM(self.ip) << 8
            self.ip = mask & (self.ip + 1)
            addr = tmp2 + tmp1
        tmp1 = rdDM(addr); tmp2 = 0
        if not self.ind: self.ip = mask & (self.ip + 1)
        if self.siz:
            tmp2 = self.rdDM(mask & (addr + 1)) << 8
            if not self.ind: self.ip = mask & (self.ip + 1)
        data = tmp2 + tmp1
        op(data)

    def wo_ipp(self, op):
        self.rdPM()   # skip immediate operand, unused.
        
        data = self.op()
        
        addr = self.ip
        mask = self.addrMask
        if self.ind:
            tmp1 = self.rdDM(self.ip)
            self.ip = mask & (self.ip + 1)
            tmp2 = self.rdDM(self.ip) << 8
            self.ip = mask & (self.ip + 1)
            addr = tmp2 + tmp1
        self.wrDM(addr, data)
        if not self.ind: self.ip = mask & (self.ip + 1)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)
            if not self.ind: self.ip = mask & (self.ip + 1)

    def rmw_ipp(self, op):
        self.rdPM()   # skip immediate operand, unused.
        
        addr = self.ip
        mask = self.addrMask
        if self.ind:
            tmp1 = self.rdDM(addr)
            self.ip = mask & (self.ip + 1)
            tmp2 = self.rdDM(mask & (addr + 1)) << 8
            self.ip = mask & (self.ip + 1)
            addr = tmp2 + tmp1
        # read memory
        tmp1 = self.rdDM(addr); tmp2 = 0
        if not self.ind: self.ip = mask & (self.ip + 1)
        if self.siz:
            tmp2 = self.rdDM(mask & (addr + 1)) << 8
            if not self.ind: self.ip = mask & (self.ip + 1)
        data = tmp2 + tmp1
        # modify
        data = op(data)
        # write memory
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)
    
    #
    # These routines return addresses. Used with PUL zp, JSR/JMP/PUL abs
    #

    def zp(self):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
            mask = self.addrMask
            hiAddr = 0
        return hiAddr, mask, addr
    
    def abs(self):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            addr = mask & (addr + base)
        if self.ind:
            # first indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        return mask, addr

    def absI(self):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            addr = mask & (addr + base)
        # first indirect
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(mask & (addr + 1))
        addr = (tmp2 << 8) + tmp1
        if self.ind:
            # second indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        return mask, addr

    def absXI(self):
        if self.osx and not self.lscx:
            if self.p & self.MODE:
                index = self.sp[1]
            else:
                index = self.sp[0]
        elif self.oax:
            index = self.a[0]
        else:
            index = self.x[0]

        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        addr = (tmp2 << 8) + tmp1
        mask = self.addrMask
        addr = mask & (index + addr)
        # first indirect
        tmp1 = self.rdDM(addr)
        tmp2 = self.rdDM(mask & (addr + 1))
        addr = (tmp2 << 8) + tmp1
        if self.ind:
            # second indirect
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(mask & (addr + 1))
            addr = (tmp2 << 8) + tmp1
        return mask, addr

    #
    #   Returns a signed offset. Used with the branch instructions
    #

    def rel(self, op): # ((IND) ? rel16 : rel)
        if self.ind:
            tmp1 = self.rdPM()
            tmp2 = self.rdPM()
            offset = (tmp2 << 8) + tmp1
        else:
            tmp1 = self.rdPM()
            tmp2 = 0
            if self.NEGATIVE & tmp1:
                tmp2 = self.hiByteMask
            offset = tmp2 + tmp1
        op(offset)

    #
    #   Returns a 16-bit offset. Used with the PHR/CSR instructions
    #

    def rel16(self, op):
        tmp1 = self.rdPM()
        tmp2 = self.rdPM()
        offset = (tmp2 << 8) + tmp1
        op(offset)

    #
    #   Returns a signed offset and 8-bit data. Used for BBRx/BBSx instructions
    #

    def zprel(self, op):
        addr = self.rdPM()
        mask = self.byteMask
        hiAddr = 0
        if self.osx and not self.lscx:
            if self.MODE & self.p:
                base = self.sp[1]
            else:
                base = self.sp[0]
            if base < 512:
                hiAddr = self.addrHighMask & base
            else:
                mask = self.addrMask
            addr = hiAddr + (mask & (addr + base))
        if self.ind:
            tmp1 = self.rdDM(addr)
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
            addr = (tmp2 << 8) + tmp1
        
        data = self.rdDM(addr)

        tmp1 = self.rdPM()
        tmp2 = 0
        if self.NEGATIVE & tmp1:
            tmp2 = self.addrHighMask
        offset = tmp2 + tmp1
        op(offset, data)

    # ALU Flags Functions

    def FlagsNZ(self, value):
        self.p &= ~(self.NEGATIVE | self.ZERO)
        if value == 0:
            self.p |= self.ZERO
        if self.siz:
            self.p |= self.NEGATIVE & (value >> 8)
        else:
            self.p |= self.NEGATIVE &  value

#
#   Stack operations
#

    def PUSH(self, data):
        if self.osx:
            if self.siz:
                self.wrDM(self.x[0], data >> 8)
                addr = self.addrMask & (self.x[0] - 1)
                if self.x[0] < 512:
                    hiAddr = self.hiByteMask & self.x[0]
                    addr = hiAddr + (self.byteMask & addr)
                self.x[0] = addr
            self.wrDM(self.x[0], data)
            addr = self.addrMask & (self.x[0] - 1)
            if self.x[0] < 512:
                hiAddr = self.hiByteMask & self.x[0]
                addr = hiAddr + (self.byteMask & addr)
            self.x[0] = addr
        else:
            if self.p & self.MODE:
                sel = 1
            else:
                sel = 0
            if self.siz:
                self.wrDM(self.sp[sel], data >> 8)
                addr = self.addrMask & (self.sp[sel] - 1)
                if self.sp[sel] < 512:
                    hiAddr = self.hiByteMask & self.sp[sel]
                    addr = hiAddr + (self.byteMask & addr)
                self.sp[sel] = addr
            self.wrDM(self.sp[sel], data)
            addr = self.addrMask & (self.sp[sel] - 1)
            if self.sp[sel] < 512:
                hiAddr = self.hiByteMask & self.sp[sel]
                addr = hiAddr + (self.byteMask & addr)
            self.sp[sel] = addr

    def PULL(self):
        if self.osx:
            addr = self.addrMask & (self.x[0] + 1)
            if self.x[0] < 512:
                hiAddr = self.hiByteMask & self.x[0]
                addr = hiAddr + self.byteMask & addr
            data = self.rdDM(addr)
            if self.siz:
                addr = self.addrMask & (addr + 1)
                if self.x[0] < 512:
                    hiAddr = self.hiByteMask & self.x[0]
                    addr = hiAddr + self.byteMask & addr
                data = (self.rdDM(addr) << 8) + data
            self.x[0] = addr
        else:
            if self.p & self.MODE:
                sel = 1
            else:
                sel = 0
            addr = self.addrMask & (self.sp[sel] + 1)
            if self.sp[sel] < 512:
                hiAddr = self.hiByteMask & self.sp[sel]
                addr = hiAddr + self.byteMask & addr
            data = self.rdDM(addr)
            if self.siz:
                addr = self.addrMask & (addr + 1)
                if self.sp[sel] < 512:
                    hiAddr = self.hiByteMask & self.sp[sel]
                    addr = hiAddr + self.byteMask & addr
                data = (self.rdDM(addr) << 8) + data
            self.sp[sel] = addr

        return data

    def opPHP(self):
        self.siz = False            # for 8-bit stack push
        tmp = self.BREAK | self.p   # force B bit in P on stack
        self.PUSH(tmp)
    
    def opPLP(self):
        self.siz = False            # force 8-bit stack pop
        tmp  =  self.PULL()         # pop 8-bit value from stack
        tmp |=  self.BREAK          # set B bit (cleared on stack on NMI/INT)
        tmp &= ~self.MODE           # Mode can only be set by RTI instruction
        tmp |=  self.MODE & self.p  # keep current setting of Mode bit
        self.p = tmp                # update P
    
    def opPHA(self):
        if self.oax:
            data = self.x[0]
        elif self.oay:
            data = self.y[0]
        else:
            data = self.a[0]
        self.PUSH(data)
    
    def opPLA(self):
        data = self.PULL()
        self.FlagsNZ(data)
        if self.oax:
            self.x[0] = data
        elif self.oay:
            self.y[0] = data
        else:
            self.a[0] = data
    
    def opPHX(self):
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            data = self.sp[sel]
        elif self.oax:
            data = self.a[0]
        else:
            data = self.x[0]
        self.PUSH(data)
    
    def opPLX(self):
        data = self.PULL()
        self.FlagsNZ(data)
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            self.sp[sel] = sel
        elif self.oax:
            self.a[0] = data
        else:
            self.x[0] = data
    
    def opPHY(self):
        if self.oay:
            data = self.a[0]
        else:
            data = self.y[0]
        self.PUSH(data)

    def opPLY(self):
        data = self.PULL()
        self.FlagsNZ(data)
        if self.oay:
            self.a[0] = data
        else:
            self.y[0] = data
    
    def opPSH_zp(self):
        osx = self.osx; self.osx = False
        hiAddr, mask, addr = self.zp()
        self.osx = osx
        tmp1 = self.rdDM(addr)
        tmp2 = 0
        if self.siz:
            tmp2 = self.rdDM(hiAddr + (mask & (addr + 1)))
        data = (tmp2 << 8) + tmp1
        self.PUSH(data)
        
    def opPUL_zp(self):
        osx = self.osx; self.osx = False
        hiAddr, mask, addr = self.zp()
        self.osx = osx
        self.rwDM(addr)
        data = self.PULL()
        self.FlagsNZ(data)
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(hiAddr + (mask & (addr + 1)), data >> 8)
        
    def opPSH_abs(self):
        osx = self.osx; self.osx = False
        mask, addr = self.abs()
        self.osx = osx
        tmp1 = self.rdDM(addr)
        tmp2 = 0
        if self.siz:
            tmp2 = self.rdDM(mask & (addr + 1))
        data = (tmp2 << 8) + tmp1
        self.PUSH(data)

    def opPUL_abs(self):
        osx = self.osx; self.osx = False
        mask, addr = self.abs()
        self.osx = osx
        self.rwDM(addr)
        data = self.PULL()
        self.FlagsNZ(data)
        self.wrDM(addr, data)
        if self.siz:
            self.wrDM(mask & (addr + 1), data >> 8)

    def opPHR(self, offset):
        addr = self.addrMask & (self.pc + offset)
        self.rwDM(addr)
        if self.ind:    # CSR rel16
            self.siz = True
            self.PUSH(self.addrMask & (self.pc - 1))
            self.pc = addr
        else:
            self.siz = True
            self.PUSH(addr)
        self.clrPrefixFlags()
            
    def opADJ(self, data):
        if self.siz:
            pass
        elif self.NEGATIVE & data:
            data = self.wordMask & (self.hiByteMask | data)

        if self.osx and not self.lscx:
            self.x[0] = self.addrMask & (self.x[0] + data)
        else:
            if self.p & self.MODE:
                sel = 1
            else:
                sel = 0
            self.sp[sel] = self.addrMask & (self.sp[sel] + data)

#
#   Subroutine Call/Return Operations
#

    def opJSR(self):
        osx = self.osx; self.osx = False  # jsr abs,S not supported
        mask, addr = self.abs()   # may be better / more useful if IND enabled
                                  # absXI addressing. May provide a more useful
                                  # model for OOP using base/stack relative ptrs
        self.osx = osx
        self.siz = True
        self.PUSH(mask & (self.pc - 1))

        self.pc = addr

    def opRTI(self):        # may need to be trapped if used in User mode
        self.osx = False
        self.siz = False
        self.p = (self.PULL() | self.BREAK)
        self.siz = True
        self.pc = self.addrMask & (self.PULL() + 1)
    
    def opRTS(self):
        self.siz = True
        self.pc = self.addrMask & (self.PULL() + 1)
        
#
#   Branch Operations
#

    def opBPL(self, offset):  # ((SIZ) ? BGT : BPL)
        if self.siz:  # ~((N ^ V) | Z)
            cc = (((self.NEGATIVE & self.p) >> 7) ^ \
                  ((self.OVERFLOW & self.p) >> 6)) | \
                  ((self.ZERO     & self.p) >> 1)
        else:         # ~N
            cc = (self.NEGATIVE & self.p) >> 7

        if not cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBMI(self, offset):  # ((SIZ) ? BLE : BMI)
        if self.siz:  # ((N ^ V) | Z)
            cc = (((self.NEGATIVE & self.p) >> 7) ^ \
                  ((self.OVERFLOW & self.p) >> 6)) | \
                  ((self.ZERO     & self.p) >> 1)
        else:         # N
            cc = (self.NEGATIVE & self.p) >> 7

        if cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBVC(self, offset):  # ((SIZ) ? BGE : BVC)
        if self.siz:  # ~(N ^ V)
            cc = ((self.NEGATIVE & self.p) >> 7) ^ \
                 ((self.OVERFLOW & self.p) >> 6)
        else:         # ~V
            cc = (self.OVERFLOW & self.p) >> 6

        if not cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBVS(self, offset):  # ((SIZ) ? BLT : BVC)
        if self.siz:  # (N ^ V)
            cc = ((self.NEGATIVE & self.p) >> 7) ^ \
                 ((self.OVERFLOW & self.p) >> 6)
        else:         # V
            cc = ((self.OVERFLOW & self.p) >> 6)

        if cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBCC(self, offset):  # ((SIZ) ? BLS : BCC)
        # if self.siz:  # ~C
        # else:         # ~C
        cc = (self.CARRY & self.p)

        if not cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBCS(self, offset):  # ((SIZ) ? BHI : BCS)
        # if self.siz:  # C
        # else:         # C
        cc = (self.CARRY & self.p)

        if cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBNE(self, offset):  # ((SIZ) ? BLO : BNE)
        if self.siz:  # ~(C | Z)
            cc = ((self.ZERO & self.p) >> 1) | (self.CARRY & self.p)
        else:         # ~Z
            cc = ((self.ZERO & self.p) >> 1)

        if not cc:
                self.pc = self.addrMask & (self.pc + offset)

    def opBEQ(self, offset):  # ((SIZ) ? BHS : BEQ)
        if self.siz:  # (C | Z)
            cc = ((self.ZERO & self.p) >> 1) | (self.CARRY & self.p)
        else:         # Z
            cc = ((self.ZERO & self.p) >> 1)

        if cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBRA(self, offset):    # Unconditional branch
        self.pc = self.addrMask & (self.pc + offset)

#
#   Logical Unit Operations
#

    def opORA(self, data):
        if self.oax:
            reg = self.x[0]
        elif self.oay:
            reg = self.y[0]
        else:
            reg = self.a[0]

        if self.siz:
            reg = self.wordMask & (reg | data)
        else:
            reg = self.byteMask & (reg | data)

        if self.oax:
            self.x[0] = reg
        elif self.oay:
            self.y[0] = reg
        else:
            self.a[0] = reg
        self.FlagsNZ(reg)

    def opAND(self, data):
        if self.oax:
            reg = self.x[0]
        elif self.oay:
            reg = self.y[0]
        else:
            reg = self.a[0]

        if self.siz:
            reg = self.wordMask & (reg & data)
        else:
            reg = self.byteMask & (reg & data)

        if self.oax:
            self.x[0] = reg
        elif self.oay:
            self.y[0] = reg
        else:
            self.a[0] = reg
        self.FlagsNZ(reg)

    def opEOR(self, data):
        if self.oax:
            reg = self.x[0]
        elif self.oay:
            reg = self.y[0]
        else:
            reg = self.a[0]

        if self.siz:
            reg = self.wordMask & (reg ^ data)
        else:
            reg = self.byteMask & (reg ^ data)

        if self.oax:
            self.x[0] = reg
        elif self.oay:
            self.y[0] = reg
        else:
            self.a[0] = reg
        self.FlagsNZ(reg)

    def opBIT(self, data):  # Used for BIT[.[x|xw|y|yw|w] addr
        reg = self.a[0]
        if (self.oax or self.oay):
            if self.oay:
                reg = self.y[0]
            else:
                reg = self.x[0]

        self.p &= ~(self.ZERO | self.NEGATIVE | self.OVERFLOW)
        if (reg & data) == 0:
            self.p |= self.ZERO
        if self.siz:
            self.p |= (data >> self.BYTE_WIDTH) & \
                      (self.NEGATIVE | self.OVERFLOW)
        else:
            self.p |= data & (self.NEGATIVE | self.OVERFLOW)

    def opBTI(self, data):  # Used for BIT[.[x|xw|y|yw|w] #imm
        reg = self.a[0]
        if (self.oax or self.oay):
            if self.oay:
                reg = self.y[0]
            else:
                reg = self.x[0]

        self.p &= ~(self.ZERO)
        if (reg & data) == 0:
            self.p |= self.ZERO

    def opTRB(self, data):
        reg = self.a[0]
        if (self.oax or self.oay):
            if self.oay:
                reg = self.y[0]
            else:
                reg = self.x[0]

        self.p &= ~self.ZERO
        if (reg & data) == 0:
            self.p |= self.ZERO

        if self.siz:
            return self.wordMask & (data & ~reg)
        return self.byteMask & (data & ~reg)

    def opTSB(self, data):
        reg = self.a[0]
        if (self.oax or self.oay):
            if self.oay:
                reg = self.y[0]
            else:
                reg = self.x[0]

        self.p &= ~self.ZERO
        if (reg & data) == 0:
            self.p |= self.ZERO

        if self.siz:
            return self.wordMask & (data | reg)
        return self.byteMask & (data | reg)

    # Rockwell Bit-Oriented Operations

    def opRMBx(self, data):
        return data & self.bitMask

    def opSMBx(self, data):
        return data | self.bitMask

    def opBBRx(self, offset, data):
        cc = data & self.bitMask
        if not cc:
            self.pc = self.addrMask & (self.pc + offset)

    def opBBSx(self, offset, data):
        cc = data & self.bitMask
        if cc:
            self.pc = self.addrMask & (self.pc + offset)
#
#   Shift Unit Operations
#

    def opASLr(self):
        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        if self.oax:
            regVal = self.x[0]
        elif self.oay:
            regVal = self.y[0]
        else:
            regVal = self.a[0]
        cin = self.CARRY & self.p

        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        if self.siz:
            self.p |= self.NEGATIVE & (regVal >>  7)
            self.p |= self.CARRY    & (regVal >> 15)

            if self.ind:
                self.p &= ~self.OVERFLOW
                self.p |= self.OVERFLOW & ((regVal >> 9) ^ (regVal >> 8))

                regVal = self.wordMask  & ((regVal << 1) | cin)
            else:
                regVal = self.wordMask  &  (regVal << 1)

            if regVal == 0:
                self.p |= self.ZERO
        else:
            self.p |= self.NEGATIVE & regVal
            self.p |= self.CARRY & (regVal >> 7)

            regVal = self.byteMask & (regVal << 1)

            if regVal == 0:
                self.p |= self.ZERO

        if self.oax:
            self.x[0] = regVal
        elif self.oay:
            self.y[0] = regVal
        else:
            self.a[0] = regVal

    def opASLm(self, data):
        memVal = int(data)

        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        if self.siz:
            if self.NEGATIVE & (memVal >> 8):
                self.p |= self.CARRY

            memVal = self.wordMask & (memVal << 1)

            if memVal:
                self.p |= self.NEGATIVE & (memVal >> 8)
            else:
                self.p |= self.ZERO
        else:
            if self.NEGATIVE & memVal:
                self.p |= self.CARRY

            memVal = self.byteMask & (memVal << 1)

            if memVal:
                self.p |= self.NEGATIVE & memVal
            else:
                self.p |= self.ZERO

        return memVal

    def opROLr(self):
        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        if self.oax:
            regVal = self.x[0]
        elif self.oay:
            regVal = self.y[0]
        else:
            regVal = self.a[0]

        if self.siz:
            if self.CARRY & self.p:
                if self.NEGATIVE & (regVal >> 8):
                    pass
                else:
                    self.p &= ~self.CARRY

                regVal = self.wordMask & ((regVal << 1) | 1)
            else:
                if self.NEGATIVE & (regVal >> 8):
                    self.p |= self.CARRY

                regVal = self.wordMask & (regVal << 1)
        else:
            if self.CARRY & self.p:
                if self.NEGATIVE & regVal:
                    pass
                else:
                    self.p &= ~self.CARRY

                regVal = self.byteMask & ((regVal << 1) | 1)
            else:
                if self.NEGATIVE & regVal:
                    self.p |= self.CARRY
                regVal = self.byteMask & (regVal << 1)

        self.FlagsNZ(regVal)

        if self.oax:
            self.x[0] = regVal
        elif self.oay:
            self.y[0] = regVal
        else:
            self.a[0] = regVal

    def opROLm(self, data):
        memVal = int(data)

        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        if self.siz:
            if self.CARRY & self.p:
                if self.NEGATIVE & (memVal >> 8):
                    pass
                else:
                    self.p &= ~self.CARRY

                memVal = self.wordMask & ((memVal << 1) | 1)
            else:
                if self.NEGATIVE & (memVal >> 8):
                    self.p |= self.CARRY

                memVal = self.wordMask & (memVal << 1)
        else:
            if self.CARRY & self.p:
                if self.NEGATIVE & rmemVal:
                    pass
                else:
                    self.p &= ~self.CARRY

                memVal = self.byteMask & ((memVal << 1) | 1)
            else:
                if self.NEGATIVE & memVal:
                    self.p |= self.CARRY

                memVal = self.byteMask & (memVal << 1)

        self.FlagsNZ(memVal)
        return memVal

    def opLSRr(self):
        if self.oax:
            regVal = self.x[0]
        elif self.oay:
            regVal = self.y[0]
        else:
            regVal = self.a[0]

        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        self.p |= self.CARRY & regVal

        if self.siz:
            if self.ind:  # ASR
                sign  = ((self.OVERFLOW & self.p) << 9)
                sign ^= regVal & (1 << 15)
                if sign:
                    self.p |= self.NEGATIVE
                self.p &= ~self.OVERFLOW
                self.p |= self.OVERFLOW & ((regVal >> 9) ^ (regVal >> 8))

                regVal = sign | ((self.wordMask & regVal) >> 1)
            else:         # LSR
                regVal = (self.wordMask & regVal) >> 1
        else:
            regVal = (self.byteMask & regVal) >> 1

        if regVal == 0:
            self.p |= self.ZERO

        if self.oax:
            self.x[0] = regVal
        elif self.oay:
            self.y[0] = regVal
        else:
            self.a[0] = regVal

    def opLSRm(self, data):
        memVal = int(data)

        self.p &= ~(self.NEGATIVE | self.ZERO | self.CARRY)
        self.p |= self.CARRY & memVal

        if self.siz:
            memVal = (self.wordMask & memVal) >> 1
        else:
            memVal = (self.byteMask & memVal) >> 1

        self.FlagsNZ(memVal)
        return memVal

    def opRORr(self):
        if self.oax:
            regVal = self.x[0]
        elif self.oay:
            regVal = self.y[0]
        else:
            regVal = self.a[0]

        if self.CARRY & self.p:
            if self.CARRY & regVal:
                pass
            else:
                self.p &= ~self.CARRY
            if self.siz:
                regVal = ((self.wordMask & regVal) >> 1) | (1 << 15)
            else:
                regVal = ((self.byteMask & regVal) >> 1) | (1 <<  7)
        else:
            if self.CARRY & regVal:
                self.p |= self.CARRY
            if self.siz:
                regVal = (self.wordMask & regVal) >> 1
            else:
                regVal = (self.byteMask & regVal) >> 1
        self.FlagsNZ(regVal)

        if self.oax:
            self.x[0] = regVal
        elif self.oay:
            self.y[0] = regVal
        else:
            self.a[0] = regVal

    def opRORm(self, data):
        memVal = int(data)
        if self.CARRY & self.p:
            if self.CARRY & memVal:
                pass
            else:
                self.p &= ~self.CARRY

            if self.siz:
                memVal = ((self.wordMask & memVal) >> 1) | (1 << 15)
            else:
                memVal = ((self.wordMask & memVal) >> 1) | (1 <<  7)
        else:
            if self.CARRY & memVal:
                self.p |= self.CARRY

            if self.siz:
                memVal = (self.wordMask & memVal) >> 1
            else:
                memVal = (self.byteMask & memVal) >> 1

        self.FlagsNZ(memVal)
        return memVal

#
#   Arithmetic Unit Operations
#

    def opADC(self, data):
        if self.siz:
            sign = self.NEGATIVE << 8
            mask = self.wordMask
        else:
            sign = self.NEGATIVE
            mask = self.byteMask

        if self.oax:
            reg = self.x[0]
        elif self.oay:
            reg = self.y[0]
        else:
            reg = self.a[0]

        auL = mask & reg
        auR = mask & data
        cin = self.CARRY & self.p

        if self.p & self.DECIMAL and not self.siz:
            cy3 = 0; cy7 = 0; da0 = 0; da1 = 0
            loSum = (auL & 0xF) + (auR & 0xF) + cin
            if loSum > 9:
                da0 = 6
                cy3 = 1
            hiSum = ((auL >> 4) & 0xF) + ((auR >> 4) & 0xF) + cy3
            if hiSum > 9:
                da1 = 6
                cy7 = 1

            # 6502 sets ALU flags using result before decimal adjust
            # 65C02/M65C02A set ALU flags after decimal adjust
            # ALU outputs are decimally adjusted
            loSum = (loSum + da0) & 0xF
            hiSum = (hiSum + da1) & 0xF
            sum   = (hiSum << 4) + loSum

            self.p &= ~(self.CARRY | self.OVERFLOW | self.NEGATIVE | self.ZERO)
            if sum == 0:
                self.p |= self.ZERO
            else:
                self.p |= sign & sum

            if cy7 == 1:
                self.p |= self.CARRY
            if (~(auL ^ auR) & (auL ^ sum)) & sign:
                self.p |= self.OVERFLOW
        else:
            sum = auL + auR + cin

            self.p &= ~(self.CARRY | self.OVERFLOW | self.NEGATIVE | self.ZERO)
            if (~(auL ^ auR) & (auL ^ sum)) & sign:
                self.p |= self.OVERFLOW
            if sum > mask:
                self.p |= self.CARRY
                sum &= mask
            if sum == 0:
                self.p |= self.ZERO
            else:
                self.p |= (sign & sum) >> 8

        reg = mask & sum

        if self.oax:
            self.x[0] = reg
        elif self.oay:
            self.y[0] = reg
        else:
            self.a[0] = reg

    def opSBC(self, data):
        if self.siz:
            sign = self.NEGATIVE << 8
            mask = self.wordMask
        else:
            sign = self.NEGATIVE
            mask = self.byteMask

        if self.oax:
            reg = self.x[0]
        elif self.oay:
            reg = self.y[0]
        else:
            reg = self.a[0]

        auL = mask & reg
        auR = mask & ~data
        cin = self.CARRY & self.p

        if self.p & self.DECIMAL and not self.siz:
            cy3 = 1; cy7 = 0; da0 = 0; da1 = 0
            loSum = (auL & 0xF) + (auR & 0xF) + cin
            if loSum <= 15:
                cy3 = 0
                da0 = 10
            hiSum = ((auL >> 4) & 0xF) + ((auR >> 4) & 0xF) + cy3
            if hiSum <= 15:
                da1 = 10
            else: cy7 = 1

            # 6502 sets ALU flags using result before decimal adjust
            # 65C02/M65C02A set ALU flags after decimal adjust
            # ALU outputs are decimally adjusted
            loSum = (loSum + da0) & 0xF
            hiSum = (hiSum + da1) & 0xF
            sum   = (hiSum << 4) + loSum

            self.p &= ~(self.CARRY | self.ZERO | self.NEGATIVE | self.OVERFLOW)
            if sum == 0:
                self.p |= self.ZERO
            else:
                self.p |= sign & sum
            if cy7 == 1:
                self.p |= self.CARRY
            if (~(auL ^ auR) & (auL ^ sum)) & sign:
                self.p |= self.OVERFLOW
        else:
            sum = auL + auR + cin

            self.p &= ~(self.CARRY | self.ZERO | self.OVERFLOW | self.NEGATIVE)
            if (~(auL ^ auR) & (auL ^ sum)) & sign:
                self.p |= self.OVERFLOW
            if (mask & sum) == 0:
                self.p |= self.ZERO
            if sum > mask:
                self.p |= self.CARRY
                sum &= mask
            self.p |= (sign & sum) >> 8

        reg = mask & sum

        if self.oax:
            self.x[0] = reg
        elif self.oay:
            self.y[0] = reg
        else:
            self.a[0] = reg

#
#   Increment/Decrement/Compare Unit OPerations
#
    #
    #   Increment Operations
    #
    
    def opINC(self):
        if self.oax:
            if self.siz:
                self.x[0] = self.wordMask & (self.x[0] + 1)
            else:
                self.x[0] = self.byteMask & (self.x[0] + 1)
            self.FlagsNZ(self.x[0])
        elif self.oay:
            if self.siz:
                self.y[0] = self.wordMask & (self.y[0] + 1)
            else:
                self.y[0] = self.byteMask & (self.y[0] + 1)
            self.FlagsNZ(self.y[0])
        else:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] + 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] + 1)
            self.FlagsNZ(self.a[0])

    def opINX(self):
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            if self.siz:
                self.sp[sel] = self.wordMask & (self.sp[sel] + 1)
                self.FlagsNZ(self.sp[sel])
            else:
                self.sp[sel] = self.byteMask & (self.sp[sel] + 1)
                self.FlagsNZ(self.sp[sel])
                self.sp[sel] |= 0x0100
        elif self.oax:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] + 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] + 1)
            self.FlagsNZ(self.a[0])
        else:
            if self.siz:
                self.x[0] = self.wordMask & (self.x[0] + 1)
            else:
                self.x[0] = self.byteMask & (self.x[0] + 1)
            self.FlagsNZ(self.x[0])

    def opINY(self):
        if self.oay:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] + 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] + 1)
            self.FlagsNZ(self.a[0])
        else:
            if self.siz:
                self.y[0] = self.wordMask & (self.y[0] + 1)
            else:
                self.y[0] = self.byteMask & (self.y[0] + 1)
            self.FlagsNZ(self.y[0])

    def opINCm(self, data):
        tmp = int(data)
        if self.siz:
            tmp = self.wordMask & (tmp + 1)
        else:
            tmp = self.byteMask & (tmp + 1)
        self.FlagsNZ(tmp)
        return tmp

    #
    #   Decrement Operations
    #

    def opDEC(self):
        if self.oax:
            if self.siz:
                self.x[0] = self.wordMask & (self.x[0] - 1)
            else:
                self.x[0] = self.byteMask & (self.x[0] - 1)
            self.FlagsNZ(self.x[0])
        elif self.oay:
            if self.siz:
                self.y[0] = self.wordMask & (self.y[0] - 1)
            else:
                self.y[0] = self.byteMask & (self.y[0] - 1)
            self.FlagsNZ(self.y[0])
        else:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] - 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] - 1)
            self.FlagsNZ(self.a[0])
            
    def opDEX(self):
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            if self.siz:
                self.sp[sel] = self.wordMask & (self.sp[sel] - 1)
                self.FlagsNZ(self.sp[sel])
            else:
                self.sp[sel] = self.byteMask & (self.sp[sel] - 1)
                self.FlagsNZ(self.sp[sel])
                self.sp[sel] |= 0x0100
        elif self.oax:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] - 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] - 1)
            self.FlagsNZ(self.a[0])
        else:
            if self.siz:
                self.x[0] = self.wordMask & (self.x[0] - 1)
            else:
                self.x[0] = self.byteMask & (self.x[0] - 1)
            self.FlagsNZ(self.x[0])

    def opDEY(self):
        if self.oay:
            if self.siz:
                self.a[0] = self.wordMask & (self.a[0] - 1)
            else:
                self.a[0] = self.byteMask & (self.a[0] - 1)
            self.FlagsNZ(self.a[0])
        else:
            if self.siz:
                self.y[0] = self.wordMask & (self.y[0] - 1)
            else:
                self.y[0] = self.byteMask & (self.y[0] - 1)
            self.FlagsNZ(self.y[0])

    def opDECm(self, data):
        tmp = int(data)
        if self.siz:
            tmp = self.wordMask & (tmp - 1)
        else:
            tmp = self.byteMask & (tmp - 1)
        self.FlagsNZ(tmp)
        return tmp
        
    #
    # Compare Operations
    #
    
    def _CMP(self, regVal, memVal):
        if self.siz:
            mask = self.wordMask
            sign = self.NEGATIVE << 8
        else:
            mask = self.byteMask
            sign = self.NEGATIVE

        auL = mask & regVal
        auR = mask & (~memVal)

        sum = auL + auR + 1

        self.p &= ~(self.CARRY | self.ZERO | self.NEGATIVE)
        if sum > mask:
            self.p |= self.CARRY
        if (mask & sum) == 0:
            self.p |= self.ZERO
        if sign & sum:
            self.p |= self.NEGATIVE

        if self.siz:
            if (~(auL ^ auR) & (auL ^ sum)) & sign:
                self.p |= self.OVERFLOW
            else:
                self.p &= ~self.OVERFLOW    

    def opCMP(self, memVal):
        if self.oax:
            regVal = int(self.x[0])
        elif self.oay:
            regVal = int(self.y[0])
        else:
            regVal = int(self.a[0])
        
        self._CMP(regVal, memVal)

    def opCPX(self, memVal):
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            regVal = self.sp[sel]
        elif self.oax:
            regVal = int(self.a[0])
        else:
            regVal = int(self.x[0])

        self._CMP(regVal, memVal)

    def opCPY(self, memVal):
        if self.oay:
            regVal = int(self.a[0])
        else:
            regVal = int(self.y[0])

        self._CMP(regVal, memVal)

#
#   Load/Store/Transfer Operations
#

    def opLDA(self, data):
        if self.oax:
            self.x[0] = data
        elif self.oay:
            self.y[0] = data
        else:
            self.a[0] = data
        self.FlagsNZ(data)

    def opLDX(self, data):
        if self.osx:
            if self.MODE & self.p:
                if self.ind: stk = 0
                else: stk = 1
            else: stk = 0
            
            if self.siz:
                self.sp[stk] = self.wordMask & data
            else:
                self.sp[stk] = 256 + (self.byteMask & data)
        elif self.oax:
            self.a[0] = data
        else:
            self.x[0] = data
        self.FlagsNZ(data)

    def opLDY(self, data):
        if self.oay:
            self.a[0] = data
        else:
            self.y[0] = data
        self.FlagsNZ(data)

    def opSTA(self):
        if self.oax:
            data = self.x[0]
        elif self.oay:
            data = self.y[0]
        else:
            data = self.a[0]
        return data

    def opSTX(self):
        if self.osx:
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
            data = self.sp[sel]
        elif self.oax:
            data = self.a[0]
        else:
            data = self.x[0]
        return data

    def opSTY(self):
        if self.oax:
            data = self.a[0]
        else:
            data = self.y[0]
        return data

    def opSTZ(self):
        return 0

    def opTAX(self):
        if self.osx:    # TAS / TAU (only in Kernel mode)
            if self.MODE & self.p:
                if self.ind: stk = 0
                else: stk = 1
            else: stk = 0

            if self.siz:
                self.sp[stk] = self.a[0]
            else:
                self.sp[stk] = 256 + (self.byteMask & self.a[0])
        else:
            if self.siz:
                self.x[0] = self.a[0]
            else:
                self.x[0] = self.byteMask & self.a[0]
            self.FlagsNZ(self.x[0])

    def opTXA(self):
        if self.oay:    # TXY
            if self.siz:
                self.y[0] = self.x[0]
            else:
                self.y[0] = self.byteMask & self.x[0]
            self.FlagsNZ(self.y[0])
        else:
            if self.siz:
                self.a[0] = self.x[0]
            else:
                self.a[0] = self.byteMask & self.x[0]
            self.FlagsNZ(self.a[0])

    def opTAY(self):
        if self.siz:
            self.y[0] = self.a[0]
        else:
            self.y[0] = self.byteMask & self.a[0]
        self.FlagsNZ(self.y[0])

    def opTYA(self):
        if self.oax:    # TYX
            if self.siz:
                self.x[0] = self.y[0]
            else:
                self.x[0] = self.byteMask & self.y[0]
            self.FlagsNZ(self.x[0])
        else:
            if self.siz:
                self.a[0] = self.y[0]
            else:
                self.a[0] = self.byteMask & self.y[0]
            self.FlagsNZ(self.a[0])

    def opTXS(self):
        if self.MODE & self.p:
            if self.ind: stk = 0  # TXU (only in Kernel mode)
            else: stk = 1
        else: stk = 0

        if self.siz:
            self.sp[stk] = self.x[0]
        else:
            self.sp[stk] = 256 + (self.byteMask & self.x[0])

    def opTSX(self):
        if self.MODE & self.p:
            if self.ind: stk = 0
            else: stk = 1
        else: stk = 0

        if self.oax:    # TSA / TUA (only in Kernel mode)
            if self.siz:
                self.a[0] = self.sp[stk]
            else:
                self.a[0] = self.byteMask & self.sp[stk]
            self.FlagsNZ(self.a[0])
        else:
            if self.siz:
                self.x[0] = self.sp[stk]
            else:
                self.x[0] = self.byteMask & self.sp[stk]
            self.FlagsNZ(self.x[0])

#
#   Register Stack Operations
#

    def opDUP(self):
        if self.oax:                  # DUP X
            self.x[2] = self.x[1]
            self.x[1] = self.x[0]
        elif self.oay:                # DUP Y
            self.y[2] = self.y[1]
            self.y[1] = self.y[0]
        elif self.siz or self.ind:
            if self.siz and self.ind: # XIA
                tmp = self.ip
                self.ip   = self.a[0]
                self.a[0] = tmp
            elif self.ind:            # TAI
                self.ip = self.a[0]
            else:                     # TIA
                self.a[0] = self.ip
        else:                         # DUP A
            self.a[2] = self.a[1]
            self.a[1] = self.a[0]
    
    def opSWP(self):
        if self.oax:                  # SWP X
            tmp = self.x[1]
            self.x[0] = self.x[1]
            self.x[1] = tmp
        elif self.oay:                # SWP Y
            tmp = self.y[1]
            self.y[0] = self.y[1]
            self.y[1] = tmp
        elif self.ind:                # SWB
            tmp1 = self.byteMask &  self.a[0]
            tmp2 = self.byteMask & (self.a[0] >> self.BYTE_WIDTH)
            self.a[0] = (tmp1 << self.BYTE_WIDTH) | tmp2
        else:                         # SWP A
            tmp = self.a[0]
            self.a[0] = self.a[1]
            self.a[1] = tmp
   
    def opROT(self):
        if self.oax:                  # ROT X
            tmp = self.x[0]
            self.x[0] = self.x[1]
            self.x[1] = self.x[2]
            self.x[2] = tmp
        elif self.oay:                # ROT Y
            tmp = self.y[0]
            self.y[0] = self.y[1]
            self.y[1] = self.y[2]
            self.y[2] = tmp
        elif self.ind:                # REV
            tmp = '%s' % bin(self.a[0])[2:]
            if len(tmp) < 16:
                tmp = '0' * (16 - len(tmp)) + tmp
            # print('--1 REV:', tmp)
            tmp = tmp[::-1]
            # print('--2 REV:', tmp)
            self.a[0] = self.wordMask & int(tmp, base=2)
        else:                         # ROT A
            tmp = self.a[0]
            self.a[0] = self.a[1]
            self.a[1] = self.a[2]
            self.a[2] = tmp

#
#   FORTH VM Operations
#

    def opNXT(self):
        tmp1 = self.rdDM(self.ip)
        self.ip = self.addrMask & (self.ip + 1)
        tmp2 = self.rdDM(self.ip)
        self.ip = self.addrMask & (self.ip + 1)
        codeFieldAddr = (tmp2 << 8) + tmp1
        self.wp = codeFieldAddr
        if self.ind:
            tmp1 = self.rdDM(self.wp)
            tmp2 = self.rdDM(self.addrMask & (self.wp + 1))
            codeFieldAddr = (tmp2 << 8) + tmp1
        self.pc = codeFieldAddr
    
    def opPHI(self):
        if self.osx:                # Change default stack for PHI
            self.osx = False        # change default to S, Sk or Su
        else:
            self.osx = True         # change default to AUX, Sx

        if self.ind:                # if IND, push WP
            data = self.wp
        else:
            data = self.ip          # else IP
        self.siz = True             # Force 16-bit stack operation
        self.PUSH(data)
   
    def opINI(self):
        if self.ind:
            self.wp = self.wordMask & (self.wp + 1)
        else:
            self.ip = self.wordMask & (self.ip + 1)
    
    def opPLI(self):
        if self.osx:                # Change default stack for PHI
            self.osx = False        # change default to S, Sk or Su
        else:
            self.osx = True         # change default to AUX, Sx

        self.siz = True             # Force 16-bit stack operation
        data = self.PULL()
        if self.ind:                # if IND, pull WP
            self.wp = data
        else:                       # else IP
            self.ip = data
    
    def opENT(self):
        if self.osx:
            self.osx = False        # use PSP instead of the RSP
            if self.MODE & self.p:
                sel = 1
            else:
                sel = 0
        else:
            self.osx = True         # use RSP
        
        self.siz = True
        self.PUSH(self.ip)
        
        self.ip = self.addrMask & (self.wp + 2)
        
        self.opNxt()
#
#   Miscellaneous Instructions
#

    def opMOV(self):
        """ MOV #imm
        
            This routine provides a block move for bytes. The single byte
            operand of the instruction configures the instruction to perform a
            conitnuous block move, or to stop after each move is made. The block
            move mode cannot be interrupted, and the single move mode allows a
            simple way to allow a block move to be interrupted. If the msb of
            the operand byte is a 1, the single move mode is selected, otherwise
            the block move mode is selected.
            
            In addition to the operating mode, the single byte operand includes
            fields for the source ptr, x[0], and the destination ptr, y[0].
            These pointers can be independently configured to hold (0), incre-
            ment (2), or decrement (3). Finally, the accumulator holds the len-
            gth counter. The counter is decremented and sets the ALU N and Z
            flags. 
        """
        tmp2 = self.rdPM()
        sign = self.NEGATIVE << 8
        
        movMd = (tmp2 >> 7) & 1
        srcMd =  tmp2 & 3
        dstMd = (tmp2 >> 2) & 3
        
        while(True):
            tmp1 = self.rdDM(self.x[0])
            self.wrDM(self.y[0], tmp1)
            
            if srcMd == 2:
                self.x[0] = self.addrMask & (self.x[0] + 1)
            elif srcMd == 3:
                self.x[0] = self.addrMask & (self.x[0] - 1)
            
            if dstMd == 2:
                self.y[0] = self.addrMask & (self.y[0] + 1)
            elif dstMd == 3:
                self.y[0] = self.addrMask & (self.y[0] - 1)
                
            self.a[0] = self.wordMask & (self.a[0] - 1)

            self.p &= ~(self.NEGATIVE | self.ZERO)
            if self.a[0] == 0:
                self.p |= self.ZERO
                break
            elif sign & self.a[0]:
                self.p |= self.NEGATIVE
                
            if movMd:
                break
        
    def opXMA(self, data):
        """
            This instruction exchanges the selected register with memory pointed
            to by zp,X. The addressing mode support function delivers the memory
            data to this function, which then completes the exchange with the 
            selected register, and returns to the addressing mode function the
            value in the selected register so the addressing mode function can
            complete the operation by writing the register to the addressed
            memory location.
            
            The instruction supports all of the prefix instructions. If OAX is
            used to select the X register, then the required index is provided
            by the contents of the accumulator A.
        """
        if self.oay:
            reg = self.y[0]
        elif self.oax:
            reg = self.x[0]
        else:
            reg = self.a[0]

        if self.oay:
            self.y[0] = data
        elif self.oax:
            self.x[0] = data
        else:
            self.a[0] = data
        self.FlagsNZ(data)
            
        return reg

    def opCOP(self):
        pass

#
#   instructions
#

    def inst_not_implemented(self):
        self.pc = self.addrMask & (self.pc + 1)
    instruct = [inst_not_implemented] * 256
    cycletime = [0] * 256
    extracycles = [0] * 256
    disassemble = [('???', 'imp')] * 256

    instruction = make_instruction_decorator(instruct, disassemble,
                                             cycletime, extracycles)

#
#   Column 0
#

    def inst_0x00(self):
        # pc has already been increased one
        # make copy of P
        tmp = self.p
        # put into Kernel mode for interrupts/traps
        self.p = self.byteMask &(self.MODE | self.p)
        # push 16-bit PC onto System Stack
        self.siz = True
        self.osx = False
        self.PUSH(self.pc)
        # push 8-bit P onto System Stack
        self.siz = False
        tmp = self.byteMask & (self.BREAK | tmp)
        self.PUSH(tmp)
        # M65C02A/65C02 clears decimal flag, NMOS 6502 does not
        self.p = self.byteMask & ((self.INTERRUPT | self.BREAK) | self.p)
        self.p = self.byteMask & (~self.DECIMAL & self.p)
        # read IRQ/BRK vector
        tmp1 = self.rdDM(self.IRQ)
        tmp2 = self.rdDM(self.addrMask & (self.IRQ + 1))
        vector = (tmp2 << 8) + tmp1
        # jump to vector address
        self.pc = vector
        self.clrPrefixFlags()

    @instruction(name="BPL", mode="rel", cycles=2)
    def inst_0x10(self):
        self.rel(self.opBPL)
        self.clrPrefixFlags()

    @instruction(name="JSR", mode="abs", cycles=5)
    def inst_0x20(self):
        self.opJSR()
        self.clrPrefixFlags()

    @instruction(name="BMI", mode="rel", cycles=2)
    def inst_0x30(self):
        self.rel(self.opBMI)
        self.clrPrefixFlags()

    @instruction(name="RTI", mode="imp", cycles=4)
    def inst_0x40(self):
        self.opRTI()
        self.clrPrefixFlags()

    @instruction(name="BVC", mode="rel", cycles=2)
    def inst_0x50(self):
        self.rel(self.opBVC)
        self.clrPrefixFlags()

    @instruction(name="RTS", mode="imp", cycles=3)
    def inst_0x60(self):
        self.opRTS()
        self.clrPrefixFlags()

    @instruction(name="BVS", mode="rel", cycles=2)
    def inst_0x70(self):
        self.rel(self.opBVS)
        self.clrPrefixFlags()

    @instruction(name="BRA", mode="rel", cycles=2)
    def inst_0x80(self):
        self.rel(self.opBRA)
        self.clrPrefixFlags()

    @instruction(name="BCC", mode="rel", cycles=2)
    def inst_0x90(self):
        self.rel(self.opBCC)
        self.clrPrefixFlags()

    @instruction(name="LDY", mode="imm", cycles=2)
    def inst_0xA0(self):
        self.imm(self.opLDY)
        self.clrPrefixFlags()

    @instruction(name="BCS", mode="rel", cycles=2)
    def inst_0xB0(self):
        self.rel(self.opBCS)
        self.clrPrefixFlags()

    @instruction(name="CPY", mode="imm", cycles=2)
    def inst_0xC0(self):
        self.imm(self.opCPY)
        self.clrPrefixFlags()

    @instruction(name="BNE", mode="rel", cycles=2)
    def inst_0xD0(self):
        self.rel(self.opBNE)
        self.clrPrefixFlags()

    @instruction(name="CPX", mode="imm", cycles=2)
    def inst_0xE0(self):
        self.lscx = True
        self.imm(self.opCPX)
        self.clrPrefixFlags()

    @instruction(name="BEQ", mode="rel", cycles=2)
    def inst_0xF0(self):
        self.rel(self.opBEQ)
        self.clrPrefixFlags()

#
#   Column 1
#

    @instruction(name="ORA", mode="zpXI", cycles=5)
    def inst_0x01(self):
        self.ro_zpXI(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="ORA", mode="zpIY", cycles=5)
    def inst_0x11(self):
        self.ro_zpIY(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="zpXI", cycles=5)
    def inst_0x21(self):
        self.ro_zpXI(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="zpIY", cycles=5)
    def inst_0x31(self):
        self.ro_zpIY(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="zpXI", cycles=5)
    def inst_0x41(self):
        self.ro_zpXI(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="zpIY", cycles=5)
    def inst_0x51(self):
        self.ro_zpIY(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="zpXI", cycles=5)
    def inst_0x61(self):
        self.ro_zpXI(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="zpIY", cycles=5)
    def inst_0x71(self):
        self.ro_zpIY(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="zpXI", cycles=5)
    def inst_0x81(self):
        self.wo_zpXI(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="zpIY", cycles=5)
    def inst_0x91(self):
        self.wo_zpIY(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="zpXI", cycles=5)
    def inst_0xA1(self):
        self.ro_zpXI(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="zpIY", cycles=5)
    def inst_0xB1(self):
        self.ro_zpIY(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="zpXI", cycles=5)
    def inst_0xC1(self):
        self.ro_zpXI(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="zpIY", cycles=5)
    def inst_0xD1(self):
        self.ro_zpIY(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="zpXI", cycles=5)
    def inst_0xE1(self):
        self.ro_zpXI(self.opSBC)
        elf.clrPrefixFlags()

    @instruction(name="SBC", mode="zpIY", cycles=5)
    def inst_0xF1(self):
        self.ro_zpIY(self.opSBC)
        self.clrPrefixFlags()

#
#   Column 2
#

    @instruction(name="ORA", mode="zpI", cycles=5)
    def inst_0x12(self):
        self.ro_zpI(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="zpI", cycles=5)
    def inst_0x32(self):
        self.ro_zpI(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="zpI", cycles=5)
    def inst_0x52(self):
        self.ro_zpI(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="zpI", cycles=5)
    def inst_0x72(self):
        self.ro_zpI(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="zpI", cycles=5)
    def inst_0x92(self):
        self.wo_zpI(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="LDX", mode="imm", cycles=2)
    def inst_0xA2(self):
        self.lscx = True
        self.imm(self.opLDX)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="zpI", cycles=5)
    def inst_0xB2(self):
        self.ro_zpI(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="ADJ", mode="imm", cycles=2)
    def inst_0xC2(self):
        self.imm(self.opADJ)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode='zpI', cycles=5)
    def inst_0xD2(self):
        self.ro_zpI(self.opCMP)
        self.pc = self.addrMask & (self.pc + 1)
        self.clrPrefixFlags()

    @instruction(name="PSH", mode="imm", cycles=4)
    def inst_0xE2(self):
        self.imm(self.PUSH)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="zpI", cycles=5)
    def inst_0xF2(self):
        self.ro_zpI(self.opSBC)
        self.clrPrefixFlags()

#
#   Column 3
#

    @instruction(name="ORA", mode="ipp", cycles=3)
    def inst_0x03(self):
        self.ro_ipp(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="ASL", mode="ipp", cycles=3)
    def inst_0x13(self):
        self.rmw_ipp(self.opASLm)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="ipp", cycles=3)
    def inst_0x23(self):
        self.ro_ipp(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="ipp", cycles=3)
    def inst_0x33(self):
        self.rmw_ipp(self.opROLm)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="ipp", cycles=3)
    def inst_0x43(self):
        self.ro_ipp(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="ipp", cycles=3)
    def inst_0x53(self):
        self.rmw_ipp(self.opLSRm)
        self.clrPrefixFlags()

    @instruction(name="ADD", mode="ipp", cycles=3)
    def inst_0x63(self):
        self.ro_ipp(self.opADD)
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="ipp", cycles=3)
    def inst_0x73(self):
        self.rmw_ipp(self.opRORm)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="ipp", cycles=3)
    def inst_0x83(self):
        self.wo_ipp(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="TSB", mode="ipp", cycles=3)
    def inst_0x93(self):
        self.rmw_ipp(self.opTSB)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="ipp", cycles=3)
    def inst_0xA3(self):
        self.ro_ipp(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="TRB", mode="ipp", cycles=3)
    def inst_0xB3(self):
        self.rmw_ipp(self.opTRB)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="ipp", cycles=3)
    def inst_0xC3(self):
        self.ro_ipp(self.opCMPm)
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="ipp", cycles=3)
    def inst_0xD3(self):
        self.rmw_ipp(self.opDECm)
        self.clrPrefixFlags()

    @instruction(name="SUB", mode="ipp", cycles=3)
    def inst_0xE3(self):
        self.ro_ipp(self.opSUB)
        self.clrPrefixFlags()

    @instruction(name="INC", mode="ipp", cycles=3)
    def inst_0xF3(self):
        self.rmw_ipp(self.opINCm)
        self.clrPrefixFlags()

#
#   Column 4
#

    @instruction(name="TSB", mode="zp", cycles=4)
    def inst_0x04(self):
        self.rmw_zp(self.opTSB)
        self.clrPrefixFlags()

    @instruction(name="TRB", mode="zp", cycles=4)
    def inst_0x14(self):
        self.rmw_zp(self.opTRB)
        self.clrPrefixFlags()

    @instruction(name="BIT", mode="zp", cycles=3)
    def inst_0x24(self):
        self.ro_zp(self.opBIT)
        self.clrPrefixFlags()

    @instruction(name="BIT", mode="zpX", cycles=3)
    def inst_0x34(self):
        self.ro_zpX(self.opBIT)
        self.clrPrefixFlags()

    @instruction(name="XMA", mode="zpX", cycles=4)
    def inst_0x44(self):
        self.rmw_zpX(self.opXMA)
        self.clrPrefixFlags()

    @instruction(name="MOV", mode="imm", cycles=4)
    def inst_0x54(self):
        self.opMOV()
        self.clrPrefixFlags()

    @instruction(name="STZ", mode="zp", cycles=3)
    def inst_0x64(self):
        self.wo_zp(self.opSTZ)
        self.clrPrefixFlags()

    @instruction(name="STZ", mode="zpX", cycles=3)
    def inst_0x74(self):
        self.wo_zpX(self.opSTZ)
        self.clrPrefixFlags()

    @instruction(name="STY", mode="zp", cycles=3)
    def inst_0x84(self):
        self.wo_zp(self.opSTY)
        self.clrPrefixFlags()

    @instruction(name="STY", mode="zpX", cycles=3)
    def inst_0x94(self):
        self.wo_zpX(self.opSTY)
        self.clrPrefixFlags()

    @instruction(name="LDY", mode="zp", cycles=3)
    def inst_0xA4(self):
        self.ro_zp(self.opLDY)
        self.clrPrefixFlags()

    @instruction(name="LDY", mode="zpX", cycles=3)
    def inst_0xB4(self):
        self.ro_zpX(self.opLDY)
        self.clrPrefixFlags()

    @instruction(name="CPY", mode="zp", cycles=3)
    def inst_0xC4(self):
        self.ro_zp(self.opCPY)
        self.clrPrefixFlags()

    @instruction(name="PSH", mode="zp", cycles=4)
    def inst_0xD4(self):
        self.opPSH_zp()
        self.clrPrefixFlags()

    @instruction(name="CPX", mode="zp", cycles=3)
    def inst_0xE4(self):
        self.lscx = True
        self.ro_zp(self.opCPX)
        self.clrPrefixFlags()

    @instruction(name="PUL", mode="zp", cycles=5)
    def inst_0xF4(self):
        self.opPUL_zp()
        self.clrPrefixFlags()

#
#   Column 5
#

    @instruction(name="ORA", mode="zp", cycles=3)
    def inst_0x05(self):
        self.ro_zp(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="ORA", mode="zpX", cycles=3)
    def inst_0x15(self):
        self.ro_zpX(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="zp", cycles=3)
    def inst_0x25(self):
        self.ro_zp(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="zpX", cycles=3)
    def inst_0x35(self):
        self.ro_zpX(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="zp", cycles=3)
    def inst_0x45(self):
        self.ro_zp(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="zpX", cycles=3)
    def inst_0x55(self):
        self.ro_zpX(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="zp", cycles=3)
    def inst_0x65(self):
        self.ro_zp(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="zpX", cycles=3)
    def inst_0x75(self):
        self.ro_zpX(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="zp", cycles=3)
    def inst_0x85(self):
        self.wo_zp(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="zpX", cycles=3)
    def inst_0x95(self):
        self.wo_zpX(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="zp", cycles=3)
    def inst_0xA5(self):
        self.ro_zp(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="zpX", cycles=3)
    def inst_0xB5(self):
        self.ro_zpX(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="zp", cycles=3)
    def inst_0xC5(self):
        self.ro_zp(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="zpX", cycles=3)
    def inst_0xD5(self):
        self.ro_zpX(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="zp", cycles=3)
    def inst_0xE5(self):
        self.ro_zp(self.opSBC)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="zpX", cycles=3)
    def inst_0xF5(self):
        self.ro_zpX(self.opSBC)
        self.clrPrefixFlags()

#
#   Column 6
#

    @instruction(name="ASL", mode="zp", cycles=4)
    def inst_0x06(self):
        self.rmw_zp(self.opASLm)
        self.clrPrefixFlags()

    @instruction(name="ASL", mode="zpX", cycles=4)
    def inst_0x16(self):
        self.rmw_zpX(self.opASLm)
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="zp", cycles=4)
    def inst_0x26(self):
        self.rmw_zp(self.opROLm)
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="zpX", cycles=4)
    def inst_0x36(self):
        self.rmw_zpX(self.opROLm)
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="zp", cycles=4)
    def inst_0x46(self):
        self.rmw_zp(self.opLSRm)
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="zpX", cycles=4)
    def inst_0x56(self):
        self.rmw_zpX(self.opLSRm)
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="zp", cycles=4)
    def inst_0x66(self):
        self.rmw_zp(self.opRORm)
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="zpX", cycles=4)
    def inst_0x76(self):
        self.rmw_zpX(self.opRORm)
        self.clrPrefixFlags()

    @instruction(name="STX", mode="zp", cycles=3)
    def inst_0x86(self):
        self.lscx = True
        self.wo_zp(self.opSTX)
        self.clrPrefixFlags()

    @instruction(name="STX", mode="zpY", cycles=3)
    def inst_0x96(self):
        self.lscx = True
        self.wo_zpY(self.opSTX)
        self.clrPrefixFlags()

    @instruction(name="LDX", mode="zp", cycles=3)
    def inst_0xA6(self):
        self.lscx = True
        self.ro_zp(self.opLDX)
        self.clrPrefixFlags()

    @instruction(name="LDX", mode="zpY", cycles=3)
    def inst_0xB6(self):
        self.lscx = True
        self.ro_zpY(self.opLDX)
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="zp", cycles=4)
    def inst_0xC6(self):
        self.rmw_zp(self.opDECm)
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="zpX", cycles=4)
    def inst_0xD6(self):
        self.rmw_zpX(self.opDECm)
        self.clrPrefixFlags()

    @instruction(name="INC", mode="zp", cycles=4)
    def inst_0xE6(self):
        self.rmw_zp(self.opINCm)
        self.clrPrefixFlags()

    @instruction(name="INC", mode="zpX", cycles=4)
    def inst_0xF6(self):
        self.rmw_zpX(self.opINCm)
        self.clrPrefixFlags()

#
#   Column 7
#

    @instruction(name="RMB0", mode="zp", cycles=4)
    def inst_0x07(self):
        self.bitMask = 0xFE
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB1", mode="zp", cycles=4)
    def inst_0x17(self):
        self.bitMask = 0xFD
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB2", mode="zp", cycles=4)
    def inst_0x27(self):
        self.bitMask = 0xFB
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB3", mode="zp", cycles=4)
    def inst_0x37(self):
        self.bitMask = 0xF7
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB4", mode="zp", cycles=4)
    def inst_0x47(self):
        self.bitMask = 0xEF
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB5", mode="zp", cycles=4)
    def inst_0x57(self):
        self.bitMask = 0xDF
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB6", mode="zp", cycles=4)
    def inst_0x67(self):
        self.bitMask = 0xBF
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="RMB7", mode="zp", cycles=4)
    def inst_0x77(self):
        self.bitMask = 0x7F
        self.rmw_zp(self.opRMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB0", mode="zp", cycles=4)
    def inst_0x87(self):
        self.bitMask = 0x01
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB1", mode="zp", cycles=4)
    def inst_0x97(self):
        self.bitMask = 0x02
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB2", mode="zp", cycles=4)
    def inst_0xA7(self):
        self.bitMask = 0x04
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB3", mode="zp", cycles=4)
    def inst_0xB7(self):
        self.bitMask = 0x08
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB4", mode="zp", cycles=4)
    def inst_0xc7(self):
        self.bitMask = 0x10
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB5", mode="zp", cycles=4)
    def inst_0xd7(self):
        self.bitMask = 0x20
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB6", mode="zp", cycles=4)
    def inst_0xe7(self):
        self.bitMask = 0x40
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

    @instruction(name="SMB7", mode="zp", cycles=4)
    def inst_0xf7(self):
        self.bitMask = 0x80
        self.rmw_zp(self.opSMBx)
        self.clrPrefixFlags()

#
#   Column 8
#

    @instruction(name="PHP", mode="imp", cycles=2)
    def inst_0x08(self):
        self.opPHP()
        self.clrPrefixFlags()

    @instruction(name="CLC", mode="imp", cycles=1)
    def inst_0x18(self):
        self.p = self.byteMask & (~self.CARRY & self.p)
        self.clrPrefixFlags()

    @instruction(name="PLP", mode="imp", cycles=2)
    def inst_0x28(self):
        self.opPLP()
        self.clrPrefixFlags()

    @instruction(name="SEC", mode="imp", cycles=1)
    def inst_0x38(self):
        self.p = self.byteMask & (self.CARRY | self.p)
        self.clrPrefixFlags()

    @instruction(name="PHA", mode="imp", cycles=2)
    def inst_0x48(self):
        self.opPHA()
        self.clrPrefixFlags()

    @instruction(name="CLI", mode="imp", cycles=1)
    def inst_0x58(self):
        self.p = self.byteMask & (~self.INTERRUPT & self.p)
        self.clrPrefixFlags()

    @instruction(name="PLA", mode="imp", cycles=2)
    def inst_0x68(self):
        self.opPLA()
        self.clrPrefixFlags()

    @instruction(name="SEI", mode="imp", cycles=1)
    def inst_0x78(self):
        self.p = self.byteMask & (self.INTERRUPT | self.p)
        self.clrPrefixFlags()

    @instruction(name="DEY", mode="imp", cycles=1)
    def inst_0x88(self):
        self.opDEY()
        self.clrPrefixFlags()

    @instruction(name="TYA", mode="imp", cycles=1)
    def inst_0x98(self):
        self.opTYA()
        self.clrPrefixFlags()

    @instruction(name="TAY", mode="imp", cycles=1)
    def inst_0xA8(self):
        self.opTAY()
        self.clrPrefixFlags()

    @instruction(name="CLV", mode="imp", cycles=1)
    def inst_0xB8(self):
        self.p = self.byteMask & (~self.OVERFLOW & self.p)
        self.clrPrefixFlags()

    @instruction(name="INY", mode="imp", cycles=1)
    def inst_0xC8(self):
        self.opINY()
        self.clrPrefixFlags()

    @instruction(name="CLD", mode="imp", cycles=1)
    def inst_0xD8(self):
        self.p = self.byteMask & (~self.DECIMAL & self.p)
        self.clrPrefixFlags()

    @instruction(name="INX", mode="imp", cycles=1)
    def inst_0xE8(self):
        self.opINX()
        self.clrPrefixFlags()

    @instruction(name="SED", mode="imp", cycles=1)
    def inst_0xF8(self):
        self.p = self.byteMask & (self.DECIMAL | self.p)
        self.clrPrefixFlags()

#
#   Column 9
#

    @instruction(name="ORA", mode="imm", cycles=2)
    def inst_0x09(self):
        self.imm(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="ORA", mode="absY", cycles=4)
    def inst_0x19(self):
        self.ro_absY(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="imm", cycles=2)
    def inst_0x29(self):
        self.imm(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="absY", cycles=4)
    def inst_0x39(self):
        self.ro_absY(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="imm", cycles=2)
    def inst_0x49(self):
        self.imm(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="absY", cycles=4)
    def inst_0x59(self):
        self.ro_absY(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="imm", cycles=2)
    def inst_0x69(self):
        self.imm(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="absY", cycles=4)
    def inst_0x79(self):
        self.ro_absY(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="BIT", mode="imm", cycles=2)
    def inst_0x89(self):
        self.imm(self.BTI)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="absY", cycles=5)
    def inst_0x99(self):
        self.wo_absY(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="imm", cycles=2)
    def inst_0xA9(self):
        self.imm(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="absY", cycles=4)
    def inst_0xB9(self):
        self.absY(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="imm", cycles=2)
    def inst_0xC9(self):
        self.imm(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="absY", cycles=4)
    def inst_0xD9(self):
        self.absY(self.opCMP)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="imm", cycles=2)
    def inst_0xE9(self):
        self.imm(self.opSBC)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="absY", cycles=4)
    def inst_0xF9(self):
        self.absY(self.opSBC)
        self.clrPrefixFlags()

#
#   Column A
#

    @instruction(name="ASL", mode="acc", cycles=1)
    def inst_0x0A(self):
        self.opASLr()
        self.clrPrefixFlags()

    @instruction(name="INC", mode="acc", cycles=1)
    def inst_0x1A(self):
        self.opINC()
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="acc", cycles=1)
    def inst_0x2A(self):
        self.opROLr()
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="acc", cycles=1)
    def inst_0x3A(self):
        self.opDEC()
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="acc", cycles=1)
    def inst_0x4A(self):
        self.opLSRr()
        self.clrPrefixFlags()

    @instruction(name="PHY", mode="imp", cycles=2)
    def inst_0x5A(self):
        self.opPHY()
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="acc", cycles=1)
    def inst_0x6A(self):
        self.opRORr()
        self.clrPrefixFlags()

    @instruction(name="PLY", mode="imp", cycles=2)
    def inst_0x7A(self):
        self.opPLY()
        self.clrPrefixFlags()

    @instruction(name="TXA", mode="imp", cycles=1)
    def inst_0x8A(self):
        self.opTXA()
        self.clrPrefixFlags()

    @instruction(name="TXS", mode="imp", cycles=1)
    def inst_0x9A(self):
        self.opTXS()
        self.clrPrefixFlags()

    @instruction(name="TAX", mode="imp", cycles=1)
    def inst_0xAA(self):
        self.opTAX()
        self.clrPrefixFlags()

    @instruction(name="TSX", mode="imp", cycles=1)
    def inst_0xBA(self):
        self.opTSX()
        self.clrPrefixFlags()

    @instruction(name="DEX", mode="imp", cycles=1)
    def inst_0xCA(self):
        self.opDEX()
        self.clrPrefixFlags()

    @instruction(name="PHX", mode="imp", cycles=2)
    def inst_0xDA(self):
        self.opPHX()
        self.clrPrefixFlags()

    @instruction(name="NOP", mode="imp", cycles=1)
    def inst_0xEA(self):
        self.clrPrefixFlags()

    @instruction(name="PLX", mode="imp", cycles=2)
    def inst_0xFA(self):
        self.opPLX()
        self.clrPrefixFlags()

#
#   Column B
#

    @instruction(name="DUP", mode="acc", cycles=1)
    def inst_0x0B(self):
        self.opDUP()
        self.clrPrefixFlags()

    @instruction(name="SWP", mode="imp", cycles=1)
    def inst_0x1B(self):
        self.opSWP()
        self.clrPrefixFlags()

    @instruction(name="ROT", mode="imp", cycles=1)
    def inst_0x2B(self):
        self.opROT()
        self.clrPrefixFlags()

    @instruction(name="NXT", mode="imp", cycles=3)
    def inst_0x3B(self):
        self.opNXT()
        self.clrPrefixFlags()

    @instruction(name="PHI", mode="imp", cycles=3)
    def inst_0x4B(self):
        self.opPHI()
        self.clrPrefixFlags()

    @instruction(name="INI", mode="imp", cycles=1)
    def inst_0x5B(self):
        self.opINI()
        self.clrPrefixFlags()

    @instruction(name="PLI", mode="imp", cycles=3)
    def inst_0x6B(self):
        self.opPLI()
        self.clrPrefixFlags()

    @instruction(name="ENT", mode="imp", cycles=5)
    def inst_0x7B(self):
        self.opENT()
        self.clrPrefixFlags()

    @instruction(name="OSX", mode="imp", cycles=1)
    def inst_0x8B(self):
        self.osx = True
        self.oax = False

    @instruction(name="IND", mode="imp", cycles=1)
    def inst_0x9B(self):
        self.ind = True

    @instruction(name="SIZ", mode="imp", cycles=1)
    def inst_0xAB(self):
        self.siz = True

    @instruction(name="ISZ", mode="imp", cycles=1)
    def inst_0xBB(self):
        self.ind = True
        self.siz = True

    @instruction(name="OSZ", mode="imp", cycles=1)
    def inst_0xCB(self):
        self.osx = True
        self.oax = False
        self.siz = True

    @instruction(name="OIS", mode="imp", cycles=1)
    def inst_0xDB(self):
        self.osx = True
        self.oax = False
        self.ind = True
        self.siz = True

    @instruction(name="OAX", mode="imp", cycles=1)
    def inst_0xEB(self):
        self.oax = True
        self.osx = False
        self.oay = False

    @instruction(name="OAY", mode="imp", cycles=1)
    def inst_0xFB(self):
        self.oay = True
        self.oax = False

#
#   Column C
#

    @instruction(name="TSB", mode="abs", cycles=5)
    def inst_0x0C(self):
        self.rmw_abs(self.opTSB)
        self.clrPrefixFlags()

    @instruction(name="TRB", mode="abs", cycles=5)
    def inst_0x1C(self):
        self.rmw_abs(self.opTRB)
        self.clrPrefixFlags()

    @instruction(name="BIT", mode="abs", cycles=4)
    def inst_0x2C(self):
        self.ro_abs(self.opBIT)
        self.clrPrefixFlags()

    @instruction(name="BIT", mode="absX", cycles=4)
    def inst_0x3C(self):
        self.ro_absX(self.opBIT)
        self.clrPrefixFlags()

    @instruction(name="JMP", mode="abs", cycles=3)
    def inst_0x4C(self):
        _, self.pc = self.abs()
        self.clrPrefixFlags()

    @instruction(name="PHR", mode="rel16", cycles=6)
    def inst_0x5C(self):
        self.rel16(self.opPHR)
        self.clrPrefixFlags()

    @instruction(name="JMP", mode="absI", cycles=5)
    def inst_0x6C(self):
        _, self.pc = self.absI()
        self.clrPrefixFlags()

    @instruction(name="JMP", mode="absXI", cycles=6)
    def inst_0x7C(self):
        _, self.pc = self.absXI()
        self.clrPrefixFlags()

    @instruction(name="STY", mode="abs", cycles=4)
    def inst_0x8C(self):
        self.wo_abs(self.opSTY)
        self.clrPrefixFlags()

    @instruction(name="STZ", mode="abs", cycles=4)
    def inst_0x9C(self):
        self.wo_abs(self.opSTZ)
        self.clrPrefixFlags()

    @instruction(name="LDY", mode="abs", cycles=4)
    def inst_0xAC(self):
        self.ro_abs(self.opLDY)
        self.clrPrefixFlags()

    @instruction(name="LDY", mode="absX", cycles=4)
    def inst_0xBC(self):
        self.ro_absX(self.opLDY)
        self.clrPrefixFlags()

    @instruction(name="CPY", mode="abs", cycles=4)
    def inst_0xCC(self):
        self.abs(self.opCPY)
        self.clrPrefixFlags()

    @instruction(name="PSH", mode="abs", cycles=5)
    def inst_0xDC(self):
        self.opPSH_abs()
        self.clrPrefixFlags()

    @instruction(name="CPX", mode="abs", cycles=4)
    def inst_0xEC(self):
        self.lscx = True
        self.ro_abs(self.opCPX)
        self.clrPrefixFlags()

    @instruction(name="PUL", mode="abs", cycles=6)
    def inst_0xFC(self):
        self.opPUL_abs()
        self.clrPrefixFlags()

#
#   Column D
#

    @instruction(name="ORA", mode="abs", cycles=4)
    def inst_0x0D(self):
        self.ro_abs(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="ORA", mode="absX", cycles=4)
    def inst_0x1D(self):
        self.ro_absX(self.opORA)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="abs", cycles=4)
    def inst_0x2D(self):
        self.abs(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="AND", mode="absX", cycles=4)
    def inst_0x3D(self):
        self.ro_absX(self.opAND)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="abs", cycles=4)
    def inst_0x4D(self):
        self.ro_abs(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="EOR", mode="absX", cycles=4)
    def inst_0x5D(self):
        self.ro_absX(self.opEOR)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="abs", cycles=4)
    def inst_0x6D(self):
        self.ro_abs(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="ADC", mode="absX", cycles=4)
    def inst_0x7D(self):
        self.ro_absX(self.opADC)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="abs", cycles=4)
    def inst_0x8D(self):
        self.wo_abs(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="STA", mode="absX", cycles=4)
    def inst_0x9D(self):
        self.wo_absX(self.opSTA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="abs", cycles=4)
    def inst_0xAD(self):
        self.ro_abs(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="LDA", mode="absX", cycles=4)
    def inst_0xBD(self):
        self.ro_absX(self.opLDA)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="abs", cycles=4)
    def inst_0xCD(self):
        self.ro_abs(self.opCMPR, self.a)
        self.clrPrefixFlags()

    @instruction(name="CMP", mode="absX", cycles=4)
    def inst_0xDD(self):
        self.ro_absX(self.opCMPR, self.a)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="abs", cycles=4)
    def inst_0xED(self):
        self.ro_abs(self.opSBC)
        self.clrPrefixFlags()

    @instruction(name="SBC", mode="absX", cycles=4)
    def inst_0xFD(self):
        self.absX(self.opSBC)
        self.clrPrefixFlags()

#
#   Column E
#

    @instruction(name="ASL", mode="abs", cycles=5)
    def inst_0x0E(self):
        self.rmw_abs(self.opASLm)
        self.clrPrefixFlags()

    @instruction(name="ASL", mode="absX", cycles=5)
    def inst_0x1E(self):
        self.rmw_absX(self.opASLm)
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="abs", cycles=5)
    def inst_0x2E(self):
        self.rmw_abs(self.opROLm)
        self.clrPrefixFlags()

    @instruction(name="ROL", mode="absX", cycles=5)
    def inst_0x3E(self):
        self.rmw_absX(self.opROLm)
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="abs", cycles=5)
    def inst_0x4E(self):
        self.rmw_abs(self.opLSRm)
        self.clrPrefixFlags()

    @instruction(name="LSR", mode="absX", cycles=5)
    def inst_0x5E(self):
        self.rmw_absX(self.opLSRm)
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="abs", cycles=5)
    def inst_0x6E(self):
        self.rmw_abs(self.opRORm)
        self.clrPrefixFlags()

    @instruction(name="ROR", mode="absX", cycles=5)
    def inst_0x7E(self):
        self.rmw_absX(self.opRORm)
        self.clrPrefixFlags()

    @instruction(name="STX", mode="abs", cycles=5)
    def inst_0x8E(self):
        self.lscx = True
        self.wo_abs(self.opSTX)
        self.clrPrefixFlags()

    @instruction(name="STZ", mode="absX", cycles=4)
    def inst_0x9E(self):
        self.wo_absX(self.opSTZ)
        self.clrPrefixFlags()

    @instruction(name="LDX", mode="abs", cycles=4)
    def inst_0xAE(self):
        self.lscx = True
        self.ro_abs(self.opLDX)
        self.clrPrefixFlags()

    @instruction(name="LDX", mode="absY", cycles=4)
    def inst_0xBE(self):
        self.lscx = True
        self.ro_absY(self.opLDX)
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="abs", cycles=5)
    def inst_0xCE(self):
        self.rmw_abs(self.opDECR)
        self.clrPrefixFlags()

    @instruction(name="DEC", mode="absX", cycles=5)
    def inst_0xDE(self):
        self.rmw_absX(self.opDECR)
        self.clrPrefixFlags()

    @instruction(name="INC", mode="abs", cycles=5)
    def inst_0xEE(self):
        self.rmw_abs(self.opINCR)
        self.clrPrefixFlags()

    @instruction(name="INC", mode="absX", cycles=5)
    def inst_0xFE(self):
        self.absX(self.opINCR)
        self.clrPrefixFlags()

#
#   Column F
#

    @instruction(name="BBR0", mode="zprel", cycles=5)
    def inst_0x0F(self):
        self.bitMask = 0xFE
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR1", mode="zprel", cycles=5)
    def inst_0x1F(self):
        self.bitMask = 0xFD
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR2", mode="zprel", cycles=5)
    def inst_0x2F(self):
        self.bitMask = 0xFB
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR3", mode="zprel", cycles=5)
    def inst_0x3F(self):
        self.bitMask = 0xF7
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR4", mode="zprel", cycles=5)
    def inst_0x4F(self):
        self.bitMask = 0xEF
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR5", mode="zprel", cycles=5)
    def inst_0x5F(self):
        self.bitMask = 0xDF
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR6", mode="zprel", cycles=5)
    def inst_0x6F(self):
        self.bitMask = 0xBF
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBR7", mode="zprel", cycles=5)
    def inst_0x7F(self):
        self.bitMask = 0xEF
        self.zprel(self.opBBRx)
        self.clrPrefixFlags()

    @instruction(name="BBS0", mode="zprel", cycles=5)
    def inst_0x8F(self):
        self.bitMask = 0x01
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS1", mode="zprel", cycles=5)
    def inst_0x9F(self):
        self.bitMask = 0x02
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS2", mode="zprel", cycles=5)
    def inst_0xAF(self):
        self.bitMask = 0x04
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS3", mode="zprel", cycles=5)
    def inst_0xBF(self):
        self.bitMask = 0x08
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS4", mode="zprel", cycles=5)
    def inst_0xCF(self):
        self.bitMask = 0x10
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS5", mode="zprel", cycles=5)
    def inst_0xDF(self):
        self.bitMask = 0x20
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS6", mode="zprel", cycles=5)
    def inst_0xEF(self):
        self.bitMask = 0x40
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()

    @instruction(name="BBS7", mode="zprel", cycles=5)
    def inst_0xFF(self):
        self.bitMask = 0x80
        self.zprel(self.opBBSx)
        self.clrPrefixFlags()
