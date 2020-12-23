import requests

r = requests.get("https://gbdev.io/gb-opcodes/Opcodes.json")
opcode_data = r.json()

def get_zf(): return 'ZF[cpu.F]'
def get_nf(): return 'NF[cpu.F]'
def get_hf(): return 'HF[cpu.F]'
def get_cf(): return 'CF[cpu.F]'
def get_nzf(): return 'not ' + get_zf()
def get_ncf(): return 'not ' + get_cf()

# def set_zf(val): return 'cpu.F = ZF_to_F[cpu.F][val]'
# def set_nf(val): return 'cpu.F = NF_to_F[cpu.F][val]'
# def set_hf(val): return 'cpu.F = HF_to_F[cpu.F][val]'
# def set_cf(val): return 'cpu.F = CF_to_F[cpu.F][val]'
# def set_nf(val): return 'NNNNNNNNNNNNNNNNNNN'
# def set_hf(val): return 'HHHHHHHHHHHHHHHHHHH'
# def set_cf(val): return 'CCCCCCCCCCCCCCCCCCC'

class Operand:
    def __init__(self, operand_dic):
        self.name = operand_dic['name']
        self.bytes = operand_dic.get('bytes', 0)
        self.increment = operand_dic.get('increment', False)
        self.decrement = operand_dic.get('decrement', False)
        self.immediate = operand_dic['immediate']
    def header(self): return ('' if self.immediate or self.name[0] == 'a' else 'a') + self.name
    def read(self):
        name, imm = self.name, self.immediate
        if name in [str(i) for i in range(8)]: return self.name
        elif name in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            if imm: return f'cpu.{name}'
            return f'cpu.read_io_port(cpu.{name})'
        elif name in ['AF', 'BC', 'DE', 'HL', 'a16']:
            if imm: return f'cpu.get_{name}()'
            return f'cpu.read_{name}()'
        elif name in ['SP']: return f'cpu.SP'
        elif name in ['d8', 'd16']: return f'cpu.imm{name[1:]}()'
        elif name in ['a8']: return 'cpu.read_io_port(cpu.imm8())'
        elif name[-1] == 'H': return f'0x{name[:2]}'
    def write(self, val):
        name, imm = self.name, self.immediate
        if name in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            if imm: return f'cpu.{name} = {val}'
            return f'cpu.write_io_port(cpu.{name}, {val})'
        elif name in ['AF', 'BC', 'DE', 'HL', 'a16']:
            if imm: return f'cpu.set_{name}({val})'
            return f'cpu.write_{name}({val})'
        elif name in ['SP']: return f'cpu.SP = {val}'
        elif name in ['a8']: return f'cpu.write_io_port(cpu.imm8(), {val})'
        
