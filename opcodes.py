from helpers import BITX, BIT0, BIT7, INT8
from helpers import RES0, RES1, RES2, RES3, RES4, RES5, RES6, RES7
from helpers import SET0, SET1, SET2, SET3, SET4, SET5, SET6, SET7

F_LUT_00FF = [i & 0x30 for i in range(256)]
F_LUT_0FFF = [i & 0x70 for i in range(256)]
F_LUT_F001 = [i & 0x80 | 0x10 for i in range(256)]
F_LUT_F000 = [i & 0x80 for i in range(256)]
F_LUT_F00F = [i & 0x90 for i in range(256)]
F_LUT_F00I = [i & 0x90 ^ 0x10 for i in range(256)]
F_LUT_F010 = [i & 0x80 | 0x20 for i in range(256)]
F_LUT_F01F = [i & 0x90 | 0x20 for i in range(256)]
F_LUT_F0FF = [i & 0xB0 for i in range(256)]
F_LUT_F11F = [i & 0xF0 | 0x60 for i in range(256)]
F_LUT_F1FF = [i & 0xB0 | 0x40 for i in range(256)]
F_LUT_FF0F = [i & 0xD0 for i in range(256)]
ZF, NF, HF, CF = BITX[::-1][:4]
NZF, NCF = [1 if not i else 0 for i in ZF], [1 if not i else 0 for i in CF]

def invalid_opcode(cpu): print(f'INVALID OPCODE: {cpu.PC - 1}')

def ADD_HL_16(cpu, x):
    hl = cpu.get_HL()
    res = hl + x
    cpu.set_CF(res > 0xFFFF)
    cpu.set_HF((hl & 0xFFF) + (x & 0xFFF) > 0xFFF)
    cpu.F = F_LUT_F0FF[cpu.F]
    cpu.set_HL(res & 0xFFFF)
def add_SP_i8(cpu):  
    sp = cpu.SP
    data = cpu.fetch_imm8()
    cpu.set_CF((sp & 0xFF) + data > 0xFF)
    cpu.set_HF((sp & 0xF) + (data & 0xF) > 0xF)
    cpu.F = F_LUT_00FF[cpu.F]
    return (sp + INT8[data]) & 0xFFFF
def jp_cc(cpu, condition, func):
    if condition:
        cpu.branched = True
        func(cpu)
    else:
        if func != RET:
            cpu.fetch_imm8()
            if func != JR_i8:
                cpu.fetch_imm8()
        
def CALL_cc_a16(cpu, condition): jp_cc(cpu, condition, CALL_a16)
def JP_cc_a16(cpu, condition): jp_cc(cpu, condition, JP_a16)
def JR_cc_i8(cpu, condition): jp_cc(cpu, condition, JR_i8)
def RET_cc(cpu, condition): jp_cc(cpu, condition, RET)

def ADC(cpu, x, carry):
    a = cpu.A
    res = a + x + carry
    cpu.set_CF(res > 0xFF)
    cpu.set_HF((a & 0xF) + (x & 0xF) + carry > 0xF)
    cpu.F = F_LUT_F0FF[cpu.F]
    cpu.set_ZF((res & 0xFF) == 0)
    cpu.A = res & 0xFF
def ADD(cpu, x): ADC(cpu, x, 0)
def AND(cpu, x):
    cpu.A &= x
    cpu.F = F_LUT_F010[cpu.F]
    cpu.set_ZF(cpu.A == 0)
def BIT(cpu, index, x):
    cpu.F = F_LUT_F01F[cpu.F]
    cpu.set_ZF(BITX[index][x] == 0)
def CP(cpu, x):
    a = cpu.A
    cpu.set_CF(a < x)
    cpu.set_HF((a & 0xF) < (x & 0xF))
    cpu.set_NF(1)
    cpu.set_ZF(a == x)
def DEC(cpu, x):
    res = (x - 1) & 0xFF
    cpu.set_ZF(res == 0)
    cpu.set_NF(1)
    cpu.set_HF((res & 0xF) == 0xF)
    return res
def INC(cpu, x):
    res = (x + 1) & 0xFF
    cpu.set_ZF(res == 0)
    cpu.set_NF(0)
    cpu.set_HF((res & 0xF) == 0x0)
    return res
def OR(cpu, x):
    cpu.A |= x
    cpu.F = F_LUT_F000[cpu.F]
    cpu.set_ZF(cpu.A == 0)
