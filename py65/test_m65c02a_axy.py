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


class MonitorTests(unittest.TestCase):

    # assemble

    def test_do_assemble_assembles_valid_statement(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 lda #$ab')

        mpu = mon._mpu
        self.assertEqual(0xA9, mpu.memory[0xC000])
        self.assertEqual(0xAB, mpu.memory[0xC001])

    def test_do_assemble_outputs_disassembly(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 lda #$ab')

        out = stdout.getvalue()
        self.assertEqual("$C000  A9 AB     LDA #$AB\n", out)

    def test_do_assemble_parses_start_address_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_add_label('c000 base')
        mon.do_assemble('base rts')

        mpu = mon._mpu
        self.assertEqual(0x60, mpu.memory[0xC000])

    def test_do_assemble_passes_addr_for_relative_branch_calc(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('4000 bvs $4005')

        out = stdout.getvalue()
        self.assertEqual("$4000  70 03     BVS $4005\n", out)

     # disassemble

    def test_disassemble_shows_help_when_given_extra_args(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_disassemble("c000 c001")
        out = stdout.getvalue()
        self.assertTrue(out.startswith('disassemble <address_range>'))

    def test_disassemble_will_disassemble_one_address(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0xEA  # => NOP
        mon._mpu.step()
        mon.do_disassemble("c000")

        out = stdout.getvalue()
        disasm = "$C000  EA        NOP\n"
        self.assertEqual(out, disasm)

    def test_disassemble_will_disassemble_an_address_range(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0xEA  # => NOP
        mon._mpu.memory[0xc001] = 0xEA  # => NOP
        mon._mpu.step()
        mon.do_disassemble("c000:c001")

        out = stdout.getvalue()
        disasm = "$C000  EA        NOP\n$C001  EA        NOP\n"
        self.assertEqual(out, disasm)

    def test_disassemble_wraps_an_instruction_around_memory(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xffff] = 0x20  # => JSR
        mon._mpu.memory[0x0000] = 0xD2  #
        mon._mpu.memory[0x0001] = 0xFF  # => $FFD2
        mon.do_disassemble("ffff")

        out = stdout.getvalue()
        disasm = "$FFFF  20 D2 FF  JSR $FFD2\n"
        self.assertEqual(out, disasm)

    # fill

    def test_do_fill_will_fill_one_address(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon.do_fill('c000 aa')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +1 bytes from $C000 to $C000'))

    def test_do_fill_will_fill_an_address_range_with_a_single_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon._mpu.memory[0xc001] = 0x00
        mon._mpu.memory[0xc002] = 0x00
        mon.do_fill('c000:c001 aa')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        self.assertEqual(0xAA, mon._mpu.memory[0xc001])
        self.assertEqual(0x00, mon._mpu.memory[0xc002])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +2 bytes from $C000 to $C001'))

    def test_do_fill_will_fill_an_address_range_with_byte_sequence(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon._mpu.memory[0xc001] = 0x00
        mon._mpu.memory[0xc002] = 0x00
        mon._mpu.memory[0xc003] = 0x00
        mon.do_fill('c000:c003 aa bb')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        self.assertEqual(0xBB, mon._mpu.memory[0xc001])
        self.assertEqual(0xAA, mon._mpu.memory[0xc002])
        self.assertEqual(0xBB, mon._mpu.memory[0xc003])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +4 bytes from $C000 to $C003'))

    def test_do_fill_bad_label_in_address_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_fill('nonexistent 0')

        out = stdout.getvalue()
        self.assertTrue(out.startswith("Label not found: nonexistent"))

    def test_do_fill_bad_label_in_value_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_fill('0 nonexistent')

        out = stdout.getvalue()
        self.assertTrue(out.startswith("Label not found: nonexistent"))

    # goto

    def test_goto_with_breakpoints_stops_execution_at_breakpoint(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._breakpoints = [ 0x03 ]
        mon._mpu.memory = [ 0xEA, 0xEA, 0xEA, 0xEA ]
        mon.do_goto('0')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Breakpoint 0 reached"))
        self.assertEqual(0x03, mon._mpu.pc)

    def test_goto_with_breakpoints_stops_execution_at_brk(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._breakpoints = [ 0x02 ]
        mon._mpu.memory = [ 0xEA, 0xEA, 0x00, 0xEA ]
        mon.do_goto('0')
        self.assertEqual(0x02, mon._mpu.pc)

    def test_goto_without_breakpoints_stops_execution_at_brk(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._breakpoints = []
        mon._mpu.memory = [ 0xEA, 0xEA, 0x00, 0xEA ]
        mon.do_goto('0')
        self.assertEqual(0x02, mon._mpu.pc)

    # load

    def test_load(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)

        filename = tempfile.mktemp()
        try:
            f = open(filename, 'wb')
            f.write(b'\xaa\xbb\xcc')
            f.close()

            mon.do_load("'%s' a600" % filename)
            self.assertEqual('Wrote +3 bytes from $A600 to $A602\n',
                             stdout.getvalue())
            self.assertEqual([0xAA, 0xBB, 0xCC],
                             mon._mpu.memory[0xA600:0xA603])
        finally:
            os.unlink(filename)

    # registers

    def test_registers_updates_single_register(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('x=42')
        out = stdout.getvalue()
        self.assertEqual("", out)
        self.assertEqual(0x42, mon._mpu.x[0])

    def test_registers_updates_all_registers(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('a=42, x=43, y=44, p=45, sp=46, pc=4600')
        out = stdout.getvalue()
        self.assertEqual("", out)
        self.assertEqual(0x42, mon._mpu.a[0])
        self.assertEqual(0x43, mon._mpu.x[0])
        self.assertEqual(0x44, mon._mpu.y[0])
        self.assertEqual(0x45, mon._mpu.p)
        self.assertEqual(0x46, mon._mpu.sp[0])
        self.assertEqual(0x4600, mon._mpu.pc)

    # save

    def test_save(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0:3] = [0xAA, 0xBB, 0xCC]

        filename = tempfile.mktemp()
        try:
            mon.do_save("'%s' 0 2" % filename)
            self.assertEqual('Saved +3 bytes to %s\n' % filename,
                             stdout.getvalue())

            f = open(filename, 'rb')
            contents = f.read()
            f.close()
            self.assertEqual(b'\xaa\xbb\xcc', contents)
        finally:
            os.unlink(filename)

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
