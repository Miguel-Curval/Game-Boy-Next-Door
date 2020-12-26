class APU:
    def __init__(self):
        self.WAV = [None] * 0x10
        self.reset(False)

    def reset(self, skip_bootrom):
        self.NR10, self.NR11, self.NR12, self.NR13, self.NR14 = (0,) * 5
        _________, self.NR21, self.NR22, self.NR23, self.NR24 = (0,) * 5
        self.NR30, self.NR31, self.NR32, self.NR33, self.NR34 = (0,) * 5
        _________, self.NR41, self.NR42, self.NR43, self.NR44 = (0,) * 5
        self.NR50, self.NR51, self.NR52, _________, _________ = (0,) * 5
        self.WAV[:] = [0] * 0x10
    def read_NR10(self, address): return self.NR10
    def read_NR11(self, address): return self.NR11
    def read_NR12(self, address): return self.NR12
    def read_NR13(self, address): return self.NR13
    def read_NR14(self, address): return self.NR14
    def read_NR21(self, address): return self.NR21
    def read_NR22(self, address): return self.NR22
    def read_NR23(self, address): return self.NR23
    def read_NR24(self, address): return self.NR24
    def read_NR30(self, address): return self.NR30
    def read_NR31(self, address): return self.NR31
    def read_NR32(self, address): return self.NR32
    def read_NR33(self, address): return self.NR33
    def read_NR34(self, address): return self.NR34
    def read_NR41(self, address): return self.NR41
    def read_NR42(self, address): return self.NR42
    def read_NR43(self, address): return self.NR43
    def read_NR44(self, address): return self.NR44
    def read_NR50(self, address): return self.NR50
    def read_NR51(self, address): return self.NR51
    def read_NR52(self, address): return self.NR52
    def read_WAV(self, address): return self.WAV[address - 0xFF30]
    def read_ignr(self, address): return 0xFF
    def write_NR10(self, address, value): self.NR10 = value
    def write_NR11(self, address, value): self.NR11 = value
    def write_NR12(self, address, value): self.NR12 = value
    def write_NR13(self, address, value): self.NR13 = value
    def write_NR14(self, address, value): self.NR14 = value
    def write_NR21(self, address, value): self.NR21 = value
    def write_NR22(self, address, value): self.NR22 = value
    def write_NR23(self, address, value): self.NR23 = value
    def write_NR24(self, address, value): self.NR24 = value
    def write_NR30(self, address, value): self.NR30 = value
    def write_NR31(self, address, value): self.NR31 = value
    def write_NR32(self, address, value): self.NR32 = value
    def write_NR33(self, address, value): self.NR33 = value
    def write_NR34(self, address, value): self.NR34 = value
    def write_NR41(self, address, value): self.NR41 = value
    def write_NR42(self, address, value): self.NR42 = value
    def write_NR43(self, address, value): self.NR43 = value
    def write_NR44(self, address, value): self.NR44 = value
    def write_NR50(self, address, value): self.NR50 = value
    def write_NR51(self, address, value): self.NR51 = value
    def write_NR52(self, address, value): self.NR52 = value
    def write_WAV(self, address, value): self.WAV[address - 0xFF30] = value
    def write_ignr(self, address, value): pass