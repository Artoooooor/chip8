class Chip8State:
    def __init__(self):
        self.memory = bytearray(0x1000)
        self.PC = 0x200

class Chip8Cpu:
    def __init__(self,state):
        self.state=state

    def tick(self):
        self.state.PC += 2
        for i in range(0x100):  
            self.state.memory[0x1000 - 0x100 + i]=0