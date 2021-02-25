import pygame
import unittest
from chip8_pygame_integration.config import KeyBind


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
