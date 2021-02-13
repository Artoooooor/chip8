import pygame
def get_keys_config(lines, default):
    if lines:
        keys = {}
        numbers_per_line = ((0x1,0x2,0x3,0xC), (0x4,0x5,0x6,0xD), (0x7,0x8,0x9,0xE), (0xA,0x0,0xB,0xF))
        for i,line in enumerate(lines):
            chars = [char for char in line.split() if len(char) > 0]
            if len(chars) != 4:
                print('Line {} \'{}\' has invalid length - use exactly 4 characters per line'.format(i+1,  line))
                return default
            for (char,number) in zip(chars, numbers_per_line[i]):
                key = getattr(pygame,'K_' + char)
                if key in keys:
                    print('Duplicate key {} in line {} of config \'{}\''.format(char, i+1, line))
                    return default
                keys[key] = number
        return keys
    else:
        return default