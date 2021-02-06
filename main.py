import pygame
import chip8cpu
import blitter
import random
import sys

CYCLES_PER_FRAME = 9

def update(surf, state):
    arr = pygame.PixelArray(surf)
    blitter.blit_screen(state, surf.map_rgb(0,50,0), surf.map_rgb(0,255,0), arr)

def make_noise(state):
    for i in range(len(state.memory)):
        state.memory[i] = random.randrange(0x00,0x100)

pygame.init()
screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()
playing = True

surf = pygame.Surface((64,32))
bigSurf = pygame.Surface((640,320))
state = chip8cpu.Chip8State()
cpu = chip8cpu.Chip8Cpu(state, lambda: random.randrange(0x00,0x100))
program = []

with open(sys.argv[1],"rb") as inFile:
    program = inFile.read()
state.load_program(program)

while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            playing = False
    for i in range(CYCLES_PER_FRAME):
        cpu.tick()
    update(surf, state)
    pygame.transform.scale(surf,(640,320), bigSurf)
    screen.blit(bigSurf, (80,20))        
    pygame.display.update()
    clock.tick(60)
pygame.quit()

