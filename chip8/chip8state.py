CHIP8_STANDARD_FONT = [
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
    0xF0, 0x80, 0xF0, 0x80, 0x80
]


class Chip8State:
    def __init__(self):
        self.memory = bytearray(0x1000)
        self.PC = 0x200
        self.SP = 0x00
        self.DT = 0x00
        self.ST = 0x00
        self.stack = [0 for _ in range(20)]
        self.registers = bytearray(0x10)
        self.I = 0
        self.screen_buffer_length = 0x100
        self.screen_buffer_start = 0x1000 - self.screen_buffer_length
        self.keys = [False] * 16
        self.timer_counter = 9
        self.load_font(CHIP8_STANDARD_FONT)

    def load_program(self, program):
        rest = len(self.memory) - len(program) - 0x200
        self.memory[0x200: 0x200 + len(program)] = program
        self.memory[0x200 + len(program):] = [0x00] * rest

    def load_font(self, font):
        self.memory[:0x50] = font

    def reset(self):
        self.registers[:] = [0] * len(self.registers)
        self.memory[:] = [0] * (len(self.memory))
        self.DT = 0
        self.ST = 0
        self.I = 0
        self.PC = 0x200
        self.SP = 0
        self.stack[:] = [0] * len(self.stack)
        self.load_font(CHIP8_STANDARD_FONT)
