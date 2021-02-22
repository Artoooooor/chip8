import pygame


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


class KeyBind:
    def __init__(self, key, keyMod, command):
        self.key = key
        self.keyMod = keyMod
        self.command = command

    def __eq__(self, other):
        keysMatch = self.key == other.key
        modsMatch = self.keyMod == other.keyMod
        commandsMatch = self.command == other.command
        return keysMatch and modsMatch and commandsMatch

    def matches(self, event):
        return self.key == event.key and self.keyMod == event.mod

    def __str__(self):
        return self.__get_str(' ')

    def __repr__(self):
        return self.__get_str(',')

    def __get_str(self, separator):
        return separator.join([str(self.key), str(self.keyMod), self.command])