class Instruction:
    def __init__(self, prefix, opcode, instr_dic):
        self.prefix = prefix
        self.opcode = opcode
        mnemonic = instr_dic['mnemonic']
        self.mnemonic = mnemonic
        self.bytes = instr_dic['bytes']
        self.cycles = instr_dic['cycles']
        operands = [Operand(o) for o in instr_dic['operands']]
        self.operands = operands
        self.immediate = instr_dic['immediate']
        flags = instr_dic['flags']
        self.flags = flags
        self.Z, self.H, self.N, self.C = flags['Z'], flags['N'], flags['H'], flags['C']
        if mnemonic == 'LD':
            if operands[1].name != 'SP' and (operands[0].increment or operands[1].increment): self.mnemonic = 'LDI'
            elif operands[0].decrement or operands[1].decrement: self.mnemonic = 'LDD'
            elif sum([o.name in ['C', 'a8'] and not o.immediate for o in operands]): self.mnemonic = 'LDH'
    def is_unprefixed(self): return self.prefix == 'unprefixed'
    def is_cbprefixed(self): return self.prefix == 'cbprefixed'
    def generate(self):
        mnem = self.mnemonic
        if 'ILLEGAL' in mnem: return
        oper_len = len(self.operands)
        s = ['def ' + '_'.join([mnem] + [o.header() for o in self.operands]) + '(cpu):']
        a, d8 = Operand({'name':'A', 'immediate':True}), Operand({'name':'d8', 'immediate':True})
        cond = {'Z':get_zf(), 'NZ':get_nzf(), 'C':get_cf(), 'NC':get_ncf()}
        if oper_len == 0:
            if mnem == 'NOP': s.append('pass')
            elif mnem in ['RLCA', 'RRCA', 'RLA', 'RRA']: s.append(a.write(f'cpu.{mnem}({a.read()})'))
            elif mnem == 'STOP': s.append('return "TODO"')
            elif mnem in ['DAA', 'CPL']: s.append(f'cpu.{mnem}()')
            elif mnem == 'CCF': s.append('cpu.F = F_lut_F00I[cpu.F]')
            elif mnem == 'SCF': s.append('cpu.F = F_lut_F001[cpu.F]')
            elif mnem == 'HALT': s.append('return "TODO"')
            elif mnem in ['RET', 'RETI']:
                s.append('cpu.PC = cpu.pop()')
                if mnem == 'RETI': s.append('cpu.ime = 1')
            elif mnem == 'PREFIX': s.append(f'prefix_jump_table[{d8.read()}]')
            elif mnem == 'DI': s.append('cpu.ime = 0')
            elif mnem == 'EI': s.append('cpu.ie = 1')
            else: print('ERROR', mnem, self.opcode)
        elif oper_len == 1:
            oper1 = self.operands[0]
            if mnem == 'CP': s.append(f'cpu.CP({oper1.read()})')
            elif mnem == 'CALL': s.append(f'cpu.call({oper1.read()})')
            elif mnem == 'PUSH': s.append(f'cpu.push({oper1.read()})')
            elif mnem == 'POP': s.append(oper1.write(f'cpu.pop()'))
            elif mnem in ['INC', 'DEC']:
                if oper1.immediate and oper1.name in ['BC', 'DE', 'HL', 'SP']: s.append(f'cpu.{mnem.lower()}_{oper1.name}()')
                else: s.append(oper1.write(f'cpu.{mnem}({oper1.read()})'))                    
            elif mnem == 'RET':
                s.append(f'if {cond[oper1.name]}:')
                s.append('    cpu.PC = cpu.pop()')
            elif mnem == 'JP': s.append(f'cpu.PC = {oper1.read()}')
            elif mnem == 'JR': s.append(f'cpu.PC = (cpu.PC + int8({d8.read()})) & 0xffff')
            elif mnem == 'RST': s.append(f'cpu.call(0x{oper1.name[:2]})')
            elif mnem in ['SRL', 'SWAP', 'SRA', 'SLA', 'RR', 'RL', 'RRC', 'RLC']: s.append(oper1.write(f'cpu.{mnem}({oper1.read()})'))
            elif mnem in ['AND', 'OR', 'XOR', 'SUB']: s.append(a.write(f'cpu.{mnem}({oper1.read()})'))
        elif oper_len == 2:
            oper1 = self.operands[0]
            oper2 = self.operands[1]
            if mnem in ['LD', 'LDI', 'LDD', 'LDH']:
                if self.opcode == '0xF8':
                    s.append(f'data = {d8.read()}')
                    s.append('cpu.CF = (cpu.SP & 0xff) + (data & 0xff) > 0xff')
                    s.append('cpu.HF = (cpu.SP & 0xf) + (data & 0xf) > 0xf')
                    s.append('cpu.NF, cpu.ZF = 0, 0')
                    s.append('cpu.write_hl((cpu.SP + int8(data)) & 0xffff)')
                elif self.opcode == '0x08':
                    s.append(f'cpu.store(cpu.imm16(), cpu.SP)')
                else:
                    s.append('pass' if oper1.name == oper2.name else oper1.write(f'{oper2.read()}'))
                    if mnem == 'LDI': s.append('cpu.inc_HL()')
                    elif mnem == 'LDD': s.append('cpu.dec_HL()')
            elif mnem in ['ADD', 'ADC', 'SBC']:
                if oper1.name == 'HL':
                    # s.append(oper1.write(f'cpu.ADD16({oper2.read()})'))
                    s.append(f'result = cpu.store or something dunno')
                elif oper1.name == 'SP': s.append('return "TODO"')
                else:s.append(oper1.write(f'cpu.{mnem}({oper2.read()})'))
            elif mnem in ['SET', 'RES', 'BIT']: s.append(oper2.write(f'cpu.{mnem}({oper1.name}, {oper2.read()})'))
            elif mnem == 'CALL':
                s.append(f'if {cond[oper1.name]}:')
                s.append(f'    cpu.call({oper2.read()})')
            if mnem == 'JP':
                s.append(f'if {cond[oper1.name]}:')
                s.append(f'    cpu.PC = {oper2.read()}')
            if mnem == 'JR':
                s.append(f'if {cond[oper1.name]}:')
                s.append(f'    cpu.PC = (cpu.PC + int8({d8.read()})) & 0xffff')
        if len(s) <= 2: return ' '.join(s)
        return s[0] + '\n    ' + '\n    '.join(s[1:])
    
            
        
    
opcodes = [Instruction(prefix, opcode, instr_dic) for prefix, instructions in opcode_data.items() for opcode, instr_dic in instructions.items()]
#for op in opcodes:
    #print(op.generate())
li = filter(None, [op.generate() for op in opcodes])
with open ('opcodes.py', 'w') as f:
    for i in li:
        f.write(f'{i}\n')