def RL(cpu, x):
    res = (x << 1 | CF[cpu.F]) & 0xFF
    cpu.set_CF(BIT7[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def RLC(cpu, x):
    res = (x << 1 | x >> 7) & 0xFF
    cpu.set_CF(BIT7[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def RR(cpu, x):
    res = CF[cpu.F] << 7 | x >> 1
    cpu.set_CF(BIT0[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def RRC(cpu, x):
    res = (x << 7 | x >> 1) & 0xFF
    cpu.set_CF(BIT0[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def SLA(cpu, x):
    res = (x << 1) & 0xFF
    cpu.set_CF(BIT7[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def SRA(cpu, x):
    res = x >> 1 | (x & 0x80)
    cpu.set_CF(BIT0[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def SRL(cpu, x):
    res = x >> 1
    cpu.set_CF(BIT0[x])
    cpu.F = F_LUT_F00F[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def SBC(cpu, x, carry):
    a = cpu.A
    res = a - x - carry
    cpu.set_CF(res < 0)
    cpu.set_HF((a & 0xF) - (x & 0xF) - carry < 0)
    cpu.F = F_LUT_F1FF[cpu.F]
    cpu.set_ZF((res & 0xFF) == 0)
    cpu.A = res & 0xFF
def SUB(cpu, x): SBC(cpu, x, 0)
def SWAP(cpu, x):
    res = (x << 4 | x >> 4) & 0xFF
    cpu.F = F_LUT_F000[cpu.F]
    cpu.set_ZF(res == 0)
    return res
def XOR(cpu, x):
    cpu.A ^= x
    cpu.F = F_LUT_F000[cpu.F]
    cpu.set_ZF(cpu.A == 0)
    
    
# 8-bit loads
def LD_A_A(cpu): pass
def LD_A_B(cpu): cpu.A = cpu.B
def LD_A_C(cpu): cpu.A = cpu.C
def LD_A_D(cpu): cpu.A = cpu.D
def LD_A_E(cpu): cpu.A = cpu.E
def LD_A_H(cpu): cpu.A = cpu.H
def LD_A_L(cpu): cpu.A = cpu.L
def LD_A_aHL(cpu): cpu.A = cpu.read_HL()
def LD_B_A(cpu): cpu.B = cpu.A
def LD_B_B(cpu): pass
def LD_B_C(cpu): cpu.B = cpu.C
def LD_B_D(cpu): cpu.B = cpu.D
def LD_B_E(cpu): cpu.B = cpu.E
def LD_B_H(cpu): cpu.B = cpu.H
def LD_B_L(cpu): cpu.B = cpu.L
def LD_B_aHL(cpu): cpu.B = cpu.read_HL()
def LD_C_A(cpu): cpu.C = cpu.A
def LD_C_B(cpu): cpu.C = cpu.B
def LD_C_C(cpu): pass
def LD_C_D(cpu): cpu.C = cpu.D
def LD_C_E(cpu): cpu.C = cpu.E
def LD_C_H(cpu): cpu.C = cpu.H
def LD_C_L(cpu): cpu.C = cpu.L
def LD_C_aHL(cpu): cpu.C = cpu.read_HL()
def LD_D_A(cpu): cpu.D = cpu.A
def LD_D_B(cpu): cpu.D = cpu.B
def LD_D_C(cpu): cpu.D = cpu.C
def LD_D_D(cpu): pass
def LD_D_E(cpu): cpu.D = cpu.E
def LD_D_H(cpu): cpu.D = cpu.H
def LD_D_L(cpu): cpu.D = cpu.L
def LD_D_aHL(cpu): cpu.D = cpu.read_HL()
def LD_E_A(cpu): cpu.E = cpu.A
def LD_E_B(cpu): cpu.E = cpu.B
def LD_E_C(cpu): cpu.E = cpu.C
def LD_E_D(cpu): cpu.E = cpu.D
def LD_E_E(cpu): pass
def LD_E_H(cpu): cpu.E = cpu.H
def LD_E_L(cpu): cpu.E = cpu.L
def LD_E_aHL(cpu): cpu.E = cpu.read_HL()
def LD_H_A(cpu): cpu.H = cpu.A
def LD_H_B(cpu): cpu.H = cpu.B
def LD_H_C(cpu): cpu.H = cpu.C
def LD_H_D(cpu): cpu.H = cpu.D
def LD_H_E(cpu): cpu.H = cpu.E
def LD_H_H(cpu): pass
def LD_H_L(cpu): cpu.H = cpu.L
def LD_H_aHL(cpu): cpu.H = cpu.read_HL()
def LD_L_A(cpu): cpu.L = cpu.A
def LD_L_B(cpu): cpu.L = cpu.B
def LD_L_C(cpu): cpu.L = cpu.C
def LD_L_D(cpu): cpu.L = cpu.D
def LD_L_E(cpu): cpu.L = cpu.E
def LD_L_H(cpu): cpu.L = cpu.H
def LD_L_L(cpu): pass
def LD_L_aHL(cpu): cpu.L = cpu.read_HL()
def LD_A_d8(cpu): cpu.A = cpu.fetch_imm8()
def LD_B_d8(cpu): cpu.B = cpu.fetch_imm8()
def LD_C_d8(cpu): cpu.C = cpu.fetch_imm8()
def LD_D_d8(cpu): cpu.D = cpu.fetch_imm8()
def LD_E_d8(cpu): cpu.E = cpu.fetch_imm8()
def LD_H_d8(cpu): cpu.H = cpu.fetch_imm8()
def LD_L_d8(cpu): cpu.L = cpu.fetch_imm8()
def LD_aHL_d8(cpu): cpu.write_HL(cpu.fetch_imm8())
def LD_aHL_A(cpu): cpu.write_HL(cpu.A)
def LD_aHL_B(cpu): cpu.write_HL(cpu.B)
def LD_aHL_C(cpu): cpu.write_HL(cpu.C)
def LD_aHL_D(cpu): cpu.write_HL(cpu.D)
def LD_aHL_E(cpu): cpu.write_HL(cpu.E)
def LD_aHL_H(cpu): cpu.write_HL(cpu.H)
def LD_aHL_L(cpu): cpu.write_HL(cpu.L)
def LD_A_aBC(cpu): cpu.A = cpu.read_BC()
def LD_aBC_A(cpu): cpu.write_BC(cpu.A)
def LD_A_aDE(cpu): cpu.A = cpu.read_DE()
def LD_aDE_A(cpu): cpu.write_DE(cpu.A)
def LD_A_a16(cpu): cpu.A = cpu.read_a16()
def LD_a16_A(cpu): cpu.write_a16(cpu.A)
def LDD_A_aHL(cpu):
    cpu.A = cpu.read_HL()
    cpu.dec_HL()
def LDD_aHL_A(cpu):
    cpu.write_HL(cpu.A)
    cpu.dec_HL()
def LDI_A_aHL(cpu):
    cpu.A = cpu.read_HL()
    cpu.inc_HL()
def LDI_aHL_A(cpu):
    cpu.write_HL(cpu.A)
    cpu.inc_HL()
def LDH_A_aC(cpu): cpu.A = cpu.read_mmio(cpu.C)
def LDH_aC_A(cpu): cpu.write_mmio(cpu.C, cpu.A)
def LDH_A_a8(cpu): cpu.A = cpu.read_mmio(cpu.fetch_imm8())
def LDH_a8_A(cpu): cpu.write_mmio(cpu.fetch_imm8(), cpu.A)

# 8-bit arithmetic
def ADD_A_A(cpu): ADD(cpu, cpu.A)
def ADD_A_B(cpu): ADD(cpu, cpu.B)
def ADD_A_C(cpu): ADD(cpu, cpu.C)
def ADD_A_D(cpu): ADD(cpu, cpu.D)
def ADD_A_E(cpu): ADD(cpu, cpu.E)
def ADD_A_H(cpu): ADD(cpu, cpu.H)
def ADD_A_L(cpu): ADD(cpu, cpu.L)
def ADD_A_aHL(cpu): ADD(cpu, cpu.read_HL())
def ADD_A_d8(cpu): ADD(cpu, cpu.fetch_imm8())
def ADC_A_A(cpu): ADC(cpu, cpu.A, CF[cpu.F])
def ADC_A_B(cpu): ADC(cpu, cpu.B, CF[cpu.F])
def ADC_A_C(cpu): ADC(cpu, cpu.C, CF[cpu.F])
def ADC_A_D(cpu): ADC(cpu, cpu.D, CF[cpu.F])
def ADC_A_E(cpu): ADC(cpu, cpu.E, CF[cpu.F])
def ADC_A_H(cpu): ADC(cpu, cpu.H, CF[cpu.F])
def ADC_A_L(cpu): ADC(cpu, cpu.L, CF[cpu.F])
def ADC_A_aHL(cpu): ADC(cpu, cpu.read_HL(), CF[cpu.F])
def ADC_A_d8(cpu): ADC(cpu, cpu.fetch_imm8(), CF[cpu.F])
def SUB_A(cpu): SUB(cpu, cpu.A)
def SUB_B(cpu): SUB(cpu, cpu.B)
def SUB_C(cpu): SUB(cpu, cpu.C)
def SUB_D(cpu): SUB(cpu, cpu.D)
def SUB_E(cpu): SUB(cpu, cpu.E)
def SUB_H(cpu): SUB(cpu, cpu.H)
def SUB_L(cpu): SUB(cpu, cpu.L)
def SUB_aHL(cpu): SUB(cpu, cpu.read_HL())
def SUB_d8(cpu): SUB(cpu, cpu.fetch_imm8())
def SBC_A_A(cpu): SBC(cpu, cpu.A, CF[cpu.F])
def SBC_A_B(cpu): SBC(cpu, cpu.B, CF[cpu.F])
def SBC_A_C(cpu): SBC(cpu, cpu.C, CF[cpu.F])
def SBC_A_D(cpu): SBC(cpu, cpu.D, CF[cpu.F])
def SBC_A_E(cpu): SBC(cpu, cpu.E, CF[cpu.F])
def SBC_A_H(cpu): SBC(cpu, cpu.H, CF[cpu.F])
def SBC_A_L(cpu): SBC(cpu, cpu.L, CF[cpu.F])
def SBC_A_aHL(cpu): SBC(cpu, cpu.read_HL(), CF[cpu.F])
def SBC_A_d8(cpu): SBC(cpu, cpu.fetch_imm8(), CF[cpu.F])
def CP_A(cpu): CP(cpu, cpu.A)
def CP_B(cpu): CP(cpu, cpu.B)
def CP_C(cpu): CP(cpu, cpu.C)
def CP_D(cpu): CP(cpu, cpu.D)
def CP_E(cpu): CP(cpu, cpu.E)
def CP_H(cpu): CP(cpu, cpu.H)
def CP_L(cpu): CP(cpu, cpu.L)
def CP_aHL(cpu): CP(cpu, cpu.read_HL())
def CP_d8(cpu): CP(cpu, cpu.fetch_imm8())
def AND_A(cpu): AND(cpu, cpu.A)
def AND_B(cpu): AND(cpu, cpu.B)
def AND_C(cpu): AND(cpu, cpu.C)
def AND_D(cpu): AND(cpu, cpu.D)
def AND_E(cpu): AND(cpu, cpu.E)
def AND_H(cpu): AND(cpu, cpu.H)
def AND_L(cpu): AND(cpu, cpu.L)
def AND_aHL(cpu): AND(cpu, cpu.read_HL())
def AND_d8(cpu): AND(cpu, cpu.fetch_imm8())
def OR_A(cpu): OR(cpu, cpu.A)
def OR_B(cpu): OR(cpu, cpu.B)
def OR_C(cpu): OR(cpu, cpu.C)
def OR_D(cpu): OR(cpu, cpu.D)
def OR_E(cpu): OR(cpu, cpu.E)
def OR_H(cpu): OR(cpu, cpu.H)
def OR_L(cpu): OR(cpu, cpu.L)
def OR_aHL(cpu): OR(cpu, cpu.read_HL())
def OR_d8(cpu): OR(cpu, cpu.fetch_imm8())
def XOR_A(cpu): XOR(cpu, cpu.A)
def XOR_B(cpu): XOR(cpu, cpu.B)
def XOR_C(cpu): XOR(cpu, cpu.C)
def XOR_D(cpu): XOR(cpu, cpu.D)
def XOR_E(cpu): XOR(cpu, cpu.E)
def XOR_H(cpu): XOR(cpu, cpu.H)
def XOR_L(cpu): XOR(cpu, cpu.L)
def XOR_aHL(cpu): XOR(cpu, cpu.read_HL())
def XOR_d8(cpu): XOR(cpu, cpu.fetch_imm8())
def DEC_A(cpu): cpu.A = DEC(cpu, cpu.A)
def DEC_B(cpu): cpu.B = DEC(cpu, cpu.B)
def DEC_C(cpu): cpu.C = DEC(cpu, cpu.C)
def DEC_D(cpu): cpu.D = DEC(cpu, cpu.D)
def DEC_E(cpu): cpu.E = DEC(cpu, cpu.E)
def DEC_H(cpu): cpu.H = DEC(cpu, cpu.H)
def DEC_L(cpu): cpu.L = DEC(cpu, cpu.L)
def DEC_aHL(cpu): cpu.write_HL(DEC(cpu, cpu.read_HL()))
def INC_A(cpu): cpu.A = INC(cpu, cpu.A)
def INC_B(cpu): cpu.B = INC(cpu, cpu.B)
def INC_C(cpu): cpu.C = INC(cpu, cpu.C)
def INC_D(cpu): cpu.D = INC(cpu, cpu.D)
def INC_E(cpu): cpu.E = INC(cpu, cpu.E)
def INC_H(cpu): cpu.H = INC(cpu, cpu.H)
def INC_L(cpu): cpu.L = INC(cpu, cpu.L)
def INC_aHL(cpu): cpu.write_HL(INC(cpu, cpu.read_HL()))
def RLCA(cpu): cpu.A, cpu.F = RLC(cpu, cpu.A), F_LUT_0FFF[cpu.F]
def RLA(cpu): cpu.A, cpu.F = RL(cpu, cpu.A), F_LUT_0FFF[cpu.F]
def RRCA(cpu): cpu.A, cpu.F = RRC(cpu, cpu.A), F_LUT_0FFF[cpu.F]
def RRA(cpu): cpu.A, cpu.F = RR(cpu, cpu.A), F_LUT_0FFF[cpu.F]

# Control
def JP_a16(cpu): cpu.PC = cpu.fetch_imm16()
def JP_HL(cpu): cpu.PC = cpu.get_HL()
def JR_i8(cpu): cpu.PC = (INT8[cpu.fetch_imm8()] + cpu.PC) & 0xFFFF
def CALL_a16(cpu): cpu.call(cpu.fetch_imm16())
def RET(cpu): cpu.PC = cpu.pop()
def RETI(cpu):
    cpu.PC = cpu.pop()
    cpu.IME = True
def JP_NZ_a16(cpu): JP_cc_a16(cpu, NZF[cpu.F])
def JP_Z_a16(cpu): JP_cc_a16(cpu, ZF[cpu.F])
def JP_NC_a16(cpu): JP_cc_a16(cpu, NCF[cpu.F])
def JP_C_a16(cpu): JP_cc_a16(cpu, CF[cpu.F])
def JR_NZ_i8(cpu): JR_cc_i8(cpu, NZF[cpu.F])
def JR_Z_i8(cpu): JR_cc_i8(cpu, ZF[cpu.F])
def JR_NC_i8(cpu): JR_cc_i8(cpu, NCF[cpu.F])
def JR_C_i8(cpu): JR_cc_i8(cpu, CF[cpu.F])
def CALL_NZ_a16(cpu): CALL_cc_a16(cpu, NZF[cpu.F])
def CALL_Z_a16(cpu): CALL_cc_a16(cpu, ZF[cpu.F])
def CALL_NC_a16(cpu): CALL_cc_a16(cpu, NCF[cpu.F])
def CALL_C_a16(cpu): CALL_cc_a16(cpu, CF[cpu.F])
def RET_NZ(cpu): RET_cc(cpu, NZF[cpu.F])
def RET_Z(cpu): RET_cc(cpu, ZF[cpu.F])
def RET_NC(cpu): RET_cc(cpu, NCF[cpu.F])
def RET_C(cpu): RET_cc(cpu, CF[cpu.F])
def RST_00H(cpu): cpu.call(0x00)
def RST_08H(cpu): cpu.call(0x08)
def RST_10H(cpu): cpu.call(0x10)
def RST_18H(cpu): cpu.call(0x18)
def RST_20H(cpu): cpu.call(0x20)
def RST_28H(cpu): cpu.call(0x28)
def RST_30H(cpu): cpu.call(0x30)
def RST_38H(cpu): cpu.call(0x38)

# Miscellaneous
def HALT(cpu): cpu.halted = True
def STOP(cpu): print('IMPLEMENT STOP')
def DI(cpu): cpu.IME, cpu.IME_scheduled = False, False
def EI(cpu): cpu.IME_scheduled = True
def CCF(cpu): cpu.F = F_LUT_F00I[cpu.F]
def SCF(cpu): cpu.F = F_LUT_F001[cpu.F]
def NOP(cpu): pass
def DAA(cpu):
    a = cpu.A
    f = cpu.F
    correction = 0x60 if CF[f] else 0x0
    if HF[f] or not NF[f] and a & 0xF > 9:
        correction |= 0x6

    if CF[f] or not NF[f] and a > 0x99:
        correction |= 0x60

    if NF[f]:
        a = (a - correction) & 0xFF
    else:
        a = (a + correction) & 0xFF

    if (correction << 2) & 0x100 != 0:
        cpu.set_CF(1)

    cpu.set_HF(0)
    cpu.set_ZF(not a)

    cpu.A = a & 0xFF

def CPL(cpu):
    cpu.A ^= 0xFF
    cpu.F = F_LUT_F11F[cpu.F]
    
# 16-bit loads
def LD_BC_d16(cpu): cpu.set_BC(cpu.fetch_imm16())
def LD_DE_d16(cpu): cpu.set_DE(cpu.fetch_imm16())
def LD_HL_d16(cpu): cpu.set_HL(cpu.fetch_imm16())
def LD_SP_d16(cpu): cpu.SP = cpu.fetch_imm16()
def LD_a16_SP(cpu):
    address = cpu.fetch_imm16()
    cpu.mmu.write(address, cpu.SP & 0xFF)
    cpu.mmu.write((address + 1) & 0xFFFF, cpu.SP >> 8)
def LD_SP_HL(cpu): cpu.SP = cpu.get_HL()
def PUSH_BC(cpu): cpu.push(cpu.get_BC())
def PUSH_DE(cpu): cpu.push(cpu.get_DE())
def PUSH_HL(cpu): cpu.push(cpu.get_HL())
def PUSH_AF(cpu): cpu.push(cpu.get_AF())
def POP_BC(cpu): cpu.set_BC(cpu.pop())
def POP_DE(cpu): cpu.set_DE(cpu.pop())
def POP_HL(cpu): cpu.set_HL(cpu.pop())
def POP_AF(cpu): cpu.set_AF(cpu.pop())

# 16-bit arithmetic
def ADD_HL_BC(cpu): ADD_HL_16(cpu, cpu.get_BC())
def ADD_HL_DE(cpu): ADD_HL_16(cpu, cpu.get_DE())
def ADD_HL_HL(cpu): ADD_HL_16(cpu, cpu.get_HL())
def ADD_HL_SP(cpu): ADD_HL_16(cpu, cpu.SP)
def ADD_SP_i8(cpu): cpu.SP = add_SP_i8(cpu)
def LD_HL_SP_i8(cpu): cpu.set_HL(add_SP_i8(cpu))
def INC_BC(cpu): cpu.inc_BC()
def INC_DE(cpu): cpu.inc_DE()
def INC_HL(cpu): cpu.inc_HL()
def INC_SP(cpu): cpu.inc_SP()
def DEC_BC(cpu): cpu.dec_BC()
def DEC_DE(cpu): cpu.dec_DE()
def DEC_HL(cpu): cpu.dec_HL()
def DEC_SP(cpu): cpu.dec_SP()

# CB Prefix
def PREFIX_CB(cpu): cpu.OPCODES_CB[cpu.fetch_imm8()]()

# 8-bit arithmetic
def RLC_A(cpu): cpu.A = RLC(cpu, cpu.A)
def RLC_B(cpu): cpu.B = RLC(cpu, cpu.B)
def RLC_C(cpu): cpu.C = RLC(cpu, cpu.C)
def RLC_D(cpu): cpu.D = RLC(cpu, cpu.D)
def RLC_E(cpu): cpu.E = RLC(cpu, cpu.E)
def RLC_H(cpu): cpu.H = RLC(cpu, cpu.H)
def RLC_L(cpu): cpu.L = RLC(cpu, cpu.L)
def RLC_aHL(cpu): cpu.write_HL(RLC(cpu, cpu.read_HL()))
def RRC_A(cpu): cpu.A = RRC(cpu, cpu.A)
def RRC_B(cpu): cpu.B = RRC(cpu, cpu.B)
def RRC_C(cpu): cpu.C = RRC(cpu, cpu.C)
def RRC_D(cpu): cpu.D = RRC(cpu, cpu.D)
def RRC_E(cpu): cpu.E = RRC(cpu, cpu.E)
def RRC_H(cpu): cpu.H = RRC(cpu, cpu.H)
def RRC_L(cpu): cpu.L = RRC(cpu, cpu.L)
def RRC_aHL(cpu): cpu.write_HL(RRC(cpu, cpu.read_HL()))
def RL_A(cpu): cpu.A = RL(cpu, cpu.A)
def RL_B(cpu): cpu.B = RL(cpu, cpu.B)
def RL_C(cpu): cpu.C = RL(cpu, cpu.C)
def RL_D(cpu): cpu.D = RL(cpu, cpu.D)
def RL_E(cpu): cpu.E = RL(cpu, cpu.E)
def RL_H(cpu): cpu.H = RL(cpu, cpu.H)
def RL_L(cpu): cpu.L = RL(cpu, cpu.L)
def RL_aHL(cpu): cpu.write_HL(RL(cpu, cpu.read_HL()))
def RR_A(cpu): cpu.A = RR(cpu, cpu.A)
def RR_B(cpu): cpu.B = RR(cpu, cpu.B)
def RR_C(cpu): cpu.C = RR(cpu, cpu.C)
def RR_D(cpu): cpu.D = RR(cpu, cpu.D)
def RR_E(cpu): cpu.E = RR(cpu, cpu.E)
def RR_H(cpu): cpu.H = RR(cpu, cpu.H)
def RR_L(cpu): cpu.L = RR(cpu, cpu.L)
def RR_aHL(cpu): cpu.write_HL(RR(cpu, cpu.read_HL()))
def SLA_A(cpu): cpu.A = SLA(cpu, cpu.A)
def SLA_B(cpu): cpu.B = SLA(cpu, cpu.B)
def SLA_C(cpu): cpu.C = SLA(cpu, cpu.C)
def SLA_D(cpu): cpu.D = SLA(cpu, cpu.D)
def SLA_E(cpu): cpu.E = SLA(cpu, cpu.E)
def SLA_H(cpu): cpu.H = SLA(cpu, cpu.H)
def SLA_L(cpu): cpu.L = SLA(cpu, cpu.L)
def SLA_aHL(cpu): cpu.write_HL(SLA(cpu, cpu.read_HL()))
def SRA_A(cpu): cpu.A = SRA(cpu, cpu.A)
def SRA_B(cpu): cpu.B = SRA(cpu, cpu.B)
def SRA_C(cpu): cpu.C = SRA(cpu, cpu.C)
def SRA_D(cpu): cpu.D = SRA(cpu, cpu.D)
def SRA_E(cpu): cpu.E = SRA(cpu, cpu.E)
def SRA_H(cpu): cpu.H = SRA(cpu, cpu.H)
def SRA_L(cpu): cpu.L = SRA(cpu, cpu.L)
def SRA_aHL(cpu): cpu.write_HL(SRA(cpu, cpu.read_HL()))
def SWAP_A(cpu): cpu.A = SWAP(cpu, cpu.A)
def SWAP_B(cpu): cpu.B = SWAP(cpu, cpu.B)
def SWAP_C(cpu): cpu.C = SWAP(cpu, cpu.C)
def SWAP_D(cpu): cpu.D = SWAP(cpu, cpu.D)
def SWAP_E(cpu): cpu.E = SWAP(cpu, cpu.E)
def SWAP_H(cpu): cpu.H = SWAP(cpu, cpu.H)
def SWAP_L(cpu): cpu.L = SWAP(cpu, cpu.L)
def SWAP_aHL(cpu): cpu.write_HL(SWAP(cpu, cpu.read_HL()))
def SRL_A(cpu): cpu.A = SRL(cpu, cpu.A)
def SRL_B(cpu): cpu.B = SRL(cpu, cpu.B)
def SRL_C(cpu): cpu.C = SRL(cpu, cpu.C)
def SRL_D(cpu): cpu.D = SRL(cpu, cpu.D)
def SRL_E(cpu): cpu.E = SRL(cpu, cpu.E)
def SRL_H(cpu): cpu.H = SRL(cpu, cpu.H)
def SRL_L(cpu): cpu.L = SRL(cpu, cpu.L)
def SRL_aHL(cpu): cpu.write_HL(SRL(cpu, cpu.read_HL()))
def BIT_0_A(cpu): BIT(cpu, 0, cpu.A)
def BIT_0_B(cpu): BIT(cpu, 0, cpu.B)
def BIT_0_C(cpu): BIT(cpu, 0, cpu.C)
def BIT_0_D(cpu): BIT(cpu, 0, cpu.D)
def BIT_0_E(cpu): BIT(cpu, 0, cpu.E)
def BIT_0_H(cpu): BIT(cpu, 0, cpu.H)
def BIT_0_L(cpu): BIT(cpu, 0, cpu.L)
def BIT_0_aHL(cpu): BIT(cpu, 0, cpu.read_HL())
def BIT_1_A(cpu): BIT(cpu, 1, cpu.A)
def BIT_1_B(cpu): BIT(cpu, 1, cpu.B)
def BIT_1_C(cpu): BIT(cpu, 1, cpu.C)
def BIT_1_D(cpu): BIT(cpu, 1, cpu.D)
def BIT_1_E(cpu): BIT(cpu, 1, cpu.E)
def BIT_1_H(cpu): BIT(cpu, 1, cpu.H)
def BIT_1_L(cpu): BIT(cpu, 1, cpu.L)
def BIT_1_aHL(cpu): BIT(cpu, 1, cpu.read_HL())
def BIT_2_A(cpu): BIT(cpu, 2, cpu.A)
def BIT_2_B(cpu): BIT(cpu, 2, cpu.B)
def BIT_2_C(cpu): BIT(cpu, 2, cpu.C)
def BIT_2_D(cpu): BIT(cpu, 2, cpu.D)
def BIT_2_E(cpu): BIT(cpu, 2, cpu.E)
def BIT_2_H(cpu): BIT(cpu, 2, cpu.H)
def BIT_2_L(cpu): BIT(cpu, 2, cpu.L)
def BIT_2_aHL(cpu): BIT(cpu, 2, cpu.read_HL())
def BIT_3_A(cpu): BIT(cpu, 3, cpu.A)
def BIT_3_B(cpu): BIT(cpu, 3, cpu.B)
def BIT_3_C(cpu): BIT(cpu, 3, cpu.C)
def BIT_3_D(cpu): BIT(cpu, 3, cpu.D)
def BIT_3_E(cpu): BIT(cpu, 3, cpu.E)
def BIT_3_H(cpu): BIT(cpu, 3, cpu.H)
def BIT_3_L(cpu): BIT(cpu, 3, cpu.L)
def BIT_3_aHL(cpu): BIT(cpu, 3, cpu.read_HL())
def BIT_4_A(cpu): BIT(cpu, 4, cpu.A)
def BIT_4_B(cpu): BIT(cpu, 4, cpu.B)
def BIT_4_C(cpu): BIT(cpu, 4, cpu.C)
def BIT_4_D(cpu): BIT(cpu, 4, cpu.D)
def BIT_4_E(cpu): BIT(cpu, 4, cpu.E)
def BIT_4_H(cpu): BIT(cpu, 4, cpu.H)
def BIT_4_L(cpu): BIT(cpu, 4, cpu.L)
def BIT_4_aHL(cpu): BIT(cpu, 4, cpu.read_HL())
def BIT_5_A(cpu): BIT(cpu, 5, cpu.A)
def BIT_5_B(cpu): BIT(cpu, 5, cpu.B)
def BIT_5_C(cpu): BIT(cpu, 5, cpu.C)
def BIT_5_D(cpu): BIT(cpu, 5, cpu.D)
def BIT_5_E(cpu): BIT(cpu, 5, cpu.E)
def BIT_5_H(cpu): BIT(cpu, 5, cpu.H)
def BIT_5_L(cpu): BIT(cpu, 5, cpu.L)
def BIT_5_aHL(cpu): BIT(cpu, 5, cpu.read_HL())
def BIT_6_A(cpu): BIT(cpu, 6, cpu.A)
def BIT_6_B(cpu): BIT(cpu, 6, cpu.B)
def BIT_6_C(cpu): BIT(cpu, 6, cpu.C)
def BIT_6_D(cpu): BIT(cpu, 6, cpu.D)
def BIT_6_E(cpu): BIT(cpu, 6, cpu.E)
def BIT_6_H(cpu): BIT(cpu, 6, cpu.H)
def BIT_6_L(cpu): BIT(cpu, 6, cpu.L)
def BIT_6_aHL(cpu): BIT(cpu, 6, cpu.read_HL())
def BIT_7_A(cpu): BIT(cpu, 7, cpu.A)
def BIT_7_B(cpu): BIT(cpu, 7, cpu.B)
def BIT_7_C(cpu): BIT(cpu, 7, cpu.C)
def BIT_7_D(cpu): BIT(cpu, 7, cpu.D)
def BIT_7_E(cpu): BIT(cpu, 7, cpu.E)
def BIT_7_H(cpu): BIT(cpu, 7, cpu.H)
def BIT_7_L(cpu): BIT(cpu, 7, cpu.L)
def BIT_7_aHL(cpu): BIT(cpu, 7, cpu.read_HL())
def RES_0_A(cpu): cpu.A = RES0[cpu.A]
def RES_0_B(cpu): cpu.B = RES0[cpu.B]
def RES_0_C(cpu): cpu.C = RES0[cpu.C]
def RES_0_D(cpu): cpu.D = RES0[cpu.D]
def RES_0_E(cpu): cpu.E = RES0[cpu.E]
def RES_0_H(cpu): cpu.H = RES0[cpu.H]
def RES_0_L(cpu): cpu.L = RES0[cpu.L]
def RES_0_aHL(cpu): cpu.write_HL(RES0[cpu.read_HL()])
def RES_1_A(cpu): cpu.A = RES1[cpu.A]
def RES_1_B(cpu): cpu.B = RES1[cpu.B]
def RES_1_C(cpu): cpu.C = RES1[cpu.C]
def RES_1_D(cpu): cpu.D = RES1[cpu.D]
def RES_1_E(cpu): cpu.E = RES1[cpu.E]
def RES_1_H(cpu): cpu.H = RES1[cpu.H]
def RES_1_L(cpu): cpu.L = RES1[cpu.L]
def RES_1_aHL(cpu): cpu.write_HL(RES1[cpu.read_HL()])
def RES_2_A(cpu): cpu.A = RES2[cpu.A]
def RES_2_B(cpu): cpu.B = RES2[cpu.B]
def RES_2_C(cpu): cpu.C = RES2[cpu.C]
def RES_2_D(cpu): cpu.D = RES2[cpu.D]
def RES_2_E(cpu): cpu.E = RES2[cpu.E]
def RES_2_H(cpu): cpu.H = RES2[cpu.H]
def RES_2_L(cpu): cpu.L = RES2[cpu.L]
def RES_2_aHL(cpu): cpu.write_HL(RES2[cpu.read_HL()])
def RES_3_A(cpu): cpu.A = RES3[cpu.A]
def RES_3_B(cpu): cpu.B = RES3[cpu.B]
def RES_3_C(cpu): cpu.C = RES3[cpu.C]
def RES_3_D(cpu): cpu.D = RES3[cpu.D]
def RES_3_E(cpu): cpu.E = RES3[cpu.E]
def RES_3_H(cpu): cpu.H = RES3[cpu.H]
def RES_3_L(cpu): cpu.L = RES3[cpu.L]
def RES_3_aHL(cpu): cpu.write_HL(RES3[cpu.read_HL()])
def RES_4_A(cpu): cpu.A = RES4[cpu.A]
def RES_4_B(cpu): cpu.B = RES4[cpu.B]
def RES_4_C(cpu): cpu.C = RES4[cpu.C]
def RES_4_D(cpu): cpu.D = RES4[cpu.D]
def RES_4_E(cpu): cpu.E = RES4[cpu.E]
def RES_4_H(cpu): cpu.H = RES4[cpu.H]
def RES_4_L(cpu): cpu.L = RES4[cpu.L]
def RES_4_aHL(cpu): cpu.write_HL(RES4[cpu.read_HL()])
def RES_5_A(cpu): cpu.A = RES5[cpu.A]
def RES_5_B(cpu): cpu.B = RES5[cpu.B]
def RES_5_C(cpu): cpu.C = RES5[cpu.C]
def RES_5_D(cpu): cpu.D = RES5[cpu.D]
def RES_5_E(cpu): cpu.E = RES5[cpu.E]
def RES_5_H(cpu): cpu.H = RES5[cpu.H]
def RES_5_L(cpu): cpu.L = RES5[cpu.L]
def RES_5_aHL(cpu): cpu.write_HL(RES5[cpu.read_HL()])
def RES_6_A(cpu): cpu.A = RES6[cpu.A]
def RES_6_B(cpu): cpu.B = RES6[cpu.B]
def RES_6_C(cpu): cpu.C = RES6[cpu.C]
def RES_6_D(cpu): cpu.D = RES6[cpu.D]
def RES_6_E(cpu): cpu.E = RES6[cpu.E]
def RES_6_H(cpu): cpu.H = RES6[cpu.H]
def RES_6_L(cpu): cpu.L = RES6[cpu.L]
def RES_6_aHL(cpu): cpu.write_HL(RES6[cpu.read_HL()])
def RES_7_A(cpu): cpu.A = RES7[cpu.A]
def RES_7_B(cpu): cpu.B = RES7[cpu.B]
def RES_7_C(cpu): cpu.C = RES7[cpu.C]
def RES_7_D(cpu): cpu.D = RES7[cpu.D]
def RES_7_E(cpu): cpu.E = RES7[cpu.E]
def RES_7_H(cpu): cpu.H = RES7[cpu.H]
def RES_7_L(cpu): cpu.L = RES7[cpu.L]
def RES_7_aHL(cpu): cpu.write_HL(RES7[cpu.read_HL()])
def SET_0_A(cpu): cpu.A = SET0[cpu.A]
def SET_0_B(cpu): cpu.B = SET0[cpu.B]
def SET_0_C(cpu): cpu.C = SET0[cpu.C]
def SET_0_D(cpu): cpu.D = SET0[cpu.D]
def SET_0_E(cpu): cpu.E = SET0[cpu.E]
def SET_0_H(cpu): cpu.H = SET0[cpu.H]
def SET_0_L(cpu): cpu.L = SET0[cpu.L]
def SET_0_aHL(cpu): cpu.write_HL(SET0[cpu.read_HL()])
def SET_1_A(cpu): cpu.A = SET1[cpu.A]
def SET_1_B(cpu): cpu.B = SET1[cpu.B]
def SET_1_C(cpu): cpu.C = SET1[cpu.C]
def SET_1_D(cpu): cpu.D = SET1[cpu.D]
def SET_1_E(cpu): cpu.E = SET1[cpu.E]
def SET_1_H(cpu): cpu.H = SET1[cpu.H]
def SET_1_L(cpu): cpu.L = SET1[cpu.L]
def SET_1_aHL(cpu): cpu.write_HL(SET1[cpu.read_HL()])
def SET_2_A(cpu): cpu.A = SET2[cpu.A]
def SET_2_B(cpu): cpu.B = SET2[cpu.B]
def SET_2_C(cpu): cpu.C = SET2[cpu.C]
def SET_2_D(cpu): cpu.D = SET2[cpu.D]
def SET_2_E(cpu): cpu.E = SET2[cpu.E]
def SET_2_H(cpu): cpu.H = SET2[cpu.H]
def SET_2_L(cpu): cpu.L = SET2[cpu.L]
def SET_2_aHL(cpu): cpu.write_HL(SET2[cpu.read_HL()])
def SET_3_A(cpu): cpu.A = SET3[cpu.A]
def SET_3_B(cpu): cpu.B = SET3[cpu.B]
def SET_3_C(cpu): cpu.C = SET3[cpu.C]
def SET_3_D(cpu): cpu.D = SET3[cpu.D]
def SET_3_E(cpu): cpu.E = SET3[cpu.E]
def SET_3_H(cpu): cpu.H = SET3[cpu.H]
def SET_3_L(cpu): cpu.L = SET3[cpu.L]
def SET_3_aHL(cpu): cpu.write_HL(SET3[cpu.read_HL()])
def SET_4_A(cpu): cpu.A = SET4[cpu.A]
def SET_4_B(cpu): cpu.B = SET4[cpu.B]
def SET_4_C(cpu): cpu.C = SET4[cpu.C]
def SET_4_D(cpu): cpu.D = SET4[cpu.D]
def SET_4_E(cpu): cpu.E = SET4[cpu.E]
def SET_4_H(cpu): cpu.H = SET4[cpu.H]
def SET_4_L(cpu): cpu.L = SET4[cpu.L]
def SET_4_aHL(cpu): cpu.write_HL(SET4[cpu.read_HL()])
def SET_5_A(cpu): cpu.A = SET5[cpu.A]
def SET_5_B(cpu): cpu.B = SET5[cpu.B]
def SET_5_C(cpu): cpu.C = SET5[cpu.C]
def SET_5_D(cpu): cpu.D = SET5[cpu.D]
def SET_5_E(cpu): cpu.E = SET5[cpu.E]
def SET_5_H(cpu): cpu.H = SET5[cpu.H]
def SET_5_L(cpu): cpu.L = SET5[cpu.L]
def SET_5_aHL(cpu): cpu.write_HL(SET5[cpu.read_HL()])
def SET_6_A(cpu): cpu.A = SET6[cpu.A]
def SET_6_B(cpu): cpu.B = SET6[cpu.B]
def SET_6_C(cpu): cpu.C = SET6[cpu.C]
def SET_6_D(cpu): cpu.D = SET6[cpu.D]
def SET_6_E(cpu): cpu.E = SET6[cpu.E]
def SET_6_H(cpu): cpu.H = SET6[cpu.H]
def SET_6_L(cpu): cpu.L = SET6[cpu.L]
def SET_6_aHL(cpu): cpu.write_HL(SET6[cpu.read_HL()])
def SET_7_A(cpu): cpu.A = SET7[cpu.A]
def SET_7_B(cpu): cpu.B = SET7[cpu.B]
def SET_7_C(cpu): cpu.C = SET7[cpu.C]
def SET_7_D(cpu): cpu.D = SET7[cpu.D]
def SET_7_E(cpu): cpu.E = SET7[cpu.E]
def SET_7_H(cpu): cpu.H = SET7[cpu.H]
def SET_7_L(cpu): cpu.L = SET7[cpu.L]
def SET_7_aHL(cpu): cpu.write_HL(SET7[cpu.read_HL()])

OPCODES = [
    NOP,
    LD_BC_d16,
    LD_aBC_A,
    INC_BC,
    INC_B,
    DEC_B,
    LD_B_d8,
    RLCA,
    LD_a16_SP,
    ADD_HL_BC,
    LD_A_aBC,
    DEC_BC,
    INC_C,
    DEC_C,
    LD_C_d8,
    RRCA,
    STOP,
    LD_DE_d16,
    LD_aDE_A,
    INC_DE,
    INC_D,
    DEC_D,
    LD_D_d8,
    RLA,
    JR_i8,
    ADD_HL_DE,
    LD_A_aDE,
    DEC_DE,
    INC_E,
    DEC_E,
    LD_E_d8,
    RRA,
    JR_NZ_i8,
    LD_HL_d16,
    LDI_aHL_A,
    INC_HL,
    INC_H,
    DEC_H,
    LD_H_d8,
    DAA,
    JR_Z_i8,
    ADD_HL_HL,
    LDI_A_aHL,
    DEC_HL,
    INC_L,
    DEC_L,
    LD_L_d8,
    CPL,
    JR_NC_i8,
    LD_SP_d16,
    LDD_aHL_A,
    INC_SP,
    INC_aHL,
    DEC_aHL,
    LD_aHL_d8,
    SCF,
    JR_C_i8,
    ADD_HL_SP,
    LDD_A_aHL,
    DEC_SP,
    INC_A,
    DEC_A,
    LD_A_d8,
    CCF,
    LD_B_B,
    LD_B_C,
    LD_B_D,
    LD_B_E,
    LD_B_H,
    LD_B_L,
    LD_B_aHL,
    LD_B_A,
    LD_C_B,
    LD_C_C,
    LD_C_D,
    LD_C_E,
    LD_C_H,
    LD_C_L,
    LD_C_aHL,
    LD_C_A,
    LD_D_B,
    LD_D_C,
    LD_D_D,
    LD_D_E,
    LD_D_H,
    LD_D_L,
    LD_D_aHL,
    LD_D_A,
    LD_E_B,
    LD_E_C,
    LD_E_D,
    LD_E_E,
    LD_E_H,
    LD_E_L,
    LD_E_aHL,
    LD_E_A,
    LD_H_B,
    LD_H_C,
    LD_H_D,
    LD_H_E,
    LD_H_H,
    LD_H_L,
    LD_H_aHL,
    LD_H_A,
    LD_L_B,
    LD_L_C,
    LD_L_D,
    LD_L_E,
    LD_L_H,
    LD_L_L,
    LD_L_aHL,
    LD_L_A,
    LD_aHL_B,
    LD_aHL_C,
    LD_aHL_D,
    LD_aHL_E,
    LD_aHL_H,
    LD_aHL_L,
    HALT,
    LD_aHL_A,
    LD_A_B,
    LD_A_C,
    LD_A_D,
    LD_A_E,
    LD_A_H,
    LD_A_L,
    LD_A_aHL,
    LD_A_A,
    ADD_A_B,
    ADD_A_C,
    ADD_A_D,
    ADD_A_E,
    ADD_A_H,
    ADD_A_L,
    ADD_A_aHL,
    ADD_A_A,
    ADC_A_B,
    ADC_A_C,
    ADC_A_D,
    ADC_A_E,
    ADC_A_H,
    ADC_A_L,
    ADC_A_aHL,
    ADC_A_A,
    SUB_B,
    SUB_C,
    SUB_D,
    SUB_E,
    SUB_H,
    SUB_L,
    SUB_aHL,
    SUB_A,
    SBC_A_B,
    SBC_A_C,
    SBC_A_D,
    SBC_A_E,
    SBC_A_H,
    SBC_A_L,
    SBC_A_aHL,
    SBC_A_A,
    AND_B,
    AND_C,
    AND_D,
    AND_E,
    AND_H,
    AND_L,
    AND_aHL,
    AND_A,
    XOR_B,
    XOR_C,
    XOR_D,
    XOR_E,
    XOR_H,
    XOR_L,
    XOR_aHL,
    XOR_A,
    OR_B,
    OR_C,
    OR_D,
    OR_E,
    OR_H,
    OR_L,
    OR_aHL,
    OR_A,
    CP_B,
    CP_C,
    CP_D,
    CP_E,
    CP_H,
    CP_L,
    CP_aHL,
    CP_A,
    RET_NZ,
    POP_BC,
    JP_NZ_a16,
    JP_a16,
    CALL_NZ_a16,
    PUSH_BC,
    ADD_A_d8,
    RST_00H,
    RET_Z,
    RET,
    JP_Z_a16,
    PREFIX_CB,
    CALL_Z_a16,
    CALL_a16,
    ADC_A_d8,
    RST_08H,
    RET_NC,
    POP_DE,
    JP_NC_a16,
    invalid_opcode,
    CALL_NC_a16,
    PUSH_DE,
    SUB_d8,
    RST_10H,
    RET_C,
    RETI,
    JP_C_a16,
    invalid_opcode,
    CALL_C_a16,
    invalid_opcode,
    SBC_A_d8,
    RST_18H,
    LDH_a8_A,
    POP_HL,
    LDH_aC_A,
    invalid_opcode,
    invalid_opcode,
    PUSH_HL,
    AND_d8,
    RST_20H,
    ADD_SP_i8,
    JP_HL,
    LD_a16_A,
    invalid_opcode,
    invalid_opcode,
    invalid_opcode,
    XOR_d8,
    RST_28H,
    LDH_A_a8,
    POP_AF,
    LDH_A_aC,
    DI,
    invalid_opcode,
    PUSH_AF,
    OR_d8,
    RST_30H,
    LD_HL_SP_i8,
    LD_SP_HL,
    LD_A_a16,
    EI,
    invalid_opcode,
    invalid_opcode,
    CP_d8,
    RST_38H]

OPCODES_CB = [
    RLC_B,
    RLC_C,
    RLC_D,
    RLC_E,
    RLC_H,
    RLC_L,
    RLC_aHL,
    RLC_A,
    RRC_B,
    RRC_C,
    RRC_D,
    RRC_E,
    RRC_H,
    RRC_L,
    RRC_aHL,
    RRC_A,
    RL_B,
    RL_C,
    RL_D,
    RL_E,
    RL_H,
    RL_L,
    RL_aHL,
    RL_A,
    RR_B,
    RR_C,
    RR_D,
    RR_E,
    RR_H,
    RR_L,
    RR_aHL,
    RR_A,
    SLA_B,
    SLA_C,
    SLA_D,
    SLA_E,
    SLA_H,
    SLA_L,
    SLA_aHL,
    SLA_A,
    SRA_B,
    SRA_C,
    SRA_D,
    SRA_E,
    SRA_H,
    SRA_L,
    SRA_aHL,
    SRA_A,
    SWAP_B,
    SWAP_C,
    SWAP_D,
    SWAP_E,
    SWAP_H,
    SWAP_L,
    SWAP_aHL,
    SWAP_A,
    SRL_B,
    SRL_C,
    SRL_D,
    SRL_E,
    SRL_H,
    SRL_L,
    SRL_aHL,
    SRL_A,
    BIT_0_B,
    BIT_0_C,
    BIT_0_D,
    BIT_0_E,
    BIT_0_H,
    BIT_0_L,
    BIT_0_aHL,
    BIT_0_A,
    BIT_1_B,
    BIT_1_C,
    BIT_1_D,
    BIT_1_E,
    BIT_1_H,
    BIT_1_L,
    BIT_1_aHL,
    BIT_1_A,
    BIT_2_B,
    BIT_2_C,
    BIT_2_D,
    BIT_2_E,
    BIT_2_H,
    BIT_2_L,
    BIT_2_aHL,
    BIT_2_A,
    BIT_3_B,
    BIT_3_C,
    BIT_3_D,
    BIT_3_E,
    BIT_3_H,
    BIT_3_L,
    BIT_3_aHL,
    BIT_3_A,
    BIT_4_B,
    BIT_4_C,
    BIT_4_D,
    BIT_4_E,
    BIT_4_H,
    BIT_4_L,
    BIT_4_aHL,
    BIT_4_A,
    BIT_5_B,
    BIT_5_C,
    BIT_5_D,
    BIT_5_E,
    BIT_5_H,
    BIT_5_L,
    BIT_5_aHL,
    BIT_5_A,
    BIT_6_B,
    BIT_6_C,
    BIT_6_D,
    BIT_6_E,
    BIT_6_H,
    BIT_6_L,
    BIT_6_aHL,
    BIT_6_A,
    BIT_7_B,
    BIT_7_C,
    BIT_7_D,
    BIT_7_E,
    BIT_7_H,
    BIT_7_L,
    BIT_7_aHL,
    BIT_7_A,
    RES_0_B,
    RES_0_C,
    RES_0_D,
    RES_0_E,
    RES_0_H,
    RES_0_L,
    RES_0_aHL,
    RES_0_A,
    RES_1_B,
    RES_1_C,
    RES_1_D,
    RES_1_E,
    RES_1_H,
    RES_1_L,
    RES_1_aHL,
    RES_1_A,
    RES_2_B,
    RES_2_C,
    RES_2_D,
    RES_2_E,
    RES_2_H,
    RES_2_L,
    RES_2_aHL,
    RES_2_A,
    RES_3_B,
    RES_3_C,
    RES_3_D,
    RES_3_E,
    RES_3_H,
    RES_3_L,
    RES_3_aHL,
    RES_3_A,
    RES_4_B,
    RES_4_C,
    RES_4_D,
    RES_4_E,
    RES_4_H,
    RES_4_L,
    RES_4_aHL,
    RES_4_A,
    RES_5_B,
    RES_5_C,
    RES_5_D,
    RES_5_E,
    RES_5_H,
    RES_5_L,
    RES_5_aHL,
    RES_5_A,
    RES_6_B,
    RES_6_C,
    RES_6_D,
    RES_6_E,
    RES_6_H,
    RES_6_L,
    RES_6_aHL,
    RES_6_A,
    RES_7_B,
    RES_7_C,
    RES_7_D,
    RES_7_E,
    RES_7_H,
    RES_7_L,
    RES_7_aHL,
    RES_7_A,
    SET_0_B,
    SET_0_C,
    SET_0_D,
    SET_0_E,
    SET_0_H,
    SET_0_L,
    SET_0_aHL,
    SET_0_A,
    SET_1_B,
    SET_1_C,
    SET_1_D,
    SET_1_E,
    SET_1_H,
    SET_1_L,
    SET_1_aHL,
    SET_1_A,
    SET_2_B,
    SET_2_C,
    SET_2_D,
    SET_2_E,
    SET_2_H,
    SET_2_L,
    SET_2_aHL,
    SET_2_A,
    SET_3_B,
    SET_3_C,
    SET_3_D,
    SET_3_E,
    SET_3_H,
    SET_3_L,
    SET_3_aHL,
    SET_3_A,
    SET_4_B,
    SET_4_C,
    SET_4_D,
    SET_4_E,
    SET_4_H,
    SET_4_L,
    SET_4_aHL,
    SET_4_A,
    SET_5_B,
    SET_5_C,
    SET_5_D,
    SET_5_E,
    SET_5_H,
    SET_5_L,
    SET_5_aHL,
    SET_5_A,
    SET_6_B,
    SET_6_C,
    SET_6_D,
    SET_6_E,
    SET_6_H,
    SET_6_L,
    SET_6_aHL,
    SET_6_A,
    SET_7_B,
    SET_7_C,
    SET_7_D,
    SET_7_E,
    SET_7_H,
    SET_7_L,
    SET_7_aHL,
    SET_7_A]

CYCLES = [
     4,12, 8, 8, 4, 4, 8, 4,20, 8, 8, 8, 4, 4, 8, 4,
     4,12, 8, 8, 4, 4, 8, 4,12, 8, 8, 8, 4, 4, 8, 4,
     8,12, 8, 8, 4, 4, 8, 4, 8, 8, 8, 8, 4, 4, 8, 4,
     8,12, 8, 8,12,12,12, 4, 8, 8, 8, 8, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     8, 8, 8, 8, 8, 8, 4, 8, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     8,12,12,16,12,16, 8,16, 8,16,12, 4,12,24, 8,16,
     8,12,12, 0,12,16, 8,16, 8,16,12, 0,12, 0, 8,16,
    12,12, 8, 0, 0,16, 8,16,16, 4,16, 0, 0, 0, 8,16,
    12,12, 8, 4, 0,16, 8,16,12, 8,16, 4, 0, 0, 8,16]
CYCLES_BRANCHED = [
     4,12, 8, 8, 4, 4, 8, 4,20, 8, 8, 8, 4, 4, 8, 4,
     4,12, 8, 8, 4, 4, 8, 4,12, 8, 8, 8, 4, 4, 8, 4,
    12,12, 8, 8, 4, 4, 8, 4,12, 8, 8, 8, 4, 4, 8, 4,
    12,12, 8, 8,12,12,12, 4,12, 8, 8, 8, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     8, 8, 8, 8, 8, 8, 4, 8, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
     4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 4, 4, 4, 8, 4,
    20,12,16,16,24,16, 8,16,20,16,16, 4,24,24, 8,16,
    20,12,16, 0,24,16, 8,16,20,16,16, 0,24, 0, 8,16,
    12,12, 8, 0, 0,16, 8,16,16, 4,16, 0, 0, 0, 8,16,
    12,12, 8, 4, 0,16, 8,16,12, 8,16, 4, 0, 0, 8,16]
CYCLES_CB = [
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,12, 8, 8, 8, 8, 8, 8, 8,12, 8,
     8, 8, 8, 8, 8, 8,12, 8, 8, 8, 8, 8, 8, 8,12, 8,
     8, 8, 8, 8, 8, 8,12, 8, 8, 8, 8, 8, 8, 8,12, 8,
     8, 8, 8, 8, 8, 8,12, 8, 8, 8, 8, 8, 8, 8,12, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8,
     8, 8, 8, 8, 8, 8,16, 8, 8, 8, 8, 8, 8, 8,16, 8]