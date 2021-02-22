import unittest
from chip8.chip8cpu import Chip8State
from chip8.chip8gpu import Chip8Gpu


class Chip8GpuTest(unittest.TestCase):
    def setUp(self):
        self.state = Chip8State()
        self.gpu = Chip8Gpu(self.state)

    def test_sprite_height_0_changes_nothing(self):
        self.when_memory_is(0x400, 0xff)
        self.gpu.draw(0x400, 0, 0, 0)
        self.assert_memory_column(0, 0x00)
        self.assertEqual(0x00, self.state.registers[0xf])

    def test_sprite_height_1_draws_1_byte(self):
        self.when_memory_is(0x400, 0x01)
        self.gpu.draw(0x400, 0, 0, 1)
        self.assert_memory_column(0, 0x01)
        self.assertEqual(0x00, self.state.registers[0xf])

    def test_sprite_height_2_draws_2_bytes(self):
        self.when_memory_is(0x400, 0x01, 0x02)
        self.gpu.draw(0x400, 0, 0, 2)
        self.assert_memory_column(0, 0x01, 0x02)

    def test_sprite_drawn_x_shifted(self):
        self.when_memory_is(0x400, 0x01, 0x02)
        self.gpu.draw(0x400, 0x08, 0, 2)
        self.assert_memory_column(0x01, 0x01, 0x02)

    def test_sprite_drawn_y_shifted(self):
        self.when_memory_is(0x400, 0x01, 0x02)
        self.gpu.draw(0x400, 0, 0x02, 2)
        self.assert_memory_column(0x10, 0x01, 0x02)

    def test_sprite_drawn_x_gt_64(self):
        self.when_memory_is(0x400, 0x01, 0x02)
        self.gpu.draw(0x400, 0x88, 0, 2)
        self.assert_memory_column(0x01, 0x01, 0x02)

    def test_sprite_drawn_y_gt_32(self):
        self.when_memory_is(0x400, 0x01, 0x02)
        self.gpu.draw(0x400, 0, 0x42, 0x2)
        self.assert_memory_column(0x10, 0x01, 0x02)

    def test_sprite_drawn_y_partially_visible(self):
        self.when_memory_is(0x400, 0x01, 0x02, 0x03, 0x04)
        self.gpu.draw(0x400, 0, 0x1e, 0x2)
        self.assert_memory_column((0x1e << 3), 0x01, 0x02)

    def test_sprite_drawn_x_not_divisible_by_8(self):
        self.when_memory_is(0x400, 0xff, 0xaf)
        self.gpu.draw(0x400, 0x03, 0, 0x2)
        self.assert_memory_column(0, 0xff >> 3, 0xaf >> 3)
        self.assert_memory_column(1, (0xff << 5) & 0xff, (0xaf << 5) & 0xff)

    def test_sprite_drawn_x_not_divisible_by_8_partially_visible(self):
        self.when_memory_is(0x400, 0xff, 0xff)
        self.gpu.draw(0x400, 0x3f, 0, 0x2)
        self.assert_memory_column(0x07, 0x01, 0x01)
        self.assert_memory_column(0, *[0x00] * 32)

    def test_draw_sets_rf_to_1_if_1_is_changed_to_0(self):
        self.when_memory_is(0x400, 0xff)
        self.when_memory_is(self.state.screen_buffer_start, 0x01)
        self.gpu.draw(0x400, 0, 0, 0x1)
        self.assert_memory_column(0, 0xfe)
        self.assertEqual(0x01, self.state.registers[0xf])

    def test_draw_sets_rf_to_1_if_1_is_changed_to_0_x_not_divisible_by_8(self):
        self.when_memory_is(0x400, 0xff)
        self.when_memory_is(self.state.screen_buffer_start, 0x01, 0x80)
        self.gpu.draw(0x400, 0x04, 0, 0x1)
        self.assert_memory_column(0, 0x0e)
        self.assert_memory_column(1, 0x70)
        self.assertEqual(0x01, self.state.registers[0xf])

    def test_draw_sets_rf_to_0_if_1_not_changed_to_0_x_not_div_by_8(self):
        self.when_memory_is(0x400, 0xff)
        self.when_memory_is(self.state.screen_buffer_start, 0xf0, 0x0f)
        self.when_register_is(0xf, 0x01)
        self.gpu.draw(0x400, 0x04, 0, 0x1)
        self.assert_memory_column(0, 0xff)
        self.assert_memory_column(1, 0xff)
        self.assertEqual(0x00, self.state.registers[0xf])

    def test_last_group_drawn(self):
        self.when_memory_is(0x400, 0xff)
        self.gpu.draw(0x400, 0x38, 0x1f, 0x1)
        self.assert_memory_column(0x1f * 0x08 + (0x38 >> 3), 0xff)

    def when_memory_is(self, address, *values):
        self.state.memory[address: address + len(values)] = values

    def when_register_is(self, register, value):
        self.state.registers[register] = value

    def assert_memory_column(self, offset, *values):
        start = self.state.screen_buffer_start + offset
        for i, value in enumerate(values):
            self.assertEqual(value, self.state.memory[start + i * 0x008])
