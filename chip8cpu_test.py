import unittest

from chip8cpu import Chip8Cpu, Chip8State

class CpuTest(unittest.TestCase):

    def setUp(self):
        self.state = Chip8State()
        self.cpu = Chip8Cpu(self.state)
        

    def test_00e0_clears_screen(self):
        self.when_instruction_is(0x200,0x00e8)
        self.when_memory_is_ones(0x1000 - 0x100, 256)
        self.cpu.tick()
        self.assertEqual(0x202,self.state.PC)
        self.assert_zeros(0x1000 - 0x100, 256)

    

    def when_instruction_is(self, address, instruction):
        self.state.memory[address]=instruction & 0xff;
        self.state.memory[address+1]=(instruction >> 8) & 0xff;

    def when_memory_is_ones(self, start, length):
        for i in range(length):
            self.state.memory[start + i] = 0x01

    def assert_zeros(self, start, length):
        for i in range(length):
            self.assertEqual(self.state.memory[start + i],0,'Zero on {}'.format(start + i))



if __name__ == '__main__':
    unittest.main()