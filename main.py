import pygame
import chip8cpu
import blitter
import random
import sys
from config import get_keys_config

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
    pygame.K_f: 0xF
}

def load_keys():
    numbers_per_line = ((0x1,0x2,0x3,0xC), (0x4,0x5,0x6,0xD), (0x7,0x8,0x9,0xE), (0xA,0x0,0xB,0xF))

    with open('keys.conf','r+') as file:
        return get_keys_config(file.readlines(), key_numbers)

surf = pygame.Surface((64,32))
bigSurf = pygame.Surface((640,320))
def draw_screen(state):
    arr = pygame.PixelArray(surf)
    blitter.blit_screen(state, surf.map_rgb(0,50,0), surf.map_rgb(0,255,0), arr)
    pygame.transform.scale(surf,(640,320), bigSurf)
    screen.blit(bigSurf, (80,20))

def load_program(state, name):
    with open(name, "rb") as inFile:
        program = inFile.read()
        state.load_program(program)

def simulate_cpu(cpu):
    for i in range(CYCLES_PER_FRAME):
        cpu.tick()

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption('Chip 8')
clock = pygame.time.Clock()
state = chip8cpu.Chip8State()
cpu = chip8cpu.Chip8Cpu(state, lambda: random.randrange(0x00,0x100))

load_program(state, sys.argv[1])
options = sys.argv[2:]
stop_every_frame = False
for option in options:
    if option=='--schip':
        cpu.schip=True
    elif option=='--stop-every-frame':
        stop_every_frame = True

key_numbers = load_keys()

playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
        elif event.type == pygame.KEYDOWN:
            if event.key in key_numbers:
                state.keys[key_numbers[event.key]] = True
            elif event.key == pygame.K_SPACE and stop_every_frame:
                simulate_cpu(cpu)
        elif event.type == pygame.KEYUP:
            if event.key in key_numbers:
                state.keys[key_numbers[event.key]] = False
    if not stop_every_frame:
        simulate_cpu(cpu)
    draw_screen(state)    
    pygame.display.update()
    clock.tick(60)
pygame.quit()

