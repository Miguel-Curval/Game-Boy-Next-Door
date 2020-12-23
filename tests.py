# INÚTIL SEM OS LOGS E OS TRACES, só estou a fazer upload para curiosidade dos professores.

#!/usr/bin/env pypy

from gb import Gameboy

def main():
    with open('dmg_boot.bin', 'rb') as f:
        bootrom = [b for b in f.read()]

    for filename in ['01-special',
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
        with open(f'cpu_instrs/traces/{filename}.txt', 'r') as f:
            trace = [line for line in f]
        gb = Gameboy(bootrom, rom, True)
        cpu = gb.cpu
        bc = cpu.get_BC
        de = cpu.get_DE
        hl = cpu.get_HL
        def f(r):
            return '0x' + hex(r)[2:].upper().zfill(4)
        from opcodes import OPCODES, OPCODES_CB
        read = gb.mmu.read
        byte, old_byte = 0, 0
        pc, old_pc= 0, 0
        for cycle, should in enumerate(trace):
            old_pc = pc
            pc = cpu.PC
            old_byte = byte
            byte = read(pc)
            byte1 = read(pc+1)
            byte2 = read(pc+2)
            imm16 = hex(byte1 | (byte2 << 8))
            pc_f = '$' + hex(pc)[2:].upper().zfill(4) + ':'
            gb.tick()
            got = f'[BC={f(bc())}, DE={f(de())}, HL={f(hl())}, AF={f((cpu.A << 8) | cpu.F)}, SP={f(cpu.SP)}]'
            if pc_f != should[:6] or got != should[32:87]:
                print(should)
                print(cycle)
                print(pc_f, hex(old_pc), OPCODES_CB[byte] if byte == 0xCB else OPCODES[byte], got)
                print(imm16)

                return
            
    print('CLEARED', filename + '\n')      

    
main()