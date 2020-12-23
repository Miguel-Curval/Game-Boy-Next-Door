from helpers import BIT2

TIMA_RUNNING, TIMA_RELOADING, TIMA_RELOADED = list(range(3))
TAC_TRIGGER_BITS = [0x200, 0x8, 0x20, 0x80]

class Timer:
    def __init__(self):
        self.reset()

    def reset(self, skip_bootrom=False):
        self.counter = 0
        self.TIMA, self.TIMA_overflow, self.TIMA_loading = 0, 0, 0
        self.TMA = 0
        self.TAC_EN, self.TACK_CLK = 0, 0
        if skip_bootrom:
            self.counter = 0xABCC

        
    def read_DIV(self, address): return self.counter >> 8
    def read_TIMA(self, address): return self.TIMA
    def read_TMA(self, address): return self.TMA
    def read_TAC(self, address): return 0xF8 | (self.TAC_EN << 2) | self.TAC_CLK

    def write_DIV(self, address, value):
        old_trigger_bit = self.get_inc_TIMA_trigger_bit()
        self.counter = 0
        if old_trigger_bit: self.check_glitch()
    def write_TIMA(self, address, value):
        if not self.TIMA_loading:
            self.TIMA, self.TIMA_overflow = value, False
    def write_TMA(self, address, value):
        self.TMA = value
        if self.TIMA_loading:
            self.TIMA = value
    def write_TAC(self, address, value):
        old_trigger_bit = self.get_inc_TIMA_trigger_bit()
        self.TAC_EN, self.TAC_CLK = BIT2[value], value & 0x3
        if old_trigger_bit: self.check_glitch()

    def inc_DIV(self): self.counter = (self.counter + 4) & 0xFFFF        
    def inc_TIMA(self): self.TIMA, self.TIMA_overflow = (0, True) if self.TIMA == 0xFF else (self.TIMA + 1, False)

    def tick(self):
        if self.TIMA_overflow:
            self.mmu.IF |= 0x4
            self.TIMA, self.TIMA_overflow, self.TIMA_loading = self.TMA, False, True
        else: self.TIMA_loading = False
        old_trigger_bit = self.get_inc_TIMA_trigger_bit()
        self.inc_DIV()
        if old_trigger_bit: self.check_glitch()

    def check_glitch(self):
        if not self.get_inc_TIMA_trigger_bit(): self.inc_TIMA()

    def get_inc_TIMA_trigger_bit(self): return self.TAC_EN and self.counter & TAC_TRIGGER_BITS[self.TAC_CLK]



