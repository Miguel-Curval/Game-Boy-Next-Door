class MMU:
    def __init__(self, bootrom, cartridge, timer, ppu, apu, joypad):
        ppu.mmu = self
        self.timer = timer
        self.ppu = ppu
        self.apu = apu
        self.joypad = joypad
        self.cartridge = cartridge
        self.BOOTROM = [b for b in bootrom]
        self.WRAM = [0] * 0x2000
        self.HRAM = [0] * 0x80
        read_jt = [self.invalid_read] * 0x10000
        read_jt[:0x8000] = [self.cartridge.MBC.read_ROM0] * 0x4000 + [self.cartridge.MBC.read_ROMX] * 0x4000
        read_jt[0x8000:0xA000] = [self.ppu.read_VRAM] * 0x2000
        read_jt[0xA000:0xC000] = [self.cartridge.MBC.read_RAM] * 0x2000
        read_jt[0xC000:0xE000] = [self.read_WRAM] * 0x2000
        read_jt[0xE000:0xFE00] = [self.read_ECHO] * 0x1E00
        read_jt[0xFE00:0xFEA0] = [self.ppu.read_OAM] * 0xA0
        read_jt[0xFF00] = self.joypad.read_P1
        read_jt[0xFF04] = self.timer.read_DIV
        read_jt[0xFF05] = self.timer.read_TIMA
        read_jt[0xFF06] = self.timer.read_TMA
        read_jt[0xFF07] = self.timer.read_TAC
        read_jt[0xFF0F] = self.read_IF
        read_jt[0xFF10:0xFF27] = [self.apu.read_unimplemented] * 0x17
        read_jt[0xFF30:0xFF40] = [self.apu.read_unimplemented] * 0x10
        read_jt[0xFF24] = self.apu.read_NR50
        read_jt[0xFF40] = self.ppu.read_LCDC
        read_jt[0xFF41] = self.ppu.read_STAT
        read_jt[0xFF42] = self.ppu.read_SCY
        read_jt[0xFF43] = self.ppu.read_SCX
        read_jt[0xFF44] = self.ppu.read_LY
        read_jt[0xFF45] = self.ppu.read_LYC
        read_jt[0xFF46] = self.ppu.read_DMA
        read_jt[0xFF47] = self.ppu.read_BGP
        read_jt[0xFF48] = self.ppu.read_OBP0
        read_jt[0xFF49] = self.ppu.read_OBP1
        read_jt[0xFF4A] = self.ppu.read_WY
        read_jt[0xFF4B] = self.ppu.read_WX
        read_jt[0xFF50] = self.read_BOOT
        read_jt[0xFF80:0xFFFF] = [self.read_HRAM] * 0x7F
        read_jt[0xFFFF] = self.read_IE
        self.READ_JUMP_TABLE = read_jt
        write_jt = [self.invalid_write] * 0x10000
        rom_write_jt = cartridge.MBC.get_ROM_write_jump_table()
        write_jt[:len(rom_write_jt)] = rom_write_jt
        write_jt[0x8000:0xA000] = [self.ppu.write_VRAM] * 0x2000
        write_jt[0xA000:0xC000] = [self.cartridge.MBC.write_RAM] * 0x2000
        write_jt[0xC000:0xE000] = [self.write_WRAM] * 0x2000
        write_jt[0xE000:0xFE00] = [self.write_ECHO] * 0x1E00
        write_jt[0xFE00:0xFEA0] = [self.ppu.write_OAM] * 0xA0
        write_jt[0xFF00] = self.joypad.write_P1
        write_jt[0xFF04] = self.timer.write_DIV
        write_jt[0xFF05] = self.timer.write_TIMA
        write_jt[0xFF06] = self.timer.write_TMA
        write_jt[0xFF07] = self.timer.write_TAC
        write_jt[0xFF0F] = self.write_IF
        write_jt[0xFF10:0xFF27] = [self.apu.write_unimplemented] * 0x17
        write_jt[0xFF30:0xFF40] = [self.apu.write_unimplemented] * 0x10
        write_jt[0xFF24] = self.apu.write_NR50
        write_jt[0xFF40] = self.ppu.write_LCDC
        write_jt[0xFF41] = self.ppu.write_STAT
        write_jt[0xFF42] = self.ppu.write_SCY
        write_jt[0xFF43] = self.ppu.write_SCX
        write_jt[0xFF44] = self.ppu.write_LY
        write_jt[0xFF45] = self.ppu.write_LYC
        write_jt[0xFF46] = self.ppu.write_DMA
        write_jt[0xFF47] = self.ppu.write_BGP
        write_jt[0xFF48] = self.ppu.write_OBP0
        write_jt[0xFF49] = self.ppu.write_OBP1
        write_jt[0xFF4A] = self.ppu.write_WY
        write_jt[0xFF4B] = self.ppu.write_WX
        write_jt[0xFF50] = self.write_BOOT
        write_jt[0xFF80:0xFFFF] = [self.write_HRAM] * 0x7F
        write_jt[0xFFFF] = self.write_IE
        self.WRITE_JUMP_TABLE = write_jt
        self.reset()

    def reset(self, skip_bootrom=False):
        self.WRAM[:] = [0] * 0x2000
        self.HRAM[:] = [0] * 0x80
        self.BOOT_OFF = 0
        self.IF, self.IE = 0, 0
        if skip_bootrom:
            self.BOOT_OFF = 1
            self.IF = 1
        else:
            self.READ_JUMP_TABLE[:0x100] = [self.read_BOOTROM] * 0x100
        
        
    def read(self, address):
        a = self.READ_JUMP_TABLE[address](address)
        self.last_read = a
        self.last_read_address = address
        return a
    def write(self, address, value): self.WRITE_JUMP_TABLE[address](address, value)

    def read_BOOTROM(self, address): return self.BOOTROM[address]
    def read_WRAM(self, address): return self.WRAM[address - 0xC000]
    def read_ECHO(self, address): return self.read(address - 0x2000)
    def read_IF(self, address): return self.IF & 0x1F # JUST FOR TESTS, TODO: what the hell is this, research and fix
    def read_BOOT(self, address): return 0xFF
    def read_HRAM(self, address): return self.HRAM[address - 0xFF80]
    def read_IE(self, address): return self.IE
    def invalid_read(self, address):
        print(f'Reading unimplemented address: {hex(address)}')
        return 0xFF
    
    def write_WRAM(self, address, value): self.WRAM[address - 0xC000] = value
    def write_ECHO(self, address, value): self.write(address - 0x2000, value)
    def write_IF(self, address, value): self.IF = value | 0xE0
    def write_BOOT(self, address, value):
        self.BOOT_OFF = True
        self.READ_JUMP_TABLE[:0x100] = [self.cartridge.MBC.read_ROM0] * 0x100
    def write_HRAM(self, address, value): self.HRAM[address - 0xFF80] = value
    def write_IE(self, address, value): self.IE = value
    def invalid_write(self, address, value):
        if address == 0xff01:
            self.test_char = chr(value)
        elif address == 0xff02 and value == 0x81:
            print(self.test_char, end='')
            self.test_char = 0
        else:
            print(f'Writing unimplemented address: {hex(address)}')
