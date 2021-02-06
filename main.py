import pygame
import chip8cpu
import blitter
import random
import sys

CYCLES_PER_FRAME = 9

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
clock = pygame.time.Clock()
state = chip8cpu.Chip8State()
cpu = chip8cpu.Chip8Cpu(state, lambda: random.randrange(0x00,0x100))

load_program(state, sys.argv[1])

playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
    simulate_cpu(cpu)
    draw_screen(state)
    pygame.display.update()
    clock.tick(60)
pygame.quit()

