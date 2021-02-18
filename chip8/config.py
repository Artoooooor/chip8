import pygame
numbers_per_line = ((0x1, 0x2, 0x3, 0xC), (0x4, 0x5, 0x6, 0xD),
                    (0x7, 0x8, 0x9, 0xE), (0xA, 0x0, 0xB, 0xF), ('step',), ('reset',))


def get_keys_config(lines, default):
    if lines:
        keys = {}
        for i, line in enumerate(lines):
            chars = [char for char in line.split() if len(char) > 0]
            if len(chars) != len(numbers_per_line[i]):
                print('Line {} \'{}\' has invalid length - use exactly {} entries'.format(
                    i+1, line, len(numbers_per_line[i])))
                return default
            for (char, number) in zip(chars, numbers_per_line[i]):
                key = getattr(pygame, 'K_' + char)
                if key in keys:
                    print('Duplicate key {} in line {} of config \'{}\''.format(
                        char, i+1, line))
                    return default
                keys[key] = number

        return keys
    else:
        return default


def reverse_dictionary(dict):
    return {number: key for key, number in dict.items()}


def get_key_numbers_from_pygame():
    return {key[2:]: value for key, value in vars(pygame).items() if 'K_' in key}


def keys_config_to_text(key_config):
    reverse_config = reverse_dictionary(key_config)
    key_names = reverse_dictionary(get_key_numbers_from_pygame())

    def get_key_name(chip8_key_number):
        real_key_number = reverse_config[chip8_key_number]
        return key_names[real_key_number]

    def get_text_line(number_line):
        return ' '.join([get_key_name(chip8_key_number) for chip8_key_number in number_line]) + '\n'
    lines = [get_text_line(number_line) for number_line in numbers_per_line]
    return lines
