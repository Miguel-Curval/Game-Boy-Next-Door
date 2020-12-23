class Joypad:
    def __init__(self):
        pass
    def reset(self):
        self.P1 = 0xCF
        self.buttons = 0xF
        self.directions = 0xF

    def read_P1(self, address):
        return self.P1

    def write_P1(self, address, value):
        self.P1 = (self.P1 & 0xC0) | (value & 0x30)
        self.update_P1()

    def button_down(self, key):
        self.buttons &= ~key
        self.update_P1()
        self.mmu.IF |= 0x10

    def button_up(self, key):
        self.buttons |= key
        self.update_P1()

    def direction_down(self, key):
        self.directions &= ~key
        self.update_P1()
        self.mmu.IF |= 0x10

    def direction_up(self, key):
        self.directions |= key
        self.update_P1()

    def update_P1(self):
        self.P1 &= 0xF0
        if self.P1 & 0x10:
            self.P1 |= self.buttons
        if self.P1 & 0x20:
            self.P1 |= self.directions