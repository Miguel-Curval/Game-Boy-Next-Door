from cpu import CPU
from mmu import MMU
from timer import Timer
from ppu import PPU
from apu import APU
from cartridge import Cartridge
from joypad import Joypad


class Gameboy:
    def __init__(self, bootrom, rom, skip_bootrom=False):
        self.timer = Timer()
        self.ppu = PPU()
        self.apu = APU()
        self.joypad = Joypad()
        self.cartridge = Cartridge(rom)
        self.mmu = MMU(bootrom, self.cartridge, self.timer, self.ppu, self.apu, self.joypad)
        self.timer.mmu = self.mmu
        self.ppu.mmu = self.mmu
        self.joypad.mmu = self.mmu
        self.cpu = CPU(self.mmu)
        self.t_cycles = 0
        self.reset(skip_bootrom)
        #if skip_bootrom:
        #    self.ppu.LY = 0x90 # for LY stubbed testing

    def reset(self, skip_bootrom=False):
        self.cpu.reset(skip_bootrom)
        self.mmu.reset(skip_bootrom)
        self.timer.reset(skip_bootrom)
        self.ppu.reset(skip_bootrom)
        self.joypad.reset()
        self.cartridge.reset()

    def run_frame(self):
        while not self.ppu.new_frame:
            self.cpu.handle_interrupts()
            cycles = self.cpu.tick()
            for i in range(cycles // 4):
                self.timer.tick()
                self.ppu.tick()
            self.t_cycles += cycles
        self.ppu.new_frame = False
