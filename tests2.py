# INÚTIL SEM OS LOGS E OS TRACES, só estou a fazer upload para curiosidade dos professores.

#!/usr/bin/env pypy

from gb import Gameboy

def main():
    with open('dmg_boot.bin', 'rb') as f:
        bootrom = [b for b in f.read()]

    for filename in [
                    '01-special',
                    '02-interrupts',
                    '03-op sp,hl',
                    '04-op r,imm',
                    '05-op rp',
                    '06-ld r,r',
                    '07-jr,jp,call,ret,rst',
                    '08-misc instrs',
                    '09-op r,r',
                    '10-bit ops',
                    '11-op a,(hl)']:
        print('TESTING', filename + '\n')
        with open(f'cpu_instrs/individual/{filename}.gb', 'rb') as f:
            rom = [b for b in f.read()]
        with open(f'cpu_instrs/logs/Blargg{str(int(filename[:2]))}LYStubbed.txt', 'r') as f:
            log = [line for line in f]
        gb = Gameboy(bootrom, rom, True)
        from opcodes import OPCODES, OPCODES_CB
        cpu = gb.cpu
        read = gb.mmu.read
        def f1(r): return hex(r)[2:].upper().zfill(2)
        def f2(r): return hex(r)[2:].upper().zfill(4)
        old_should, old_got, old_imm = '', '', ''
        for cycle, should in enumerate(log):
            #print(bin(cpu.mmu.IF), 1)
            cpu.handle_interrupts()
            #print(bin(cpu.mmu.IF), 2)
            pc = cpu.PC
            imm = [read(pc + i) for i in range(4)]
            got = f"A: {f1(cpu.A)} F: {f1(cpu.F)} B: {f1(cpu.B)} C: {f1(cpu.C)} D: {f1(cpu.D)} E: {f1(cpu.E)} H: {f1(cpu.H)} L: {f1(cpu.L)} SP: {f2(cpu.SP)} PC: 00:{f2(pc)} ({' '.join([f1(s) for s in imm])})"
            if should[:82] != got:
                print(old_should[:82])
                print(should[:82])
                print(cycle - 1, (OPCODES[old_imm[0]] if old_imm[0] != 'CB' else OPCODES_CB[old_imm[0]]))
                print(cycle, (OPCODES[imm[0]] if imm[0] != 'CB' else OPCODES_CB[imm[0]]))
                print(old_got)
                print(got)
                print(bin(cpu.mmu.IF))
                return
            #print(bin(cpu.mmu.IF), 3)
            cpu.tick()
            #print(bin(cpu.mmu.IF), 4)
            old_should, old_got, old_imm = should, got, imm
            
    print('CLEARED', filename + '\n')      

    
main()