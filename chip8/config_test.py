import unittest
import pygame
from chip8.config import get_keys_config, keys_config_to_text

DEFAULT = {
    pygame.K_0: 0x0,
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0x4,
    pygame.K_5: 0x5,
    pygame.K_6: 0x6,
    pygame.K_7: 0x7,
    pygame.K_8: 0x8,
    pygame.K_9: 0x9,
    pygame.K_a: 0xA,
    pygame.K_b: 0xB,
    pygame.K_c: 0xC,
    pygame.K_d: 0xD,
    pygame.K_e: 0xE,
    pygame.K_f: 0xF,
    pygame.K_SPACE: 'step',
    pygame.K_p: 'reset',
}

EXPECTED = {
    pygame.K_a: 0x1,
    pygame.K_b: 0x2,
    pygame.K_c: 0x3,
    pygame.K_d: 0xC,
    pygame.K_e: 0x4,
    pygame.K_f: 0x5,
    pygame.K_g: 0x6,
    pygame.K_h: 0xD,
    pygame.K_i: 0x7,
    pygame.K_j: 0x8,
    pygame.K_k: 0x9,
    pygame.K_l: 0xE,
    pygame.K_m: 0xA,
    pygame.K_n: 0x0,
    pygame.K_o: 0xB,
    pygame.K_p: 0xF,
    pygame.K_SPACE: 'step',
    pygame.K_q: 'reset',
}

FIRST = 'a b c d\n'
SECOND = 'e f g h\n'
THIRD = 'i j k l\n'
FOURTH = 'm n o p\n'
FIFTH = 'SPACE\n'
SIXTH = 'q\n'

LINES = [FIRST, SECOND, THIRD, FOURTH, FIFTH, SIXTH]
LINES_ONE_TOO_SHORT = [FIRST, SECOND[:-2], THIRD, FOURTH, FIFTH, SIXTH]
LINES_ONE_TOO_LONG = [FIRST, SECOND + ' b', THIRD, FOURTH, FIFTH, SIXTH]
LINES_ONE_TWO_SPACES = [
    FIRST,
    SECOND.replace(' ', '  '),
    THIRD,
    FOURTH,
    FIFTH,
    SIXTH
]
LINES_ONE_TAB = [FIRST, SECOND.replace(' ', '\t'), THIRD, FOURTH, FIFTH, SIXTH]
LINES_ONE_DUPLICATE = [
    FIRST,
    SECOND.replace('f', 'e'),
    THIRD,
    FOURTH,
    FIFTH,
    SIXTH
]


class ConfigTest(unittest.TestCase):
    def test_default_returned_for_empty_lines(self):
        self.assertEqual(DEFAULT, get_keys_config([], DEFAULT))

    def test_keys_are_read_in_proper_order(self):
        self.assertEqual(EXPECTED, get_keys_config(LINES, DEFAULT))

    def test_too_short_line_results_in_default(self):
        self.assertEqual(
            DEFAULT,
            get_keys_config(LINES_ONE_TOO_SHORT, DEFAULT)
        )

    def test_too_long_line_results_in_default(self):
        self.assertEqual(DEFAULT, get_keys_config(LINES_ONE_TOO_LONG, DEFAULT))

    def test_two_spaces_count_as_one(self):
        self.assertEqual(
            EXPECTED,
            get_keys_config(LINES_ONE_TWO_SPACES, DEFAULT)
        )

    def test_tab_counts_as_space(self):
        self.assertEqual(EXPECTED, get_keys_config(LINES_ONE_TAB, DEFAULT))

    def test_duplicate_chars_result_in_default(self):
        self.assertEqual(
            DEFAULT,
            get_keys_config(LINES_ONE_DUPLICATE, DEFAULT)
        )

    def test_file_is_generated_based_on_key_config(self):
        self.assertEqual(
            [line for line in LINES],
            keys_config_to_text(EXPECTED)
        )


if __name__ == '__main__':
    unittest.main()
