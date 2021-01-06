from datetime import datetime

ROM_BANK_SIZE = 0x4000
RAM_BANK_SIZE = 0x2000

class Cartridge:
    def __init__(self, rom):
        self.title = "".join([chr(x) for x in rom[0x0134:0x0144] if x <= 127]).rstrip("\0")
        self.type = {
            0x00: (NoMBC   , False , False   , False) , # ROM
            0x01: (MBC1    , False , False   , False) , # MBC1
            0x02: (MBC1    , True  , False   , False) , # MBC1+RAM
            0x03: (MBC1    , True  , True    , False) , # MBC1+RAM+BATTERY
            0x05: (MBC2    , False , False   , False) , # MBC2
            0x06: (MBC2    , False , True    , False) , # MBC2+BATTERY
            0x08: (NoMBC   , True  , False   , False) , # ROM+RAM
            0x09: (NoMBC   , True  , True    , False) , # ROM+RAM+BATTERY
            0x0F: (MBC3    , False , True    , True ) , # MBC3+TIMER+BATTERY
            0x10: (MBC3    , True  , True    , True ) , # MBC3+TIMER+RAM+BATTERY
            0x11: (MBC3    , False , False   , False) , # MBC3
            0x12: (MBC3    , True  , False   , False) , # MBC3+RAM
            0x13: (MBC3    , True  , True    , False) , # MBC3+RAM+BATTERY
            0x19: (MBC5    , False , False   , False) , # MBC5
            0x1A: (MBC5    , True  , False   , False) , # MBC5+RAM
            0x1B: (MBC5    , True  , True    , False) , # MBC5+RAM+BATTERY
            0x1C: (MBC5    , False , False   , False) , # MBC5+RUMBLE
            0x1D: (MBC5    , True  , False   , False) , # MBC5+RUMBLE+RAM
            0x1E: (MBC5    , True  , True    , False) , # MBC5+RUMBLE+RAM+BATTERY
        }[rom[0x147]]
        self.has_RAM, self.has_battery, self.has_RTC = self.type[1:]

        self.ROM_bank_num = 2 << rom[0x148] if rom[0x148] <= 0x8 else {
            0x52: 72, 0x53: 80, 0x54: 96}[rom[0x148]]
        self.ROM_size = self.ROM_bank_num * ROM_BANK_SIZE

        self.RAM_size, self.RAM_bank_num = [
            (         0,  0),
            (  2 * 1024,  1),
            (  8 * 1024,  1),
            ( 32 * 1024,  4),
            (128 * 1024, 16),
            ( 64 * 1024,  8)
        ][rom[0x149]]

        self.ROM_banks = [rom[i:i + ROM_BANK_SIZE] for i in range(0, self.ROM_size, ROM_BANK_SIZE)]
        self.RAM_banks = [[0] * RAM_BANK_SIZE for i in range(self.RAM_bank_num)]

        self.MBC = self.type[0](self)
        self.reset()

    def reset(self):
        self.MBC.reset()
        

class MemoryBankController:
    def __init__(self, cartridge):
        self.ROM_banks = cartridge.ROM_banks
        self.ROM_bank_num = cartridge.ROM_bank_num
        self.RAM_banks = cartridge.RAM_banks
        self.RAM_bank_num = cartridge.RAM_bank_num
        self.has_battery = cartridge.has_battery
        self.has_RTC = cartridge.has_RTC
        self.has_RAM = cartridge.has_RAM
        self.RTC = RTC()
        self.reset()
    def reset(self):
        self.reset_RAM()
        self.RAMG = False
        self.ROM0_pointer = 0
        self.ROMB = 0x1
        self.RAMB = 0
        self.update_pointers()
    def reset_RAM(self):
        if self.has_RAM and not self.has_battery:
            for i in range(self.RAM_bank_num):
                self.RAM_banks[i][:] = [0] * RAM_BANK_SIZE
    def update_pointers(self):
        limit = self.ROM_bank_num - 1
        self.ROM0 = self.ROM_banks[self.ROM0_pointer & limit]
        self.ROMX = self.ROM_banks[self.ROMB & limit]   
        if self.has_RAM: self.RAM = self.RAM_banks[self.RAMB & (self.RAM_bank_num - 1)]

    def read_ROM0(self, address): return self.ROM0[address]
    def read_ROMX(self, address): return self.ROMX[address & 0x3FFF]
    def read_RAM(self, address): return self.RAM[address & 0x1FFF] if self.RAMG else 0xFF
    def write_RAM(self, address, value):
        if self.RAMG and self.has_RAM: self.RAM[address & 0x1FFF] = value

    def load_RAM(self, f):
        if self.has_battery:
            for i in range(self.RAM_bank_num):
                self.RAM_banks[i][:] = [int(i) for i in f.read(RAM_BANK_SIZE)]
    def save_RAM(self, f):
        if self.has_battery:
            for i in range(self.RAM_bank_num):
                f.write(bytearray(self.RAM_banks[i]))


