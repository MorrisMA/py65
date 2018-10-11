import re
from utils.addressing import AddressParser


class Assembler:
    Statement = re.compile(r'^([A-z]{3}[0-7]?\s+'
                           r'\(?\s*)([^,\s\)]+)(\s*[,xXyYiI\s]*\)?'
                           r'[,xXyYiI\s]*|\s*,\s*[^,\s\)]+)$')

    Addressing = (
        ('zp',    "$00FF"),
        ('zpX',   "$00FF,X"),
        ('zpY',   "$00FF,Y"),
        ('zpI',   "($00FF)"),
        ('zpXI',  "($00FF,X)"),
        ('zpIY',  "($00FF),Y"),
        ('abs',   "$FFFF"),
        ('absX',  "$FFFF,X"),
        ('absY',  "$FFFF,Y"),
        ('absI',  "($FFFF)"),
        ('absXI', "($FFFF,X)"),
        ('rel',   "$FFFF"),
        ('imp',   ""),
        ('acc',   ""),
        ('acc',   "A"),
        ('imm',   "#$FF"),
<<<<<<< HEAD
=======
        ('imm',   "#$0FFF"),
>>>>>>> 6b9803d6b558e09e4c37f2cfa2bb949253ef7c10
        ('imm',   "#$FFFF"),
        ('rel16', "$FFFF"),
        ('ipp',   "$FF,I"),
        ('zprel', "$00FF,$FFFF"),
    )

    def __init__(self, mpu, address_parser=None):
        """ If a configured AddressParser is passed, symbolic addresses
        may be used in the assembly statements.
        """
        self._mpu = mpu

        if address_parser is None:
            address_parser = AddressParser()
        self._address_parser = address_parser

        self._addressing = []
        numchars = mpu.BYTE_WIDTH / 4  # 1 byte = 2 chars in hex
        for mode, format in self.Addressing:
            pat = "^" + re.escape(format) + "$"
            pat = pat.replace('00', '0{%d}' % numchars)
            pat = pat.replace('0F', '([0-9A-F]{%d})' % 1)
            pat = pat.replace('FF', '([0-9A-F]{%d})' % numchars)
            self._addressing.append([mode, re.compile(pat)])

    def assemble(self, statement, pc=0000):
        """ Assemble the given assembly language statement.  If the statement
        uses relative addressing, the program counter (pc) must also be given.
        The result is a list of bytes.  Raises SyntaxError when assembly fails.
        """
        opcode, operand = self.normalize_and_split(statement)
<<<<<<< HEAD
        print(' --- assemble: ', opcode, operand)

=======
        
>>>>>>> 6b9803d6b558e09e4c37f2cfa2bb949253ef7c10
        for mode, pattern in self._addressing:
            match = pattern.match(operand)
            print(' ---- assemble: ', opcode, operand, pattern, match)
            if match:
                # check if opcode supports this addressing mode
                try:
                    print(' ---- assemble: ', opcode, mode)
                    bytes = [self._mpu.disassemble.index((opcode, mode))]
                except ValueError:
                    continue

                operands = match.groups()

                if mode == 'rel':
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 2
                    relative = relative & self._mpu.byteMask
                    operands = [(self._mpu.BYTE_FORMAT % relative)]

                elif mode == 'rel16':
                   # relative branch
                   absolute = int(''.join(operands), 16)
                   relative = (absolute - pc) - 3
                   relative = relative & self._mpu.wordMask
                   operands = [(self._mpu.WORD_FORMAT % relative)]
                   operands = [operands[0][2:], operands[0][:2]]
                    
                elif len(operands) == 2:
                    # swap bytes
                    operands = (operands[1], operands[0])
                
                operands = [int(hex, 16) for hex in operands]
                bytes.extend(operands)

                # raise if the assembled bytes would exceed top of memory
                if (pc + len(bytes)) > (2 ** self._mpu.ADDR_WIDTH):
                    raise OverflowError

                return bytes

        # assembly failed
        raise SyntaxError(statement)

    def normalize_and_split(self, statement):
        """ Given an assembly language statement like "lda $c12,x", normalize
            the statement by uppercasing it, removing unnecessary whitespace,
            and parsing the address part using AddressParser.  The result of
            the normalization is a tuple of two strings (opcode, operand).
        """
        statement = ' '.join(str.split(statement))
        # normalize target in operand
        match = self.Statement.match(statement)
        if match:
            before, target, after = match.groups()
            # target is an immediate value
            if target.startswith('#'):
                try:
                    if target[1] in ("'", '"'): # quoted ascii character
                        number = ord(target[2])
                    else:
                        number = self._address_parser.number(target[1:])
                except IndexError:
                    raise SyntaxError(statement)

                # if (number < 0) or (number > self._mpu.byteMask):
                if (number < 0) or (number > self._mpu.wordMask):
                    raise OverflowError
                statement = before + '#$' + self._mpu.BYTE_FORMAT % number

            # target is the accumulator
            elif target in ('a', 'A'):
                pass

            # target is an address or label
            else:
                address = self._address_parser.number(target)
                statement = before + '$' + self._mpu.ADDR_FORMAT % address + after

        # separate opcode and operand
        splitted = statement.split(" ", 2)
        opcode = splitted[0].strip().upper()
        if len(splitted) > 1:
            operand = splitted[1].strip().upper()
        else:
            operand = ''
        return (opcode, operand)
