import unittest

from chip8.chip8cpu import Chip8Cpu
from chip8.chip8state import Chip8State


class GpuMock:
    def __init__(self):
        self.lastAddress = None

    def draw(self, address, x, y, height):
        self.lastAddress = address
        self.lastX = x
        self.lastY = y
        self.lastHeight = height


class CpuTest(unittest.TestCase):

    def setUp(self):
        self.state = Chip8State()
        self.gpu = GpuMock()
        self.cpu = Chip8Cpu(self.state, self.get_random_mock, self.gpu)

    def get_random_mock(self):
        return self.random_mock_number

    def test_00e0_clears_screen(self):
        self.when_instruction_is(0x200, 0x00e0)
        self.when_memory_is_ones(
            self.state.screen_buffer_start, self.state.screen_buffer_length)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)
        self.assert_zeros(self.state.screen_buffer_start,
                          self.state.screen_buffer_length)
        self.assertEqual(0x1000, len(self.state.memory))

    def test_00ee_pops_stack_to_pc_and_increments_by_2(self):
        self.when_stack_is(0x300)
        self.when_instruction_is(0x200, 0xee)
        self.cpu.tick()
        self.assertEqual(0x302, self.state.PC)
        self.assertEqual(0x00, self.state.SP)

    def test_0nnn_except_00ee_and_00e0_is_ignored(self):
        for i in range(0x000, 0x1000):
            if i != 0x00ee and i != 0x00e0:
                self.when_stack_is(0x2)
                self.when_instruction_is(0x200, i)
                self.when_pc_is(0x200)
                self.when_memory_is_ones(
                    self.state.screen_buffer_start,
                    self.state.screen_buffer_length
                )
                self.cpu.tick()
                self.assertEqual(0x202, self.state.PC)
                self.assert_ones(self.state.screen_buffer_start,
                                 self.state.screen_buffer_length)

    def test_1ABC_jumps_to_ABC(self):
        self.when_instruction_is(0x200, 0x1ABC)
        self.cpu.tick()
        self.assertEqual(0xABC, self.state.PC)

    def test_2ABC_pushes_PC_and_jumps_to_ABC(self):
        self.when_instruction_is(0x200, 0x2ABC)
        self.cpu.tick()
        self.assertEqual(0xABC, self.state.PC)
        self.assert_stack(0x200)

    def test_3ABC_skips_instruction_if_rA_contains_BC(self):
        self.when_instruction_is(0x200, 0x3ABC)
        self.when_register_is(0xA, 0xBC)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_3ABC_does_not_skip_instruction_if_rA_contains_BB(self):
        self.when_instruction_is(0x200, 0x3ABC)
        self.when_register_is(0xA, 0xBB)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_4ABC_does_not_skip_instruction_if_rA_contains_BC(self):
        self.when_instruction_is(0x200, 0x4ABC)
        self.when_register_is(0xA, 0xBC)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_4ABC_skips_instruction_if_rA_does_not_contain_BC(self):
        self.when_instruction_is(0x200, 0x4ABC)
        self.when_register_is(0xA, 0xBB)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_5AB0_skips_instruction_if_rA_equals_rB(self):
        self.when_instruction_is(0x200, 0x5AB0)
        self.when_register_is(0xA, 0x12)
        self.when_register_is(0xB, 0x12)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_5AB0_does_not_skip_instruction_if_rA_differs_rB(self):
        self.when_instruction_is(0x200, 0x5AB0)
        self.when_register_is(0xA, 0x12)
        self.when_register_is(0xB, 0x13)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_5AB1_is_ignored(self):
        self.when_instruction_is(0x200, 0x5AB1)
        self.when_register_is(0xA, 0x12)
        self.when_register_is(0xB, 0x12)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_6C17_stores_17_in_rC(self):
        self.when_instruction_is(0x200, 0x6C17)
        self.cpu.tick()
        self.assertEqual(0x17, self.state.registers[0xC])

    def test_7C17_adds_17_to_rC(self):
        self.when_instruction_is(0x200, 0x7C17)
        self.when_register_is(0xC, 0x10)
        self.cpu.tick()
        self.assertEqual(0x27, self.state.registers[0xC])

    def test_7Cff_adds_ff_to_rC_and_handles_overflow(self):
        self.when_instruction_is(0x200, 0x7Cff)
        self.when_register_is(0xC, 0x10)
        self.cpu.tick()
        self.assertEqual(0x0f, self.state.registers[0xC])

    def test_8cb0_stores_rB_in_rC(self):
        self.when_instruction_is(0x200, 0x8CB0)
        self.when_register_is(0xB, 0x17)
        self.cpu.tick()
        self.assertEqual(0x17, self.state.registers[0xC])

    def test_8cb1_sets_rC_to_rC_or_rB(self):
        self.when_instruction_is(0x200, 0x8CB1)
        self.when_register_is(0xB, 0x06)
        self.when_register_is(0xC, 0x03)
        self.cpu.tick()
        self.assertEqual(0x07, self.state.registers[0xC])

    def test_8cb2_sets_rC_to_rC_and_rB(self):
        self.when_instruction_is(0x200, 0x8CB2)
        self.when_register_is(0xB, 0x06)
        self.when_register_is(0xC, 0x03)
        self.cpu.tick()
        self.assertEqual(0x02, self.state.registers[0xC])

    def test_8cb3_sets_rC_to_rC_xor_rB(self):
        self.when_instruction_is(0x200, 0x8CB3)
        self.when_register_is(0xB, 0x06)
        self.when_register_is(0xC, 0x03)
        self.cpu.tick()
        self.assertEqual(0x05, self.state.registers[0xC])

    def test_8cb4_adds_rB_to_rC_and_sets_rF_to_1_if_carry_occurs(self):
        self.when_instruction_is(0x200, 0x8CB4)
        self.when_register_is(0xB, 0xfe)
        self.when_register_is(0xC, 0x03)
        self.cpu.tick()
        self.assertEqual(0x01, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_8cb4_adds_rB_to_rC_and_sets_rF_to_0_if_carry_does_not_occur(self):
        self.when_instruction_is(0x200, 0x8CB4)
        self.when_register_is(0xB, 0xf0)
        self.when_register_is(0xC, 0x03)
        self.when_register_is(0xF, 0x01)
        self.cpu.tick()
        self.assertEqual(0xf3, self.state.registers[0xC])
        self.assertEqual(0x00, self.state.registers[0xF])

    def test_8cb5_subtracts_rB_from_rC_and_sets_rF_to_0_if_borrow_occurs(self):
        self.when_instruction_is(0x200, 0x8CB5)
        self.when_register_is(0xB, 0xff)
        self.when_register_is(0xC, 0x03)
        self.when_register_is(0xF, 0x01)
        self.cpu.tick()
        self.assertEqual(0x04, self.state.registers[0xC])
        self.assertEqual(0x00, self.state.registers[0xF])

    def test_8cb5_subtracts_rB_from_rC_and_sets_rF_to_1_if_not_borrowed(self):
        self.when_instruction_is(0x200, 0x8CB5)
        self.when_register_is(0xB, 0x01)
        self.when_register_is(0xC, 0x03)
        self.cpu.tick()
        self.assertEqual(0x02, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_8cb6_sets_rC_to_rB_rshift_1_and_rF_to_LSB_0(self):
        self.when_instruction_is(0x200, 0x8CB6)
        self.when_register_is(0xB, 0x12)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.registers[0xC])
        self.assertEqual(0x00, self.state.registers[0xF])

    def test_8cb6_sets_rC_to_rB_rshift_1_and_rF_to_LSB_1(self):
        self.when_instruction_is(0x200, 0x8CB6)
        self.when_register_is(0xB, 0x13)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_schip_mode_8cb6_shifts_rc(self):
        self.when_instruction_is(0x200, 0x8CB6)
        self.when_register_is(0xC, 0x13)
        self.when_schip_mode_on()
        self.cpu.tick()
        self.assertEqual(0x09, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_8cb7_sub_rC_from_rB_stores_in_rC_sets_rF_to_0_if_borrowed(self):
        self.when_instruction_is(0x200, 0x8CB7)
        self.when_register_is(0xB, 0x03)
        self.when_register_is(0xC, 0xff)
        self.when_register_is(0xf, 0x01)
        self.cpu.tick()
        self.assertEqual(0x04, self.state.registers[0xC])
        self.assertEqual(0x00, self.state.registers[0xF])

    def test_8cb7_sub_rC_from_rB_stores_in_rC_sets_rF_to_1_if_not_borrow(self):
        self.when_instruction_is(0x200, 0x8CB7)
        self.when_register_is(0xB, 0x0f)
        self.when_register_is(0xC, 0x01)
        self.cpu.tick()
        self.assertEqual(0x0e, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_8cbe_sets_rC_to_rB_lshift_1_and_rF_to_MSB_0(self):
        self.when_instruction_is(0x200, 0x8CBe)
        self.when_register_is(0xB, 0x03)
        self.cpu.tick()
        self.assertEqual(0x06, self.state.registers[0xC])
        self.assertEqual(0x00, self.state.registers[0xF])

    def test_8cbe_sets_rC_to_rB_lshift_1_and_rF_to_MSB_1(self):
        self.when_instruction_is(0x200, 0x8CBe)
        self.when_register_is(0xB, 0x81)
        self.cpu.tick()
        self.assertEqual(0x02, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_schip_mode_8cbe_shifts_rc(self):
        self.when_instruction_is(0x200, 0x8CBE)
        self.when_register_is(0xC, 0x81)
        self.when_schip_mode_on()
        self.cpu.tick()
        self.assertEqual(0x02, self.state.registers[0xC])
        self.assertEqual(0x01, self.state.registers[0xF])

    def test_9cb0_skips_instruction_if_ra_differs_from_rb(self):
        self.when_instruction_is(0x200, 0x9cb0)
        self.when_register_is(0xB, 0x81)
        self.when_register_is(0xC, 0x82)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_9cb0_does_not_skip_instruction_if_ra_equals_rb(self):
        self.when_instruction_is(0x200, 0x9cb0)
        self.when_register_is(0xB, 0x81)
        self.when_register_is(0xC, 0x81)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_9cb1_is_ignored(self):
        self.when_instruction_is(0x200, 0x9cb1)
        self.when_register_is(0xB, 0x81)
        self.when_register_is(0xC, 0x82)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_abcd_stores_bcd_in_i(self):
        self.when_instruction_is(0x200, 0xabcd)
        self.cpu.tick()
        self.assertEqual(0xbcd, self.state.I)

    def test_bbcd_jumps_to_bcd_plus_r0(self):
        self.when_instruction_is(0x200, 0xbbcd)
        self.when_register_is(0x0, 0x02)
        self.cpu.tick()
        self.assertEqual(0xbcf, self.state.PC)

    def test_caff_sets_ra_to_random(self):
        self.when_instruction_is(0x200, 0xcaff)
        self.when_random_number_is(0x2a)
        self.cpu.tick()
        self.assertEqual(0x2a, self.state.registers[0xa])

    def test_cafe_sets_ra_to_random_masked_by_fe(self):
        self.when_instruction_is(0x200, 0xcafe)
        self.when_random_number_is(0x2b)
        self.cpu.tick()
        self.assertEqual(0x2a, self.state.registers[0xa])

    def test_d123_draws_sprite(self):
        self.when_instruction_is(0x200, 0xd123)
        self.when_register_is(0x1, 0x23)
        self.when_register_is(0x2, 0x12)
        self.when_I_is(0x400)
        self.cpu.tick()
        self.assertDrawn(0x400, 0x23, 0x12, 0x3)

    def test_ea9e_skips_instruction_if_key_from_ra_is_pressed(self):
        self.when_instruction_is(0x200, 0xea9e)
        self.when_register_is(0xa, 0x01)
        self.when_key_is_pressed(0x1)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_ea9e_does_not_skip_instruction_if_key_from_ra_not_pressed(self):
        self.when_instruction_is(0x200, 0xea9e)
        self.when_register_is(0xa, 0x01)
        self.when_key_is_not_pressed(0x1)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_eaa1_skips_instruction_if_key_from_ra_is_not_pressed(self):
        self.when_instruction_is(0x200, 0xeaa1)
        self.when_register_is(0xa, 0x01)
        self.when_key_is_not_pressed(0x1)
        self.cpu.tick()
        self.assertEqual(0x204, self.state.PC)

    def test_eaa1_does_not_skip_instruction_if_key_from_ra_is_pressed(self):
        self.when_instruction_is(0x200, 0xeaa1)
        self.when_register_is(0xa, 0x01)
        self.when_key_is_pressed(0x1)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)

    def test_fa07_sets_ra_to_dt(self):
        self.when_instruction_is(0x200, 0xfa07)
        self.when_dt_is(0x2a)
        self.cpu.tick()
        self.assertEqual(0x2a, self.state.registers[0xa])

    def test_fa0a_stops_if_key_not_pressed(self):
        self.when_instruction_is(0x200, 0xfa0a)
        self.when_register_is(0xa, 0x01)
        self.cpu.tick()
        self.assertEqual(0x200, self.state.PC)

    def test_fa0a_advances_if_any_key_pressed(self):
        self.when_instruction_is(0x200, 0xfa0a)
        self.when_key_is_pressed(0x4)
        self.cpu.tick()
        self.assertEqual(0x202, self.state.PC)
        self.assertEqual(0x4, self.state.registers[0xa])

    def test_fa15_sets_dt_to_ra(self):
        self.when_instruction_is(0x200, 0xfa15)
        self.when_register_is(0xa, 0x2a)
        self.cpu.tick()
        self.assertEqual(0x2a, self.state.DT)

    def test_fa18_sets_st_to_ra(self):
        self.when_instruction_is(0x200, 0xfa18)
        self.when_register_is(0xa, 0x2a)
        self.cpu.tick()
        self.assertEqual(0x2a, self.state.ST)

    def test_fa1e_adds_ra_to_I(self):
        self.when_instruction_is(0x200, 0xfa1e)
        self.when_I_is(0x123)
        self.when_register_is(0xa, 0x2a)
        self.cpu.tick()
        self.assertEqual(0x14d, self.state.I)

    def test_fa29_sets_I_to_sprite_from_ra(self):
        self.when_instruction_is(0x200, 0xfa29)
        self.when_register_is(0xa, 0x04)
        self.cpu.tick()
        self.assertEqual(0x04 * 5, self.state.I)

    def test_fa33_stored_bcd_of_ra_in_memI(self):
        self.when_instruction_is(0x200, 0xfa33)
        self.when_register_is(0xa, 0xfe)
        self.when_I_is(0x300)
        self.cpu.tick()
        self.assert_memory_value(0x300, 0x02, 0x05, 0x04)
        self.assertEqual(0x1000, len(self.state.memory))

    def test_f355_stores_r0_to_r3_in_memI_to_memIplus3(self):
        self.when_instruction_is(0x200, 0xf355)
        self.when_registers_are(0x0, 0x01, 0x02, 0x03, 0x04, 0x05)
        self.when_I_is(0x300)
        self.cpu.tick()
        self.assert_memory_value(0x300, 0x01, 0x02, 0x03, 0x04, 0x00)
        self.assertEqual(0x304, self.state.I)
        self.assertEqual(0x1000, len(self.state.memory))

    def test_f365_loads_r0_to_r3_from_memI_to_memIplus3(self):
        self.when_instruction_is(0x200, 0xf365)
        self.when_I_is(0x300)
        self.when_memory_is(0x300, 0x01, 0x02, 0x03, 0x04, 0x05)
        self.cpu.tick()
        self.assert_registers(0x0, 0x01, 0x02, 0x03, 0x04, 0x00)
        self.assertEqual(0x304, self.state.I)
        self.assertEqual(0x1000, len(self.state.memory))

    def test_tick_decreases_timer_counter(self):
        self.when_timer_counter_is(0x05)
        self.cpu.tick()
        self.assertEqual(0x04, self.state.timer_counter)

    def test_dt_decrements_when_timer_counter_is_0(self):
        self.when_timer_counter_is(0x00)
        self.when_dt_is(0x02)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.timer_counter)
        self.assertEqual(0x01, self.state.DT)

    def test_dt_stays_at_0(self):
        self.when_timer_counter_is(0x00)
        self.when_dt_is(0x00)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.timer_counter)
        self.assertEqual(0x00, self.state.DT)

    def test_st_decrements_when_timer_counter_is_0(self):
        self.when_timer_counter_is(0x00)
        self.when_st_is(0x02)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.timer_counter)
        self.assertEqual(0x01, self.state.ST)

    def test_st_stays_at_0(self):
        self.when_timer_counter_is(0x00)
        self.when_st_is(0x00)
        self.cpu.tick()
        self.assertEqual(0x09, self.state.timer_counter)
        self.assertEqual(0x00, self.state.ST)

    def test_dt_not_upgraded_when_cpu_halted(self):
        self.when_instruction_is(0x200, 0xfa0a)
        self.when_timer_counter_is(0x01)
        self.when_dt_is(0x01)
        self.when_st_is(0x01)
        self.cpu.tick()
        self.assertEqual(0x01, self.state.timer_counter)
        self.assertEqual(0x01, self.state.DT)
        self.assertEqual(0x01, self.state.ST)

    def when_instruction_is(self, address, instruction):
        instruction_bytes = [(instruction >> 8) & 0xff, instruction & 0xff]
        self.when_memory_is(address, *instruction_bytes)

    def when_memory_is(self, address, *values):
        self.state.memory[address:address + len(values)] = values

    def when_memory_is_ones(self, start, length):
        self.state.memory[start:start + length] = [0x01] * length

    def when_stack_is(self, *numbers):
        for i, element in enumerate(numbers):
            self.state.stack[i] = element
        self.state.SP = len(numbers)

    def when_pc_is(self, pc):
        self.state.PC = pc

    def when_dt_is(self, dt):
        self.state.DT = dt

    def when_st_is(self, st):
        self.state.ST = st

    def when_I_is(self, i):
        self.state.I = i

    def when_registers_are(self, first, *values):
        self.state.registers[first:first + len(values)] = values

    def when_register_is(self, register, value):
        self.when_registers_are(register, value)

    def when_random_number_is(self, number):
        self.random_mock_number = number

    def when_key_is_pressed(self, key):
        self.state.keys[key] = True

    def when_key_is_not_pressed(self, key):
        self.state.keys[key] = False

    def when_timer_counter_is(self, value):
        self.state.timer_counter = value

    def when_schip_mode_on(self):
        self.cpu.schip = True

    def assert_zeros(self, start, length):
        for b in self.state.memory[start:start + length]:
            self.assertEqual(b, 0)

    def assert_ones(self, start, length):
        for b in self.state.memory[start:start + length]:
            self.assertEqual(b, 1)

    def assert_stack(self, *expected):
        for i, element in enumerate(expected):
            self.assertEqual(self.state.stack[i], element)
        self.assertEqual(self.state.SP, len(expected))

    def assert_memory_value(self, address, *values):
        for i, value in enumerate(values):
            self.assertEqual(value, self.state.memory[address + i])

    def assert_registers(self, first, *values):
        for i, value in enumerate(values):
            self.assertEqual(value, self.state.registers[first + i])

    def assertDrawn(self, address, x, y, height):
        self.assertEqual(address, self.gpu.lastAddress)
        self.assertEqual(x, self.gpu.lastX)
        self.assertEqual(y, self.gpu.lastY)
        self.assertEqual(height, self.gpu.lastHeight)


if __name__ == '__main__':
    unittest.main()
