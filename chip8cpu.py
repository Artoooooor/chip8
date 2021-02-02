class Chip8State:
    def __init__(self):
        self.memory = bytearray(0x1000)
        self.PC = 0x200
        self.SP = 0x00
        self.DT = 0x00
        self.stack = [0 for _ in range(20)]
        self.registers = bytearray(0x10)
        self.I = 0
        self.screen_buffer_length = 0x100
        self.screen_buffer_start = 0x1000 - self.screen_buffer_length
        self.keys = [False] * 16

class Chip8Cpu:
    def __init__(self,state, rng):
        self.state=state
        self.rng = rng

    def tick(self):
        instruction = (self.state.memory[self.state.PC] << 8) + self.state.memory[self.state.PC+1]
        if instruction == 0x00e0:
            for i in range(0x100):  
                self.state.memory[0x1000 - 0x100 + i]=0
        elif instruction == 0x00ee:
            self.state.PC = self.pop()
        elif (instruction & 0xf000) == 0x1000:
            self.state.PC = (instruction & 0x0fff) - 2;
        elif (instruction & 0xf000) == 0x2000:
            self.push(self.state.PC)
            self.state.PC = (instruction & 0x0fff) - 2;
        elif (instruction & 0xf000) == 0x3000:
            register = (instruction & 0x0f00) >> 0x08;
            value = instruction & 0x00ff
            if self.state.registers[register] == value:
                self.state.PC += 2
        elif (instruction & 0xf000) == 0x4000:
            register = (instruction & 0x0f00) >> 0x08;
            value = instruction & 0x00ff
            if self.state.registers[register] != value:
                self.state.PC += 2
        elif (instruction & 0xf000) == 0x5000 and instruction & 0x000f == 0x00:
            register1 = (instruction & 0x0f00) >> 0x08;
            register2 = (instruction & 0x00f0) >> 0x04;
            if self.state.registers[register1] == self.state.registers[register2]:
                self.state.PC += 2
        elif (instruction & 0xf000) == 0x6000:
            register = (instruction & 0x0f00) >> 0x08;
            value = instruction & 0x00ff
            self.state.registers[register] = value
        elif (instruction & 0xf000) == 0x7000:
            register = (instruction & 0x0f00) >> 0x08;
            value = instruction & 0x00ff
            self.state.registers[register] += value
        elif (instruction & 0xf000) == 0x8000:
            register1 = (instruction & 0x0f00) >> 0x08;
            register2 = (instruction & 0x00f0) >> 0x04;
            if instruction & 0x000f == 0x0:
                self.state.registers[register1] = self.state.registers[register2]
            elif instruction & 0x000f == 0x1:
                self.state.registers[register1] = self.state.registers[register1] | self.state.registers[register2]
            elif instruction & 0x000f == 0x2:
                self.state.registers[register1] = self.state.registers[register1] & self.state.registers[register2]
            elif instruction & 0x000f == 0x3:
                self.state.registers[register1] = self.state.registers[register1] ^ self.state.registers[register2]
            elif instruction & 0x000f == 0x4:
                sum = self.state.registers[register1] + self.state.registers[register2]
                self.state.registers[register1] = sum & 0xff
                if self.state.registers[register1] < sum:
                    self.state.registers[0xf] = 0x01
            elif instruction & 0x000f == 0x5:
                result = self.state.registers[register1] - self.state.registers[register2]
                if result<0:
                    result += 0x100
                else:
                    self.state.registers[0xf] = 0x01
                self.state.registers[register1] = result
            elif instruction & 0x000f == 0x6:
                self.state.registers[register1] = self.state.registers[register2] >> 1
                self.state.registers[0xf] = self.state.registers[register2] & 0x01
            elif instruction & 0x000f == 0x7:
                result = self.state.registers[register2] - self.state.registers[register1]
                if result<0:
                    result += 0x100
                else:
                    self.state.registers[0xf] = 0x01
                self.state.registers[register1] = result
            elif instruction & 0x000f == 0xe:
                self.state.registers[register1] = (self.state.registers[register2] << 1) & 0xff
                self.state.registers[0xf] = self.state.registers[register2] >> 7
        elif instruction & 0xf000 == 0x9000 and instruction & 0x000f == 0:
            register1 = (instruction & 0x0f00) >> 0x08;
            register2 = (instruction & 0x00f0) >> 0x04;
            if self.state.registers[register1] != self.state.registers[register2]:
                self.state.PC += 2
        elif instruction & 0xf000 == 0xa000:
            self.state.I = instruction & 0x0fff
        elif instruction & 0xf000 == 0xb000:
            self.state.PC = (instruction & 0x0fff) + self.state.registers[0x0] - 2
        elif instruction & 0xf000 == 0xc000:
            register = (instruction & 0x0f00) >> 0x08;
            mask = instruction & 0x00ff
            self.state.registers[register] = self.rng() & mask
        elif instruction & 0xf000 == 0xd000:
            register1 = (instruction & 0x0f00) >> 0x08;
            register2 = (instruction & 0x00f0) >> 0x04;
            x = self.state.registers[register1] & 0x3f
            y = self.state.registers[register2] & 0x1f
            x_byte_shift = x >> 3;
            y_byte_shift = y << 3;
            shift_in_byte = x & 0x07;
            height = min(instruction & 0x000f, 0x20 - y)
            start = self.state.screen_buffer_start + x_byte_shift + y_byte_shift
            for i in range(height):
                sprite_byte=self.state.memory[self.state.I + i]
                row_byte_shift = i << 3
                self.draw_byte(start + row_byte_shift, sprite_byte >> shift_in_byte)
                if x < 0x3f:
                    self.draw_byte(start + row_byte_shift + 1, sprite_byte << (8-shift_in_byte) & 0xff)
        elif instruction & 0xf000 == 0xe000:
            register = (instruction & 0x0f00) >> 8
            key = self.state.registers[register]
            mode = instruction & 0x00ff
            if mode == 0x9e and self.state.keys[key]:
                self.state.PC += 2
            elif mode == 0xa1 and not self.state.keys[key]:
                self.state.PC += 2
        elif instruction & 0xf000 == 0xf000:
            mode = instruction & 0x00ff
            register = (instruction & 0x0f00) >> 8
            if mode == 0x07:
                self.state.registers[register] = self.state.DT
            elif mode == 0x0a:
                key = self.state.registers[register]
                if not self.state.keys[key]:
                    return
            elif mode == 0x15:
                self.state.DT = self.state.registers[register]
        self.state.PC += 2

    def push(self, number):
        self.state.stack[self.state.SP]=number
        self.state.SP += 1

    def pop(self):
        number = self.state.stack[self.state.SP-1]
        self.state.SP -= 1
        return number

    def draw_byte(self,address,byte):
        self.state.memory[address] = self.state.memory[address] ^ byte
        if self.state.memory[address] != byte:
            self.state.registers[0xf] = 0x01