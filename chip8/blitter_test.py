import unittest
import numpy
from blitter import blit_screen

class StateMock:
    def __init__(self):
        self.screen_buffer_start = 0
        self.memory = [0] * 0x100

class BlitterTest(unittest.TestCase):
    def setUp(self):
        self.state = StateMock()
        self.color1 = 0x000000
        self.color2 = 0x00ff00
        self.array = numpy.ndarray((64,32))

    def test_zeros_mapped_to_color1(self):
        blit_screen(self.state, self.color1, self.color2, self.array)
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                self.assertEqual(self.color1,self.array[x,y])

    def test_255_mapped_to_color2(self):
        self.state.memory[:] = [0xff] * 0x100
        blit_screen(self.state, self.color1, self.color2, self.array)
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                self.assertEqual(self.color2,self.array[x,y])

    def test_screen_buffer_start_is_used(self):
        self.state.memory = [0x0] * 0x100 + [0xff] * 0x100
        self.state.screen_buffer_start = 0x100
        blit_screen(self.state, self.color1, self.color2, self.array)
        for x in range(self.array.shape[0]):
            for y in range(self.array.shape[1]):
                self.assertEqual(self.color2,self.array[x,y])
    
    def test_0xaa_is_bit_mapped(self):
        self.state.memory[0] = 0xaa
        blit_screen(self.state, self.color1, self.color2, self.array)
        self.assertEqual(self.color2,self.array[0,0])
        self.assertEqual(self.color1,self.array[1,0])




if __name__ == '__main__':
    unittest.main()