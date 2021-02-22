class Chip8Gpu:
    def __init__(self, state):
        self.state = state

    def draw(self, address, x, y, height):
        x = x & 0x3f
        y = y & 0x1f
        x_byte_shift = x >> 3
        y_byte_shift = y << 3
        shift_in_byte = x & 0x07
        height = min(height, 0x20 - y)
        start = self.state.screen_buffer_start + x_byte_shift + y_byte_shift
        self.state.registers[0xf] = 0x00
        for i in range(height):
            sprite_byte = self.state.memory[address + i]
            row_byte_shift = i << 3
            self.draw_byte(start + row_byte_shift,
                           sprite_byte >> shift_in_byte)
            if x < 0x38:
                self.draw_byte(start + row_byte_shift + 1,
                               sprite_byte << (8 - shift_in_byte) & 0xff)

    def draw_byte(self, address, byte):
        self.state.memory[address] = self.state.memory[address] ^ byte
        if self.state.memory[address] & byte != byte:
            self.state.registers[0xf] = 0x01
