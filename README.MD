# Chip8-PY - Chip8 emulator
The project is a simple Chip8 emulator written in Python.

[![Python package](https://github.com/Artoooooor/chip8/actions/workflows/python-package.yml/badge.svg)](https://github.com/Artoooooor/chip8/actions/workflows/python-package.yml)

## Running
python main.py program.rom [--schip] [--stop-every-frame]

--schip changes behaviour of the opcodes:
| Command | without --schip | with --schip |
|-|-|-|
| 8XY6 | rX = rY >> 1 | rX = rX >> 1 |
| 8XYE | rX = rY << 1 | rX = rX << 1 |
Many Chip8 program seem to rely on the schip behaviour.

--stop-every-frame halts the emulation on every frame. The emulation is advanced one frame when particular key is pressed (space by default).

## Configuration
Keys can be configured in file keys.conf. It has the following layout:
```
1 2 3 c
4 5 6 d
7 8 9 e
a 0 b f
SPACE
ctrl+r
```
First 4 lines configure keypad keys. Corresponding keys are:
```
0x1 0x2 0x3 0xC
0x4 0x5 0x6 0xD
0x7 0x8 0x9 0xE
0xA 0x0 0xB 0xF
```
The next 2 lines determine keys for stepping in --stop-every-frame mode and resetting the VM.

Every slot can be given a key or key combination. The following modifiers can be used:
* ctrl
* lctrl
* rctrl
* shift
* lshift
* rshift
* alt
* lalt
* ralt
