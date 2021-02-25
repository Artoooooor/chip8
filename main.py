import pygame
from random import randrange
from sys import argv
from chip8.blitter import blit_screen
from chip8.chip8state import Chip8State
from chip8.chip8cpu import Chip8Cpu
from chip8.chip8gpu import Chip8Gpu
from chip8_pygame_integration.config import get_config_chip8, to_text_chip8
from chip8_pygame_integration.key_bind import find_command, KeyBind

CYCLES_PER_FRAME = 9

key_numbers = [
    KeyBind(pygame.K_0, pygame.KMOD_NONE, 0x0),
    KeyBind(pygame.K_1, pygame.KMOD_NONE, 0x1),
    KeyBind(pygame.K_2, pygame.KMOD_NONE, 0x2),
    KeyBind(pygame.K_3, pygame.KMOD_NONE, 0x3),
    KeyBind(pygame.K_4, pygame.KMOD_NONE, 0x4),
    KeyBind(pygame.K_5, pygame.KMOD_NONE, 0x5),
    KeyBind(pygame.K_6, pygame.KMOD_NONE, 0x6),
    KeyBind(pygame.K_7, pygame.KMOD_NONE, 0x7),
    KeyBind(pygame.K_8, pygame.KMOD_NONE, 0x8),
    KeyBind(pygame.K_9, pygame.KMOD_NONE, 0x9),
    KeyBind(pygame.K_a, pygame.KMOD_NONE, 0xA),
    KeyBind(pygame.K_b, pygame.KMOD_NONE, 0xB),
    KeyBind(pygame.K_c, pygame.KMOD_NONE, 0xC),
    KeyBind(pygame.K_d, pygame.KMOD_NONE, 0xD),
    KeyBind(pygame.K_e, pygame.KMOD_NONE, 0xE),
    KeyBind(pygame.K_f, pygame.KMOD_NONE, 0xF),
    KeyBind(pygame.K_SPACE, pygame.KMOD_NONE, 'step'),
    KeyBind(pygame.K_p, pygame.KMOD_NONE, 'reset'),
]


def load_keys():
    try:
        with open('keys.conf', 'r') as file:
            return get_config_chip8(file.readlines(), key_numbers)
    except FileNotFoundError:
        return key_numbers


def save_keys():
    with open('keys.conf', 'w') as file:
        file.writelines(to_text_chip8(key_numbers))


screenSurface = pygame.Surface((64, 32))
scaledSurface = pygame.Surface((640, 320))
offColour = screenSurface.map_rgb(0, 50, 0)
onColour = screenSurface.map_rgb(0, 255, 0)


def draw_screen(state):
    screenSurfaceArray = pygame.PixelArray(screenSurface)
    blit_screen(state, offColour, onColour, screenSurfaceArray)
    pygame.transform.scale(screenSurface, (640, 320), scaledSurface)
    screen.blit(scaledSurface, (80, 20))


def load_program(state, name):
    with open(name, "rb") as inFile:
        program = inFile.read()
        state.load_program(program)


def simulate_cpu(cpu):
    for i in range(CYCLES_PER_FRAME):
        cpu.tick()


def update_sound():
    if state.ST > 0:
        if not sound_playing:
            sound.play()
    else:
        if sound_playing:
            sound.stop()
    return state.ST > 0


def get_options(args):
    options = args[2:]
    values = {'schip': False, 'stop_every_frame': False}
    values['file'] = args[1]
    for option in options:
        if option == '--schip':
            values['schip'] = True
        elif option == '--stop-every-frame':
            values['stop_every_frame'] = True
    return values


def set_window_icon():
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)


if len(argv) == 1:
    print('Usage: {} program [--schip] [--stop-every-frame]'.format(argv[0]))
    exit()


def get_command(event):
    return find_command(key_numbers, event)


def reset():
    state.reset()
    load_program(state, options['file'])


pygame.init()
set_window_icon()
pygame.display.set_caption('Chip 8')
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

pygame.mixer.init()
sound = pygame.mixer.Sound('sound.mp3')
sound_playing = False

options = get_options(argv)

state = Chip8State()
gpu = Chip8Gpu(state)
cpu = Chip8Cpu(state, lambda: randrange(0x00, 0x100), gpu)
cpu.schip = options['schip']
key_numbers = load_keys()
reset()

playing = True
while playing:
    step = not options['stop_every_frame']
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        elif event.type == pygame.KEYDOWN:
            command = get_command(event)
            if command == 'step':
                step = True
            elif command == 'reset':
                reset()
            elif command is not None:
                state.keys[command] = True
        elif event.type == pygame.KEYUP:
            command = get_command(event)
            if command is not None:
                state.keys[command] = False
    if step:
        simulate_cpu(cpu)

    sound_playing = update_sound()
    draw_screen(state)
    pygame.display.update()
    clock.tick(60)

save_keys()
pygame.quit()
