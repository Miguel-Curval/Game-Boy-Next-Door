from helpers import BIT0, BIT1, BIT2, BIT3, BIT4, BIT5, BIT6, BIT7, BITX, INT8
from helpers import RES2, RES3, RES4, RES5, RES6
from helpers import SET2, SET3, SET4, SET5, SET6
from helpers import BITS1_0

HBLANK, VBLANK, OAM_SEARCH, PIXEL_TRANSFER, = list(range(4))

CLK_PER_HBLANK = 200            # Mode 0
CLK_PER_VBLANK = 456            # Mode 1
CLK_PER_OAM_SEARCH = 84         # Mode 2
CLK_PER_PIXEL_TRANSFER = 172    # Mode 3
SCROLL_ADJUST = [0, 1, 1, 1, 1, 2, 2, 2]

PALETTE_LOOKUP = [[(palette >> (color_value << 1)) & 0x3 for palette in range(256)] for color_value in range(4)]

class PPU:
    def __init__(self):
        #self.cycles = 0

        self.VRAM = [0] * 0x2000
        self.OAM  = [0] * 0x2000
        
    def reset(self, skip_bootrom=0):
        self.cycles = CLK_PER_OAM_SEARCH
        self.VRAM[:] = [0] * 0x2000
        self.OAM[:] = [0] * 0x2000
        self.LCD_EN  , self.BG_EN , self.WIN_EN , self.OBJ_EN   = 0, 0, 0, 0
        self.TILE_SEL, self.BG_MAP, self.WIN_MAP, self.OBJ_SIZE = 0, 0, 0, 0
        self.LCD_MODE = skip_bootrom
        self.LYC_STAT = skip_bootrom
        self.INTR_M0, self.INTR_M1, self.INTR_M2, self.INTR_LYC = 0, 0, 0, 0
        self.SCY, self.SCX = 0, 0
        self.LY, self.LYC = 0, 0
        self.DMA = 0
        self.BGP = 0
        self.OBP0, self.OBP1 = 0, 0
        self.WY, self.WX = 0, 0
        self.framebuffer = [0x3] * 160 * 144
        self.new_frame = False
        self.tiles = [[[0] * 8 for i in range(8)] for i in range(384)]
        if skip_bootrom:
            self.cycles = 56 # TODO check this, BGB says 28, in BGB 1 cnt is 2 clocks
            self.LCD_EN, self.BG_EN = 1, 1
            self.TILE_SEL = 1
            self.LCD_MODE = 0x1
            self.LYC_STAT = 1
            self.DMA = 0xFF
            self.BGP = 0xFC
            self.OBP0, self.OBP1 = 0xFF, 0xFF

    def read_VRAM(self, address): return 0xFF if self.LCD_MODE == PIXEL_TRANSFER else self.VRAM[address - 0x8000]
    def read_OAM(self, address): return 0xFF if self.LCD_MODE >= OAM_SEARCH else self.OAM[address - 0xFE00]
    def read_LCDC(self, address): return self.LCD_EN << 7 | self.WIN_MAP << 6 | self.WIN_EN << 5 | self.TILE_SEL << 4 | self.BG_MAP << 3 | self.OBJ_SIZE << 2 | self.OBJ_EN << 1 | self.BG_EN
    def read_STAT(self, address): return 0x80 | self.INTR_LYC << 6 | self.INTR_M2 << 5 | self.INTR_M1 << 4 | self.INTR_M0 << 3 | self.LYC_STAT << 2 | self.LCD_MODE if self.LCD_EN else 0x80
    def read_SCY(self, address): return self.SCY
    def read_SCX(self, address): return self.SCX
    def read_LY(self, address): return self.LY
    def read_LYC(self, address): return self.LYC
    def read_DMA(self, address): return self.DMA
    def read_BGP(self, address): return self.BGP
    def read_OBP0(self, address): return self.OBP0
    def read_OBP1(self, address): return self.OBP1
    def read_WY(self, address): return self.WY
    def read_WX(self, address): return self.WX
    
    def write_VRAM(self, address, value):
        if self.LCD_MODE == PIXEL_TRANSFER: return 
        address -= 0x8000
        self.VRAM[address] = value
        if address < 0x1800:
            first_byte_address = address & 0xFFFE
            byte1, byte2 = self.VRAM[first_byte_address : first_byte_address + 2]
            self.tiles[address // 16][(address % 16) // 2][:] = [BITX[7 - px_i][byte2] << 1 | BITX[7 - px_i][byte1] for px_i in range(8)]
        elif address < 0x1C00:
            pass
        else:
            pass

    def write_OAM(self, address, value):
        if self.LCD_MODE >= OAM_SEARCH: return
        address -= 0xFE00
        self.OAM[address] = value


    def write_LCDC(self, address, value):
        new_lcd_en = BIT7[value]
        if not new_lcd_en and self.LCD_EN:
            self.LY = 0
        if new_lcd_en and not self.LCD_EN:
            self.LCD_MODE = HBLANK
            self.cycles = CLK_PER_OAM_SEARCH
            self.LYC_STAT = 1
        self.LCD_EN, self.WIN_MAP, self.WIN_EN, self.TILE_SEL, self.BG_MAP, self.OBJ_SIZE, self.OBJ_EN, self.BG_EN = BIT7[value], BIT6[value], BIT5[value], BIT4[value], BIT3[value], BIT2[value], BIT1[value], BIT0[value]
    def write_STAT(self, address, value): self.INTR_LYC, self.INTR_M2, self.INTR_M1, self.INTR_M0 = BIT6[value], BIT5[value], BIT4[value], BIT3[value]
    def write_SCY(self, address, value): self.SCY = value
    def write_SCX(self, address, value): self.SCX = value
    def write_LY(self, address, value): self.LY = value
    def write_LYC(self, address, value): self.LYC = value
    def write_DMA(self, address, value): self.DMA = value
    def write_BGP(self, address, value): self.BGP = value
    def write_OBP0(self, address, value): self.OBP0 = value
    def write_OBP1(self, address, value): self.OBP1 = value
    def write_WY(self, address, value): self.WY = value
    def write_WX(self, address, value): self.WX = value

    def tick(self):
        if self.LCD_EN:
            self.cycles -= 4
            if self.cycles == 4 and self.LCD_MODE == PIXEL_TRANSFER:
                if self.INTR_M0:
                    self.mmu.IF |= 0x2

            if self.cycles > 0: return
            mode = self.LCD_MODE
            if mode == HBLANK:
                self.LY += 1
                if self.LY < 144:
                    self.LCD_MODE = OAM_SEARCH
                    self.cycles += CLK_PER_OAM_SEARCH
                    if self.INTR_M2:
                        self.mmu.IF |= 0x2
                else:
                    self.LCD_MODE = VBLANK
                    self.cycles += CLK_PER_VBLANK
                    self.mmu.IF |= 0x1
                    if self.INTR_M1:
                        self.mmu.IF |= 0x2
                    if self.INTR_M2:
                        self.mmu.IF |= 0x2
                self.check_compare_interrupt()
            elif mode == PIXEL_TRANSFER:
                self.draw_line()
                self.LCD_MODE = HBLANK
                self.cycles += CLK_PER_HBLANK #- SCROLL_ADJUST[self.SCX % 8]
            elif mode == OAM_SEARCH:
                self.LCD_MODE = PIXEL_TRANSFER
                self.cycles += CLK_PER_PIXEL_TRANSFER #+ SCROLL_ADJUST[self.SCX % 8]
            elif mode == VBLANK:
                self.LY += 1
                if self.LY > 153:
                    if self.OBJ_EN:
                        self.draw_sprites()
                    self.new_frame = True
                    self.LY = 0
                    self.LCD_MODE = OAM_SEARCH
                    self.cycles += CLK_PER_OAM_SEARCH
                    if self.INTR_M2:
                        self.mmu.IF |= 0x2
                else:
                    self.cycles += CLK_PER_VBLANK
                self.check_compare_interrupt()

    def check_compare_interrupt(self):
        if self.LY != self.LYC:
            self.LYC_STAT = 0
        else:
            self.LYC_STAT = 1
            if self.INTR_LYC:
                self.mmu.IF |= 0x2

    def draw_line(self):
        ly, wy, scx = self.LY, self.WY, self.SCX
        tiles, vram = self.tiles, self.VRAM
        palette = self.BGP
        buffer_index_start = 160 * ly
        tiles_not_overlapped = not self.TILE_SEL
        if self.BG_EN:
            bg_y = (ly + self.SCY) & 0xFF
            tile_set_row = bg_y // 8
            tile_set_row_address = (tile_set_row  * 32) | (0x1C00 if self.BG_MAP else 0x1800)
            tile_y = bg_y % 8
            for i in range(160):
                bg_x = (i + scx) & 0xFF
                tile_index = vram[bg_x // 8 | tile_set_row_address]
                if tiles_not_overlapped:
                    tile_index = 256 + INT8[tile_index]
                color_value = tiles[tile_index][tile_y][bg_x % 8]
                raw_color = PALETTE_LOOKUP[color_value][palette]
                self.framebuffer[buffer_index_start + i] = raw_color
        if self.WIN_EN and wy <= ly:
            win_x_start = (self.WX - 7) & 0xFF
            win_y = ly - wy
            tile_set_row = y // 8
            tile_set_row_address = (tile_set_row  * 32) | (0x1C00 if self.WIN_MAP else 0x1800)
            tile_y = y % 8
            for x in range(win_x_start, 160):
                win_x = (x + scx) & 0xFF
                if win_x >= win_x_start:
                    win_x = x - win_x_start
                tile_index = vram[win_x // 8 | tile_set_row_address]
                if tiles_not_overlapped:
                    tile_index = 256 + INT8[tile_index]
                color_value = tiles[tile_index][tile_y][win_x % 8]
                raw_color = PALETTE_LOOKUP[color_value][palette]
                self.framebuffer[buffer_index_start + x] = raw_color
                

    def draw_sprites(self):
        obj_height = 16 if self.OBJ_SIZE else 8
        for i in range(0, 0xA0, 4):
            obj_y, obj_x, tile_index, obj_attrs = self.OAM[i:i+4]
            flip_x, flip_y = BIT5[obj_attrs], BIT6[obj_attrs]
            has_priority = not BIT7[obj_attrs]
            palette = self.OBP1 if BIT4[obj_attrs] else self.OBP0
            start_x, start_y = obj_x - 8, obj_y - 16
            for y in range(obj_height):
                screen_y = start_y + y
                if 0 <= screen_y < HEIGHT:
                    tile_y = obj_height - y - 1 if flip_y else y
                    y_index = screen_y * 160
                    for x in range(8):
                        tile_x = 7 - x if flip_x else x
                        color_value = self.tiles[tile_index][tile_y][tile_x]
                        if color_value:
                            screen_x = start_x + x
                            if screen_x < 160:
                                index = y_index + screen_x
                                if has_priority or not self.framebuffer[index]:
                                    raw_color = PALETTE_LOOKUP[color_value][palette]
                                    if raw_color != self.framebuffer[index]:
                                        self.framebuffer[index] = raw_color
                                        

