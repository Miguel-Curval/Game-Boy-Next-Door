#!/usr/bin/env pypy

from gb import Gameboy

import argparse
import pygame

def main():
    parser = argparse.ArgumentParser(description='GameBoy Next Door')
    parser.add_argument('rom_path',
                        metavar='r',
                        type=str,
                        help='path to rom')
    args = parser.parse_args()
    
    with open('dmg_boot.bin', 'rb') as f:
        bootrom = [b for b in f.read()]
    with open(args.rom_path, 'rb') as f:
        rom = [b for b in f.read()]
     
    
    pygame.init()
    gb = Gameboy(bootrom, rom)

    from pygame.locals import QUIT, KEYDOWN, KEYUP
    clock = pygame.time.Clock()
    scale = 4
    scaled_dimensions = (160 * scale, 144 * scale)
    screen = pygame.display.set_mode(scaled_dimensions)
    pygame.display.set_caption('Game Boy Next Door')
    pygame.display.set_icon(pygame.image.load('GBND.ico'))
    gb_framebuffer = gb.ppu.framebuffer
    scaled_img = pygame.Surface((scaled_dimensions), depth=8)
    for i, val in enumerate([0xFF, 0xAA, 0x55, 0x00]):
        scaled_img.set_palette_at(i, (val,) * 3)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    gb.joypad.direction_down(0x1)
                elif event.key == pygame.K_LEFT:
                    gb.joypad.direction_down(0x2)
                elif event.key == pygame.K_UP:
                    gb.joypad.direction_down(0x4)
                elif event.key == pygame.K_DOWN:
                    gb.joypad.direction_down(0x8)
                elif event.key == pygame.K_z:
                    gb.joypad.button_down(0x1)
                elif event.key == pygame.K_x:
                    gb.joypad.button_down(0x2)
                elif event.key == pygame.K_BACKSPACE:
                    gb.joypad.button_down(0x4)
                elif event.key == pygame.K_RETURN:
                    gb.joypad.button_down(0x8)
            elif event.type == KEYUP:
                if event.key == pygame.K_RIGHT:
                    gb.joypad.direction_up(0x1)
                elif event.key == pygame.K_LEFT:
                    gb.joypad.direction_up(0x2)
                elif event.key == pygame.K_UP:
                    gb.joypad.direction_up(0x4)
                elif event.key == pygame.K_DOWN:
                    gb.joypad.direction_up(0x8)
                elif event.key == pygame.K_z:
                    gb.joypad.button_up(0x1)
                elif event.key == pygame.K_x:
                    gb.joypad.button_up(0x2)
                elif event.key == pygame.K_BACKSPACE:
                    gb.joypad.button_up(0x4)
                elif event.key == pygame.K_RETURN:
                    gb.joypad.button_up(0x8)
        gb.run_frame()
        img = pygame.image.frombuffer(bytearray(gb_framebuffer), (160, 144), 'P')
        pygame.transform.scale(img, scaled_dimensions, scaled_img)
        screen.blit(scaled_img, (0, 0))
        pygame.display.flip()
        #clock.tick_busy_loop(60)


    
if __name__ == '__main__':
    main()