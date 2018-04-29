from py65.utils.addressing import AddressParser


class Disassembler:
    def __init__(self, mpu, address_parser=None):
        if address_parser is None:
            address_parser = AddressParser()

        self._mpu = mpu
        self._address_parser = address_parser

        self.addrWidth = mpu.ADDR_WIDTH
        self.byteWidth = mpu.BYTE_WIDTH
        if mpu.BYTE_WIDTH == 8:
            self.wordWidth = 16
        else:
            self.wordWidth = 32
        self.addrFmt = mpu.ADDR_FORMAT
        self.byteFmt = mpu.BYTE_FORMAT
        if mpu.BYTE_WIDTH == 8:
            self.wordFmt = '%04X'
        else:
            self.wordFmt = '%08X'
        self.addrMask = (1 << self.addrWidth) - 1
        self.byteMask = (1 << self.byteWidth) - 1
        self.wordMask = (1 << self.wordWidth) - 1

    def instruction_at(self, pc):
        """ Disassemble the instruction at PC and return a tuple
        containing (instruction byte count, human readable text)
        """

        instruction = self._mpu.rdDM(pc)
        disasm, addressing = self._mpu.disassemble[instruction]

        if addressing == 'acc':
            disasm += ' A'
            length = 1

        elif addressing == 'imp':
            length = 1

        elif addressing == 'imm':
            byte = self._mpu.rdDM(pc + 1)
            disasm += ' #$' + self.byteFmt % byte
            length = 2

        elif addressing == 'zp':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpX':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing == 'zpY':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2

        elif addressing == 'zpI':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '($' + self.byteFmt % zp_address + ')')
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpIY':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'zpXI':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'abs':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing == 'absX':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s,X' % address_or_label
            length = 3

        elif addressing == 'absY':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' %s,Y' % address_or_label
            length = 3

        elif addressing == 'absI':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'absXI':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(
                address, '$' + self.addrFmt % address)
            disasm += ' (%s,X)' % address_or_label
            length = 3

        elif addressing == 'rel':
            opv = self._mpu.rdDM(pc + 1)
            targ = pc + 2
            if opv & (1 << (self.byteWidth - 1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'zprel':
            print(' --- zprel: ', end='')
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s' % address_or_label
            
            opv = self._mpu.rdDM(pc + 2)
            targ = pc + 3
            if opv & (1 << (self.byteWidth - 1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ',' + address_or_label

            length = 3

        elif addressing == 'rel16':
            opv = self._mpu.WordAt(pc + 1)
            targ = pc + 3
            if opv & (1 << (self.wordWidth - 1)):
                targ -= (opv ^ self.wordMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(
                targ, '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 3
            
        elif addressing == 'ipp':
            zp_address = self._mpu.rdDM(pc + 1)
            address_or_label = self._address_parser.label_for(
                zp_address, '$' + self.byteFmt % zp_address)
            disasm += ' %s,I' % address_or_label
            length = 2

        return (length, disasm)
