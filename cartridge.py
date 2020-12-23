ROM_BANK_SIZE = 0x4000

class Cartridge:
    def __init__(self, rom):
        self.type = {
            0x00: "ROM ONLY",
            0x01: "MBC1",
            0x02: "MBC1+RAM",
            0x03: "MBC1+RAM+BATTERY",
            0x05: "MBC2",
            0x06: "MBC2+BATTERY",
            0x08: "ROM+RAM",
            0x09: "ROM+RAM+BATTERY",
            0x0B: "MMM01",
            0x0C: "MMM01+RAM",
            0x0D: "MMM01+RAM+BATTERY",
            0x0F: "MBC3+TIMER+BATTERY",
            0x10: "MBC3+TIMER+RAM+BATTERY",
            0x11: "MBC3",
            0x12: "MBC3+RAM",
            0x13: "MBC3+RAM+BATTERY",
            0x19: "MBC5",
            0x1A: "MBC5+RAM",
            0x1B: "MBC5+RAM+BATTERY",
            0x1C: "MBC5+RUMBLE",
            0x1D: "MBC5+RUMBLE+RAM",
            0x1E: "MBC5+RUMBLE+RAM+BATTERY",
            0x20: "MBC6",
            0x22: "MBC7+SENSOR+RUMBLE+RAM+BATTERY",
            0xFC: "POCKET CAMERA",
            0xFD: "BANDAI TAMA5",
            0xFE: "HuC3",
            0xFF: "HuC1+RAM+BATTERY",
        }[rom[0x147]]
        self.rom_bank_num = 2 << rom[0x148] if rom[0x148] <= 0x8 else {
            0x52: 72, 0x53: 80, 0x54: 96}[rom[0x148]]
        self.rom_size = self.rom_bank_num * ROM_BANK_SIZE
        self.ram_bank_size, self.ram_bank_num = [
            (         0,  0),
            (  2 * 1024,  1),
            (  8 * 1024,  1),
            ( 32 * 1024,  4),
            (128 * 1024, 16),
            ( 64 * 1024,  8)
        ][rom[0x149]]
        self.ram_size = self.ram_bank_size * self.ram_bank_num
        self.rom_banks = [rom[:ROM_BANK_SIZE], rom[ROM_BANK_SIZE:ROM_BANK_SIZE + ROM_BANK_SIZE]]
        self.ROM0 = self.rom_banks[0]
        self.reset()

    def reset(self, skip_bootrom=False):
        self.ROMX = self.rom_banks[1]
        
    def read_ROM0(self, address): return self.ROM0[address]
    def read_ROMX(self, address): return self.ROMX[address - 0x4000]
    def read_RAM(self, address): pass
    
    def write_ROM0(self, address, value): pass
    def write_ROMX(self, address, value): pass
    def write_RAM(self, address, value): pass
    
    def write_external_RAM(self, address, value):
        pass







