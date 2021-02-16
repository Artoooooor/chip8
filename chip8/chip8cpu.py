from math import floor

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
        self.memory[0x200 : 0x200 + len(program)] = program
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

class Chip8Cpu:
    def __init__(self,state, rng):
        self.state=state
        self.rng = rng
        self.schip = False

    def tick(self):
        instruction = (self.state.memory[self.state.PC] << 8) + self.state.memory[self.state.PC+1]
        group = (instruction & 0xf000) >> 0x0c
        register1 = (instruction & 0x0f00) >> 0x08
        register2 = (instruction & 0x00f0) >> 0x04
        address = instruction & 0x0fff
        value = instruction & 0x00ff
        mode = instruction & 0x000f
        halted = False
        if instruction == 0x00e0:
            self.state.memory[-0x100:] = [0]*0x100
        elif instruction == 0x00ee:
            self.state.PC = self.pop()
        elif group == 0x1:
            self.state.PC = address - 2;
        elif group == 0x2:
            self.push(self.state.PC)
            self.state.PC = address - 2;
        elif group == 0x3:
            self.skip_if_equal(self.state.registers[register1], value)
        elif group == 0x4:
            self.skip_if_not_equal(self.state.registers[register1], value)
        elif group == 0x5 and instruction & 0x000f == 0x00:
            self.skip_if_equal(self.state.registers[register1], self.state.registers[register2])
        elif group == 0x6:
            self.state.registers[register1] = value
        elif group == 0x7:
            self.state.registers[register1] = (self.state.registers[register1] + value) & 0xff
        elif group == 0x8:
            self.handle_alu(register1, register2, mode)
        elif group == 0x9 and instruction & 0x000f == 0:
            self.skip_if_not_equal(self.state.registers[register1], self.state.registers[register2])
        elif group == 0xa:
            self.state.I = address
        elif group == 0xb:
            self.state.PC = address + self.state.registers[0x0] - 2
        elif group == 0xc:
            self.state.registers[register1] = self.rng() & value
        elif group == 0xd:
            self.draw(register1, register2, mode)
        elif group == 0xe:
            self.handle_keyboard(register1, value)
        elif group == 0xf:
            halted = self.handle_memory_operation(register1, value)
        
        if not halted:
            self.state.PC += 2
            self.handle_timers()
        

    def push(self, number):
        self.state.stack[self.state.SP]=number
        self.state.SP += 1

    def pop(self):
        number = self.state.stack[self.state.SP-1]
        self.state.SP -= 1
        return number
    
    def skip_if_equal(self, value1, value2):
        if value1 == value2:
            self.state.PC += 2

    def skip_if_not_equal(self, value1, value2):
        if value1 != value2:
            self.state.PC += 2

    def handle_alu(self, register1, register2, mode):
        value1 = self.state.registers[register1]
        value2 = self.state.registers[register2]
        if mode == 0x0:
            self.state.registers[register1] = value2
        elif mode == 0x1:
            self.state.registers[register1] = value1 | value2
        elif mode == 0x2:
            self.state.registers[register1] = value1 & value2
        elif mode == 0x3:
            self.state.registers[register1] = value1 ^ value2
        elif mode == 0x4:
            self.state.registers[register1] = self.add(value1, value2)
        elif mode == 0x5:
            self.state.registers[register1] = self.subtract(value1, value2)
        elif mode == 0x6:
            value = value1 if self.schip else value2
            self.state.registers[register1] = value >> 1
            self.state.registers[0xf] = value & 0x01
        elif mode == 0x7:
            self.state.registers[register1] = self.subtract(value2, value1)
        elif mode == 0xe:
            value = value1 if self.schip else value2
            self.state.registers[register1] = (value << 1) & 0xff
            self.state.registers[0xf] = value >> 7

    def subtract(self, num1, num2):
        result = num1 - num2
        self.state.registers[0xf] = 0x00 if result<0 else 0x01
        if result<0:
            result += 0x100
        return result

    def add(self, num1, num2):
        result = (num1+num2) & 0xff
        self.state.registers[0xf] = 0x01 if result < num1 else 0x00
        return result

    def draw(self, register1, register2, mode):
        x = self.state.registers[register1] & 0x3f
        y = self.state.registers[register2] & 0x1f
        x_byte_shift = x >> 3;
        y_byte_shift = y << 3;
        shift_in_byte = x & 0x07;
        height = min(mode, 0x20 - y)
        start = self.state.screen_buffer_start + x_byte_shift + y_byte_shift
        self.state.registers[0xf] = 0x00
        for i in range(height):
            sprite_byte=self.state.memory[self.state.I + i]
            row_byte_shift = i << 3
            self.draw_byte(start + row_byte_shift, sprite_byte >> shift_in_byte)
            if x < 0x38:
                self.draw_byte(start + row_byte_shift + 1, sprite_byte << (8-shift_in_byte) & 0xff)

    def draw_byte(self, address, byte):
        self.state.memory[address] = self.state.memory[address] ^ byte
        if self.state.memory[address] & byte != byte:
            self.state.registers[0xf] = 0x01

    def handle_keyboard(self, register, mode):
        key = self.state.registers[register]
        if mode == 0x9e and self.is_key_pressed(key):
            self.state.PC += 2
        elif mode == 0xa1 and not self.is_key_pressed(key):
            self.state.PC += 2
    
    def handle_memory_operation(self, register, mode):
        halted = False
        registerValue = self.state.registers[register]
        if mode == 0x07:
            self.state.registers[register] = self.state.DT
        elif mode == 0x0a:
            key = self.get_key_pressed()
            if key is not None:
                self.state.registers[register] = key
            else:
                halted = True
        elif mode == 0x15:
            self.state.DT = registerValue
        elif mode == 0x18:
            self.state.ST = registerValue
        elif mode == 0x1e:
            self.state.I += registerValue
        elif mode == 0x29:
            self.state.I = registerValue * 5
        elif mode == 0x33:
            self.state.memory[self.state.I : self.state.I + 3] = to_bcd(registerValue)
        elif mode == 0x55:
            self.state.memory[self.state.I : self.state.I + register + 1] = self.state.registers[:register + 1]
            self.state.I += register + 1
        elif mode == 0x65:
            self.state.registers[:register + 1] = self.state.memory[self.state.I : self.state.I + register + 1]
            self.state.I += register + 1
        return halted
    
    def handle_timers(self):
        if self.state.timer_counter>0:
            self.state.timer_counter -= 1
        else:
            self.state.timer_counter = 9
            self.state.DT = max(self.state.DT - 1, 0)
            self.state.ST = max(self.state.ST - 1, 0)

    def get_key_pressed(self):
        for key, keyState in enumerate(self.state.keys):
            if keyState:
                return key
        return None

    def is_key_pressed(self, key):
        if key<=0xf:
            return self.state.keys[key]
        else:
            return False

def to_bcd(number):
    a = floor(number/100)
    number -= a * 100
    b = floor(number/10)
    number -= b * 10
    c = number
    return a,b,c