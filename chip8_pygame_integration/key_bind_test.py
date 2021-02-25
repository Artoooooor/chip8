import pygame
import unittest
from chip8_pygame_integration.key_bind import KeyBind, find_command


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
        evt = key_event(pygame.K_a)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertTrue(bind.matches(evt))

    def test_key_event_does_not_match_different_key(self):
        evt = key_event(pygame.K_b)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertFalse(bind.matches(evt))

    def test_same_key_different_mods_does_not_match(self):
        evt = key_event(pygame.K_a, pygame.KMOD_LCTRL | pygame.KMOD_SHIFT)
        bind = KeyBind(pygame.K_a, pygame.KMOD_NONE, 'comm1')
        self.assertFalse(bind.matches(evt))

    def test_same_key_same_mods_match(self):
        mods = pygame.KMOD_LCTRL | pygame.KMOD_SHIFT
        evt = key_event(pygame.K_a, mods)
        bind = KeyBind(pygame.K_a, mods, 'comm1')
        self.assertTrue(bind.matches(evt))


class FindEventTest(unittest.TestCase):
    def test_event_without_key_finds_none(self):
        self.when_binds_are([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'c1')])
        self.when_event_is(non_key_event())
        self.expect_command_found(None)

    def test_matching_event_no_mods_finds_command(self):
        self.when_binds_are([KeyBind(pygame.K_a, pygame.KMOD_NONE, 'c1')])
        self.when_event_is(key_event(pygame.K_a))
        self.expect_command_found('c1')

    def test_matching_event_with_mods_finds_command(self):
        self.when_binds_are([KeyBind(pygame.K_a, pygame.KMOD_CTRL, 'c1')])
        self.when_event_is(key_event(pygame.K_a, pygame.KMOD_CTRL))
        self.expect_command_found('c1')

    def when_binds_are(self, commands):
        self.commands = commands

    def when_event_is(self, event):
        self.event = event

    def expect_command_found(self, command):
        self.assertEqual(command, find_command(self.commands, self.event))


def key_event(key, mod=pygame.KMOD_NONE):
    return MockEvent(pygame.KEYUP, key, mod)


def non_key_event():
    return MockEvent(-1)


class MockEvent:
    def __init__(self, type, key=None, modifier=pygame.KMOD_NONE):
        self.type = type
        if key:
            self.key = key
        self.mod = modifier
