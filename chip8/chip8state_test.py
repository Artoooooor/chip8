import unittest
from chip8.chip8state import Chip8State


STANDARD_FONT = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,
    0x20, 0x60, 0x20, 0x20, 0x70,
    0xF0, 0x10, 0xF0, 0x80, 0xF0,
    0xF0, 0x10, 0xF0, 0x10, 0xF0,
    0x90, 0x90, 0xF0, 0x10, 0x10,
    0xF0, 0x80, 0xF0, 0x10, 0xF0,
    0xF0, 0x80, 0xF0, 0x90, 0xF0,
    0xF0, 0x10, 0x20, 0x40, 0x40,
    0xF0, 0x90, 0xF0, 0x90, 0xF0,
    0xF0, 0x90, 0xF0, 0x10, 0xF0,
    0xF0, 0x90, 0xF0, 0x90, 0x90,
    0xE0, 0x90, 0xE0, 0x90, 0xE0,
    0xF0, 0x80, 0x80, 0x80, 0xF0,
    0xE0, 0x90, 0x90, 0x90, 0xE0,
    0xF0, 0x80, 0xF0, 0x80, 0xF0,
    0xF0, 0x80, 0xF0, 0x80, 0x80]


class StateTest(unittest.TestCase):
    def test_load_program_loads_array_to_0x200(self):
        state = Chip8State()
        state.load_program([0x01, 0x02, 0x03, 0x04])
        for i, value in enumerate([0x01, 0x02, 0x03, 0x04]):
            self.assertEqual(value, state.memory[0x200 + i])

    def test_load_program_clears_memory_from_0x200_to_end(self):
        state = Chip8State()
        state.memory[:] = [0xff] * len(state.memory)
        state.load_program([0x01, 0x02, 0x03, 0x04])
        for i in range(0x204, len(state.memory)):
            self.assertEqual(0x00, state.memory[i])

    def test_load_font_load_them_into_0x00(self):
        state = Chip8State()
        state.load_font([i for i in range(0x50)])
        for i in range(0x50):
            self.assertEqual(i, state.memory[i])

    def test_default_font_is_standard(self):
        state = Chip8State()
        self.assertArray(state.memory, STANDARD_FONT)

    def test_reset_clears_state(self):
        state = Chip8State()
        state.registers = [i for i in range(0x10)]
        state.memory = [i & 0xff for i in range(len(state.memory))]
        state.DT = 1
        state.ST = 2
        state.I = 234
        state.PC = 456
        state.SP = 4
        state.stack = [i for i in range(len(state.stack))]
        state.reset()
        self.assertZeros(state.registers)
        self.assertZeros(state.memory[5 * 16:])
        self.assertEqual(0x1000, len(state.memory))
        self.assertEqual(0, state.DT)
        self.assertEqual(0, state.ST)
        self.assertEqual(0, state.I)
        self.assertEqual(0x200, state.PC)
        self.assertEqual(0, state.SP)
        self.assertZeros(state.stack)
        self.assertArray(state.memory, STANDARD_FONT)

    def assertZeros(self, array):
        for value in array:
            self.assertEqual(0, value)

    def assertArray(self, actual, expected):
        for i, value in enumerate(expected):
            self.assertEqual(value, actual[i])


if __name__ == '__main__':
    unittest.main()
