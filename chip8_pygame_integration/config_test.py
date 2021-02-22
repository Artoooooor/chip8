import unittest
import pygame
from chip8_pygame_integration.config import get_config, KeyBind


DEFAULT = [KeyBind(pygame.K_o, pygame.KMOD_CTRL, 'some_command')]


class Config2LoadTest(unittest.TestCase):
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


class KeyBindTest(unittest.TestCase):
    def test_eq_returns_false_for_different_binds(self):
        bind1 = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        bind2 = KeyBind(pygame.K_b, pygame.KMOD_NONE, 'comm1')
        self.assertNotEqual(bind1, bind2)

    def test_eq_returns_true_for_equal_binds(self):
        bind1 = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        bind2 = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertEqual(bind1, bind2)

    def test_key_event_matches_same_key(self):
        evt = MockEvent(pygame.K_a)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertTrue(bind.matches(evt))

    def test_key_event_does_not_match_different_key(self):
        evt = MockEvent(pygame.K_b)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertFalse(bind.matches(evt))

    def test_same_key_different_mods_does_not_match(self):
        evt = MockEvent(pygame.K_a, pygame.KMOD_LCTRL | pygame.KMOD_SHIFT)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertFalse(bind.matches(evt))

    def test_same_key_same_mods_match(self):
        mods = pygame.KMOD_LCTRL | pygame.KMOD_SHIFT
        evt = MockEvent(pygame.K_a, mods)
        bind = KeyBind(pygame.K_a, mods, 'comm1')
        self.assertTrue(bind.matches(evt))


class MockEvent:
    def __init__(self, key, modifier=pygame.KMOD_NONE):
        self.key = key
        self.mod = modifier