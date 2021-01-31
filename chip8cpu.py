class Chip8State:
    def __init__(self):
        self.memory = bytearray(0x1000)
        self.PC = 0x200
        self.stack = [0 for _ in range(20)]
        self.SP = 0x00
        self.registers = bytearray(0x10)
        self.I = 0

class Chip8Cpu:
    def __init__(self,state):
        self.state=state

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
        self.state.PC += 2

    def push(self, number):
        self.state.stack[self.state.SP]=number
        self.state.SP += 1

    def pop(self):
        number = self.state.stack[self.state.SP-1]
        self.state.SP -= 1
        return number