class NoMBC(MemoryBankController):
    def read_RAM(self, address): return self.RAM[address & 0x1FFF]
    def write_RAM(self, address, value): self.RAM[address & 0x1FFF] = value
    def get_ROM_write_jump_table(self): return []

class MBC1(MemoryBankController):
    def reset(self):
        self.BANK1 = 0x1
        self.BANK2 = 0
        self.MODE = 0
        super().reset()
    def write_0000_1FFF(self, address, value): self.RAMG = value & 0xF == 0xA
    def write_2000_3FFF(self, address, value):
        value &= 0x1F
        self.BANK1 = value if value else 0x1
        self.update_pointers()
    def write_4000_5FFF(self, address, value):
        self.BANK2 = value & 0x3
        self.update_pointers()
    def write_6000_7FFF(self, address, value):
        self.MODE = value & 0x1
        self.update_pointers()
    def update_pointers(self):
        mode, bank2 = self.MODE, self.BANK2
        self.ROM0_pointer = bank2 << 5 if mode else 0
        self.ROMB = bank2 << 5 | self.BANK1
        self.RAMB = bank2 if mode else 0
        super().update_pointers()
    def get_ROM_write_jump_table(self): return [self.write_0000_1FFF] * 0x2000 + [self.write_2000_3FFF] * 0x2000 + [self.write_4000_5FFF] * 0x2000 + [self.write_6000_7FFF] * 0x2000

class MBC2(MemoryBankController):
    def reset_RAM(self):
        if not self.has_battery: self.RAM_banks = [[0xF0] * 512]
    def read_RAM(self, address): return self.RAM[address & 0x1FF] | 0xF0 if self.RAMG else 0xFF
    def write_0000_3FFF(self, address, value):
        value &= 0xF
        if address & 0x100:
            self.ROMB = value if value else 0x1
            self.update_pointers()
        else: self.RAMG = value == 0xA
    def write_RAM(self, address, value):
        if self.RAMG: self.RAM[address & 0x1FF] = value | 0xF0
    def get_ROM_write_jump_table(self): return [self.write_0000_3FFF] * 0x4000

    def load_RAM(self, f):
        if self.has_battery:
            self.RAM[:] = [int(i) for i in f.read(512)]
    def save_RAM(self, f):
        if self.has_battery:
            f.write(bytearray(self.RAM))

class MBC3(MemoryBankController):
    def write_0000_1FFF(self, address, value): self.RAMG = value == 0x0A
    def write_2000_3FFF(self, address, value):
        value &= 0x7F
        self.ROMB = value if value else 0x1
        self.update_pointers()
    def write_4000_5FFF(self, address, value):
        if value <= 0x3:
            self.RTC.set_active_register(False)
            self.RAMB = value
            self.update_pointers()
        elif 0x8 <= value <= 0xC:
            self.RTC.set_active_register(value)
    def read_RAM(self, address):
        return (self.RTC.read_active_register() if self.RTC.active_register else self.RAM[address & 0x1FFF]) if self.RAMG else 0xFF
    def get_ROM_write_jump_table(self): return [self.write_0000_1FFF] * 0x2000 + [self.write_2000_3FFF] * 0x2000 + [self.write_4000_5FFF] * 0x2000 # + [self.write_6000_7FFF] * 0x2000 

class MBC5(MemoryBankController):
    def write_0000_1FFF(self, address, value): self.RAMG = value == 0x0A
    def write_2000_2FFF(self, address, value):
        self.ROMB = self.ROMB & 0x100 | value
        self.update_pointers()
    def write_3000_3FFF(self, address, value):
        self.ROMB = value << 8 | self.ROMB & 0xFF
        self.update_pointers()
    def write_4000_5FFF(self, address, value):
        self.RAMB = value & 0xF
        self.update_pointers()
    def get_ROM_write_jump_table(self): return [self.write_0000_1FFF] * 0x2000 + [self.write_2000_2FFF] * 0x1000 + [self.write_3000_3FFF] * 0x1000 + [self.write_4000_5FFF] * 0x2000

class RTC:
    def __init__(self):
        self.reset()
    def reset(self):
        self.set_active_register(0)
    def set_active_register(self, value):
        self.active_register = value
    def read_active_register(self):
        current = datetime.today()
        return {0:0, 0x8:current.second, 0x9:current.minute, 0xA:current.hour, 0xB:current.day & 0xFF, 0xC:current.day > 0xFF}[self.active_register]