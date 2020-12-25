from opcodes import OPCODES, OPCODES_CB, CYCLES, CYCLES_BRANCHED, CYCLES_CB

INTERRUPT_JUMP_VECTORS = [0x40, 0x48, 0x50, 0x58, 0x60]

def dec16(uint16): return (uint16 - 1) & 0xFFFF
def inc16(uint16): return (uint16 + 1) & 0xFFFF

class CPU:
    def __init__(self, mmu):
        self.mmu = mmu
        self.reset()

    def reset(self, skip_bootrom=False):
        self.A, self.F = 0, 0
        self.B, self.C = 0, 0
        self.D, self.E = 0, 0
        self.H, self.L = 0, 0
        self.PC, self.SP = 0, 0
        self.IME, self.IME_scheduled = 0, 0
        self.halted, self.halt_bug = 0, 0
        self.branched = 0
        if skip_bootrom:
            self.A, self.F = 0x01, 0xB0
            ______, self.C = None, 0x13
            ______, self.E = None, 0xD8
            self.H, self.L = 0x01, 0x4D
            self.SP, self.PC = 0xFFFE, 0x0100
        
    def get_AF(self): return self.A << 8 | (self.F & 0xF0)
    def get_BC(self): return self.B << 8 | self.C
    def get_DE(self): return self.D << 8 | self.E
    def get_HL(self): return self.H << 8 | self.L
    def set_AF(self, value): self.A, self.F = value >> 8, value & 0xF0
    def set_BC(self, value): self.B, self.C = value >> 8, value & 0xFF
    def set_DE(self, value): self.D, self.E = value >> 8, value & 0xFF
    def set_HL(self, value): self.H, self.L = value >> 8, value & 0xFF

    def set_ZF(self, boolean): self.F = self.F | 0x80 if boolean else self.F & 0x70
    def set_NF(self, boolean): self.F = self.F | 0x40 if boolean else self.F & 0xB0
    def set_HF(self, boolean): self.F = self.F | 0x20 if boolean else self.F & 0xD0
    def set_CF(self, boolean): self.F = self.F | 0x10 if boolean else self.F & 0xE0

    def dec_BC(self): self.set_BC(dec16(self.get_BC()))
    def dec_DE(self): self.set_DE(dec16(self.get_DE()))
    def dec_HL(self): self.set_HL(dec16(self.get_HL()))
    def dec_SP(self): self.SP = dec16(self.SP)
    def inc_BC(self): self.set_BC(inc16(self.get_BC()))
    def inc_DE(self): self.set_DE(inc16(self.get_DE()))
    def inc_HL(self): self.set_HL(inc16(self.get_HL()))
    def inc_SP(self): self.SP = inc16(self.SP)
    def inc_PC(self): self.PC = inc16(self.PC)
        
    def read_BC(self): return self.mmu.read(self.get_BC())
    def read_DE(self): return self.mmu.read(self.get_DE())
    def read_HL(self): return self.mmu.read(self.get_HL())
    def read_a16(self): return self.mmu.read(self.fetch_imm16())
    def write_BC(self, value): self.mmu.write(self.get_BC(), value)
    def write_DE(self, value): self.mmu.write(self.get_DE(), value)
    def write_HL(self, value): self.mmu.write(self.get_HL(), value)
    def write_a16(self, value): self.mmu.write(self.fetch_imm16(), value)
    
    def read_mmio(self, address_low): return self.mmu.read(address_low | 0xFF00)    
    def write_mmio(self, address_low, value): self.mmu.write(address_low | 0xFF00, value)
    
        
    def tick(self):
        if self.halted:
            return 4
        if self.IME_scheduled:
            self.IME, self.IME_scheduled = True, False
        opcode = self.fetch_imm8()
        if self.halt_bug:
            self.halt_bug = False
            self.PC = dec16(self.PC)
        cycles = self.exec_opcode(opcode)
        return cycles

    def fetch_imm8(self):
        data = self.mmu.read(self.PC)
        self.PC = inc16(self.PC)
        return data
    def fetch_imm16(self): return self.fetch_imm8() | (self.fetch_imm8() << 8)
        
    def push(self, address):
        self.dec_SP()
        self.mmu.write(self.SP, address >> 8)
        self.dec_SP()
        self.mmu.write(self.SP, address & 0xFF)
    def pop(self):
        data = self.mmu.read(self.SP)
        self.inc_SP()
        data |= self.mmu.read(self.SP) << 8
        self.inc_SP()
        return data
    
    def call(self, address):
        self.push(self.PC)
        self.PC = address

    def exec_opcode(self, opcode):
        if opcode == 0xCB:
            opcode = self.fetch_imm8()
            OPCODES_CB[opcode](self)
            return CYCLES_CB[opcode]
        OPCODES[opcode](self)
        if self.branched:
            self.branched = False
            return CYCLES_BRANCHED[opcode]
        return CYCLES[opcode]

    def handle_interrupts(self):
        mmu = self.mmu
        interrupt_flags = mmu.IF
        irqs = mmu.IE & interrupt_flags & 0x1F
        if irqs:
            self.halted = False
            if self.IME:
                for i in range(5):
                    bit = 1 << i
                    if irqs & bit:
                        self.IME = False
                        self.call(INTERRUPT_JUMP_VECTORS[i])
                        interrupt_flags &= (bit ^ 0xFF)
                mmu.IF = interrupt_flags
                