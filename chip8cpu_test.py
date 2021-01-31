import unittest

from chip8cpu import Chip8Cpu, Chip8State

class CpuTest(unittest.TestCase):

    def setUp(self):
        self.state = Chip8State()
        self.cpu = Chip8Cpu(self.state)
        

    def test_00e0_clears_screen(self):
        self.when_instruction_is(0x200,0x00e0)
        self.when_memory_is_ones(0x1000 - 0x100, 256)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)
        self.assert_zeros(0x1000 - 0x100, 256)

    def test_00ee_pops_stack_to_pc_and_increments_by_2(self):
        self.when_stack_is(0x300)
        self.when_instruction_is(0x200,0xee)
        self.cpu.tick()
        self.assertEqual(0x302, self.state.PC)
        self.assertEqual(0x00, self.state.SP)

    def test_0nnn_except_00ee_and_00e0_is_ignored(self):
        for i in range(0x000,0x1000):
            if i != 0x00ee and i != 0x00e0:
                self.when_stack_is(0x2)
                self.when_instruction_is(0x200,i)
                self.when_pc_is(0x200)
                self.when_memory_is_ones(0x1000 - 0x100, 256)
                self.cpu.tick()
                self.assertEqual(0x202,self.state.PC)
                self.assert_ones(0x1000 - 0x100, 256)

    def test_1ABC_jumps_to_ABC(self):
        self.when_instruction_is(0x200,0x1ABC)
        self.cpu.tick()
        self.assertEqual(0xABC, self.state.PC)

    def test_2ABC_pushes_PC_and_jumps_to_ABC(self):
        self.when_instruction_is(0x200,0x2ABC)
        self.cpu.tick()
        self.assertEqual(0xABC, self.state.PC)
        self.assert_stack(0x200)

    def test_3ABC_skips_instruction_if_rA_contains_BC(self):
        self.when_instruction_is(0x200,0x3ABC)
        self.when_register_is(0xA,0xBC)
        self.cpu.tick()
        self.assertEqual(0x204,self.state.PC)

    def test_3ABC_does_not_skip_instruction_if_rA_contains_BB(self):
        self.when_instruction_is(0x200,0x3ABC)
        self.when_register_is(0xA,0xBB)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)

    def test_4ABC_does_not_skip_instruction_if_rA_contains_BC(self):
        self.when_instruction_is(0x200,0x4ABC)
        self.when_register_is(0xA,0xBC)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)

    def test_4ABC_skips_instruction_if_rA_contains_BB(self):
        self.when_instruction_is(0x200,0x4ABC)
        self.when_register_is(0xA,0xBB)
        self.cpu.tick()
        self.assertEqual(0x204,self.state.PC)

    def test_5AB0_skips_instruction_if_rA_equals_rB(self):
        self.when_instruction_is(0x200,0x5AB0)
        self.when_register_is(0xA,0x12)
        self.when_register_is(0xB,0x12)
        self.cpu.tick()
        self.assertEqual(0x204,self.state.PC)

    def test_5AB0_does_not_skip_instruction_if_rA_differs_rB(self):
        self.when_instruction_is(0x200,0x5AB0)
        self.when_register_is(0xA,0x12)
        self.when_register_is(0xB,0x13)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)

    def test_5AB1_is_ignored(self):
        self.when_instruction_is(0x200,0x5AB1)
        self.when_register_is(0xA,0x12)
        self.when_register_is(0xB,0x12)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)

    def test_6C17_stores_17_in_rC(self):
        self.when_instruction_is(0x200,0x6C17)
        self.cpu.tick()
        self.assertEqual(0x17,self.state.registers[0xC])

    def test_7C17_adds_17_to_rC(self):
        self.when_instruction_is(0x200,0x7C17)
        self.when_register_is(0xC,0x10)
        self.cpu.tick()
        self.assertEqual(0x27,self.state.registers[0xC])
        

    def when_instruction_is(self, address, instruction):
        self.state.memory[address+1]=instruction & 0xff;
        self.state.memory[address]=(instruction >> 8) & 0xff;

    def when_memory_is_ones(self, start, length):
        self.state.memory[start:start+length] = [0x01] * length

    def when_stack_is(self, *numbers):
        for i,element in enumerate(numbers):
            self.state.stack[i]=element
        self.state.SP=len(numbers)

    def when_pc_is(self, pc):
        self.state.PC = pc

    def when_register_is(self,register,value):
        self.state.registers[register]=value

    def assert_zeros(self, start, length):
        for b in self.state.memory[start:start+length]:
            self.assertEqual(b,0)

    def assert_ones(self, start, length):
        for b in self.state.memory[start:start+length]:
            self.assertEqual(b,1)

    def assert_stack(self, *expected):
        for i,element in enumerate(expected):
            self.assertEqual(self.state.stack[i],element)
        self.assertEqual(self.state.SP,len(expected))

if __name__ == '__main__':
    unittest.main()