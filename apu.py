class APU:
    def __init__(self):
        self.NR50 = 0 # ? No idea
    def read_NR50(self, address): return self.NR50
    def write_NR50(self, address, value): self.NR50 = value
    def read_unimplemented(self, address): return 0xFF
    def write_unimplemented(self, address, value): pass