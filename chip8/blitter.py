def blit_screen(state,color1,color2,outArray):
    for y in range(0x20):
        for x in range(0x00,0x40,0x08):
            index = (y << 3) + (x >> 3) + state.screen_buffer_start
            byte = state.memory[index]
            for i in range(0x08):
                outArray[x+i,y]=color1 if (byte & (0x80 >> i)) == 0 else color2