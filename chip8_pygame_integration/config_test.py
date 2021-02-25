import unittest
import pygame
from chip8_pygame_integration.config import get_config, KeyBind, to_text


DEFAULT = [KeyBind(pygame.K_o, pygame.KMOD_CTRL, 'some_command')]


class ConfigLoadTest(unittest.TestCase):
    def setUp(self):
        self.default = None

    def test_empty_pattern_returns_empty_array(self):
        self.assertEqual([], get_config((), []))

    def test_single_command_pattern_parses_single_key(self):
        self.when_pattern_is((('comm1',),))
        self.when_lines_are(['A'])
        self.expect_config([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')])

    def test_two_command_pattern_parses_2_keys(self):
        self.when_pattern_is((('comm1', 'comm2',),))
        self.when_lines_are(['A D'])
        self.expect_config([
            KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1'),
            KeyBind(pygame.K_d, pygame.KMOD_NONE, 'comm2')])

    def test_2_lines_pattern_parses_2_lines(self):
        self.when_pattern_is((('comm1',), ('comm2',)))
        self.when_lines_are(['A', 'D'])
        self.expect_config([
            KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1'),
            KeyBind(pygame.K_d, pygame.KMOD_NONE, 'comm2')])

    def test_too_little_elements_in_line_return_default(self):
        self.when_pattern_is((('comm1', 'comm2'),))
        self.when_lines_are(['A'])
        self.when_default_is(DEFAULT)
        self.expect_config(DEFAULT)

    def test_ctrl_is_parsed_as_KMOD_CTRL(self):
        self.when_pattern_is((('comm1',),))
        self.when_lines_are(['ctrl+A'])
        self.expect_config([KeyBind(pygame.K_a, pygame.KMOD_CTRL, 'comm1')])

    def test_two_modifiers_are_parsed(self):
        self.when_pattern_is((('comm1',),))
        self.when_lines_are(['ctrl+lshift+A'])
        kmods = pygame.KMOD_CTRL | pygame.KMOD_LSHIFT
        self.expect_config([KeyBind(pygame.K_a, kmods, 'comm1')])

    def test_lowercase_keys_are_parsed(self):
        self.when_pattern_is((('comm1',),))
        self.when_lines_are(['a'])
        self.expect_config([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')])

    def test_uppercase_modifiers_are_parsed(self):
        self.when_pattern_is((('comm1',),))
        self.when_lines_are(['LCTRL+A'])
        self.expect_config([KeyBind(pygame.K_a, pygame.KMOD_LCTRL, 'comm1')])

    def when_pattern_is(self, pattern):
        self.pattern = pattern

    def when_lines_are(self, lines):
        self.lines = lines

    def when_default_is(self, default):
        self.default = default

    def expect_config(self, config):
        result = get_config(self.pattern, self.lines, self.default)
        self.assertEqual(config, result)


class ConfigSaveTest(unittest.TestCase):
    def test_empty_pattern_generates_empty_file(self):
        self.assertEqual([], to_text((), []))

    def test_one_command_generates_1_line(self):
        self.when_pattern_is((('comm1',),))
        self.when_config_is([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')])
        self.expect_generated_text(['a'])

    def test_two_commands_generate_line_with_2_elements(self):
        self.when_pattern_is((('comm1', 'comm2'),))
        self.when_config_is([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1'),
                             KeyBind(pygame.K_b, pygame.KMOD_NONE, 'comm2')])
        self.expect_generated_text(['a b'])

    def test_commands_are_generated_in_order_of_pattern(self):
        self.when_pattern_is((('comm1', 'comm2'),))
        self.when_config_is([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm2'),
                             KeyBind(pygame.K_b, pygame.KMOD_NONE, 'comm1')])
        self.expect_generated_text(['b a'])

    def test_two_lines_generate_2_lines_(self):
        self.when_pattern_is((('comm1',), ('comm2',),))
        self.when_config_is([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm2'),
                             KeyBind(pygame.K_b, pygame.KMOD_NONE, 'comm1')])
        self.expect_generated_text(['b', 'a'])

    def test_KMOD_CTRL_generates_output(self):
        self.expect_3_mod_versions_handled('ctrl')

    def test_KMOD_SHIFT_generates_output(self):
        self.expect_3_mod_versions_handled('shift')

    def test_KMOD_ALT_generates_output(self):
        self.expect_3_mod_versions_handled('alt')

    def test_KMOD_META_generates_output(self):
        self.expect_3_mod_versions_handled('meta')

    def test_KMOD_CAPS_generates_output(self):
        self.expect_mod_handled('caps')

    def test_KMOD_NUM_generates_output(self):
        self.expect_mod_handled('num')

    def test_KMOD_MODE_generates_output(self):
        self.expect_mod_handled('mode')

    def expect_3_mod_versions_handled(self, baseModName):
        self.expect_mod_handled(baseModName)
        self.expect_mod_handled('l' + baseModName)
        self.expect_mod_handled('r' + baseModName)

    def expect_mod_handled(self, modName):
        self.when_pattern_is((('comm1',),))
        fieldName = 'KMOD_' + modName.upper()
        mod = getattr(pygame, fieldName)
        self.when_config_is([KeyBind(pygame.K_a, mod, 'comm1')])
        expected = '{}+a'.format(modName)
        self.expect_generated_text([expected])

    def when_pattern_is(self, pattern):
        self.pattern = pattern

    def when_config_is(self, config):
        self.config = config

    def expect_generated_text(self, text):
        self.assertEqual(text, to_text(self.pattern, self.config))
