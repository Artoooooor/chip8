import pygame
from chip8_pygame_integration.key_bind import KeyBind


def reverse_dictionary(dict):
    return {number: key for key, number in dict.items()}


PYGAME_ITEMS = vars(pygame).items()
PYGAME_KEYS = {k[2:]: v for k, v in PYGAME_ITEMS if 'K_' in k}
PYGAME_KEYS_BY_NUMBER = reverse_dictionary(PYGAME_KEYS)
PYGAME_KMODS = {k[5:].lower(): v for k, v in PYGAME_ITEMS if 'KMOD_' in k}
PYGAME_KMODS_BY_NUMBER = reverse_dictionary(PYGAME_KMODS)
INVALID_LENGTH = 'Line {} \'{}\' has invalid length - use {} entries'


def get_config(pattern, lines, default=None):
    if len(pattern) == 0:
        return []
    binds = []
    i = 0
    for line, commands in zip(lines, pattern):
        i += 1
        line_length = len(line)
        commands_length = len(commands)
        if line_length >= commands_length:
            keys = line.split()
            binds += [get_bind(comm, key) for comm, key in zip(commands, keys)]
        else:
            print(INVALID_LENGTH.format(i, line, commands_length))
            return default
    return binds


def get_bind(command, inputKey):
    elements = inputKey.split('+')
    keyMod = pygame.KMOD_NONE
    key = None
    for element in elements:
        if is_key_modifier(element):
            keyMod |= to_modifier(element)
        else:
            key = to_key(element)
    return KeyBind(key, keyMod, command)


def is_key_modifier(key):
    return getattr(pygame, 'KMOD_' + key.upper(), None) is not None


def to_modifier(key):
    return getattr(pygame, 'KMOD_' + key.upper())


def to_key(key):
    return getattr(pygame, 'K_' + key.lower())


def to_text(pattern, config):
    if len(pattern) == 0:
        return []

    lines = []
    for commands in pattern:
        chars = []
        for command in commands:
            bind = find_bind(command, config)
            chars.append(to_repr(bind))
        lines.append(' '.join(chars))
    return lines


def to_repr(bind):
    elements = []
    elements += get_first_mod(bind, 'ctrl', 'lctrl', 'rctrl')
    elements += get_first_mod(bind, 'shift', 'lshift', 'rshift')
    elements += get_first_mod(bind, 'alt', 'lalt', 'ralt')
    elements += get_first_mod(bind, 'meta', 'lmeta', 'rmeta')
    elements += get_all_mods(bind, 'caps', 'num', 'mode')
    elements.append(PYGAME_KEYS_BY_NUMBER[bind.key])

    return '+'.join(elements)


def get_first_mod(bind, *mods):
    for mod in mods:
        if has_mod(bind, mod):
            return [mod]
    return []


def get_all_mods(bind, *mods):
    return [mod for mod in mods if has_mod(bind, mod)]


def has_mod(bind, modName):
    mod = PYGAME_KMODS[modName]
    return bind.keyMod & mod == mod


def find_bind(command, config):
    for bind in config:
        if bind.command == command:
            return bind
    return None
