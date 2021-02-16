import pygame
from random import randrange
from sys import argv
from chip8.blitter import blit_screen
from chip8.chip8cpu import Chip8State, Chip8Cpu
from chip8.config import get_keys_config, keys_config_to_text

CYCLES_PER_FRAME = 9

key_numbers = {
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

def load_keys():
    try:
        with open('keys.conf','r') as file:
            return get_keys_config(file.readlines(), key_numbers)
    except FileNotFoundError:
        return key_numbers
def save_keys():
    with open('keys.conf','w') as file:
        file.writelines(keys_config_to_text(key_numbers))

surf = pygame.Surface((64,32))
bigSurf = pygame.Surface((640,320))
def draw_screen(state):
    arr = pygame.PixelArray(surf)
    blit_screen(state, surf.map_rgb(0,50,0), surf.map_rgb(0,255,0), arr)
    pygame.transform.scale(surf,(640,320), bigSurf)
    screen.blit(bigSurf, (80,20))

def load_program(state, name):
    with open(name, "rb") as inFile:
        program = inFile.read()
        state.load_program(program)

def simulate_cpu(cpu):
    for i in range(CYCLES_PER_FRAME):
        cpu.tick()

def update_sound():
    if state.ST>0:
        if not sound_playing:
            sound.play()
    else:
        if sound_playing:
            sound.stop()
    return state.ST>0

def get_options(args):
    options = args[2:]
    values = {'schip':False,'stop_every_frame':False}
    stop_every_frame = False
    values['file'] = args[1]
    for option in options:
        if option=='--schip':
            values['schip']=True
        elif option=='--stop-every-frame':
            values['stop_every_frame'] = True
    return values

def set_window_icon():
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)

if len(argv) == 1:
    print('Usage: {} program [--schip] [--stop-every-frame]'.format(argv[0]))
    exit()

def get_command(key):
    if key in key_numbers:
        return key_numbers[key]
    return None

def reset():
    state.reset()
    load_program(state, options['file'])

pygame.init()
set_window_icon()
pygame.display.set_caption('Chip 8')
screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

pygame.mixer.init()
sound = pygame.mixer.Sound('sound.mp3')
sound_playing = False

options = get_options(argv)

state = Chip8State()
cpu = Chip8Cpu(state, lambda: randrange(0x00,0x100))
cpu.schip = options['schip']
key_numbers = load_keys()
reset()

playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        elif event.type == pygame.KEYDOWN:
            command = get_command(event.key)
            if command == 'step':
                if options['stop_every_frame']:
                    simulate_cpu(cpu)
            elif command == 'reset':
                reset()
            else:
                state.keys[key_numbers[event.key]] = True
        elif event.type == pygame.KEYUP:
            command = get_command(event.key)
            if command in state.keys:
                state.keys[command] = False
    if not options['stop_every_frame']:
        simulate_cpu(cpu)

    sound_playing = update_sound()
    draw_screen(state)    
    pygame.display.update()
    clock.tick(60)

save_keys()
pygame.quit()