import pygame
from pygame.locals import *
import math
import world_manager
import time
import sys


def load_image(image, darken, color_key=None):
    ret = []
    if color_key is not None:
        image.set_colorkey(color_key)
    if darken:
        image.set_alpha(127)
    for i in range(image.get_width()):
        s = pygame.Surface((1, image.get_height())).convert()
        # s.fill((0,0,0))
        s.blit(image, (- i, 0))
        if color_key is not None:
            s.set_colorkey(color_key)
        ret.append(s)
    return ret


def main(world_map, sprite_positions, cord=(22, 11.5, -1, 0, 0, .66)):
    t = time.clock()  # time of current frame
    old_time = 0.0  # time of previous frame
    pygame.mixer.init()
    # pygame.mixer.music.load("Muse_Uprising.mp3")
    # pygame.mixer.music.play(-1)
    size = w, h = 1920, 1080
    pygame.init()
    # cp_info = pygame.display.Info()
    # size = w, h = cp_info.current_w, cp_info.current_h
    window = pygame.display.set_mode(size)
    pygame.display.set_caption("Gh0stenstein")
    screen = pygame.display.get_surface()
    # pixScreen = pygame.surfarray.pixels2d(screen)
    pygame.mouse.set_visible(False)
    # pygame.display.toggle_fullscreen()
    clock = pygame.time.Clock()

    f = pygame.font.SysFont(pygame.font.get_default_font(), 20)

    x, y, dirx, diry, planex, planey = cord
    wm = world_manager.WorldManager(world_map, sprite_positions, x, y, dirx, diry, planex, planey)

    while True:
        clock.tick(30)

        wm.draw(screen)

        # timing for input and FPS counter

        frame_time = float(clock.get_time()) / 1000.0  # frame_time is the time this frame has taken, in seconds
        t = time.clock()
        text = f.render(str(clock.get_fps()), False, (255, 255, 0))
        screen.blit(text, text.get_rect(), text.get_rect())
        pygame.display.flip()

        # speed modifiers
        move_speed = frame_time * 6.0  # the constant value is in squares / second
        rot_speed = frame_time * 2.0  # the constant value is in radians / second

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return
                if event.key == K_m:
                    wm.new_map(world_map)
                if event.key == K_n:
                    wm.new_map(world_map)
            elif event.type == KEYUP:
                pass
            else:
                pass

        keys = pygame.key.get_pressed()
        if keys[K_UP] or keys[K_w]:
            # move forward if no wall in front of you
            move_x = wm.camera.x + wm.camera.dirx * move_speed

            if (world_map[int(move_x)][int(wm.camera.y)] == 0
                    and world_map[int(move_x + 0.1)][int(wm.camera.y)] == 0):
                wm.camera.x += wm.camera.dirx * move_speed
            move_y = wm.camera.y + wm.camera.diry * move_speed

            if (world_map[int(wm.camera.x)][int(move_y)] == 0
                    and world_map[int(wm.camera.x)][int(move_y + 0.1)] == 0):
                wm.camera.y += wm.camera.diry * move_speed

        if keys[K_DOWN] or keys[K_s]:
            # move backwards if no wall behind you
            if (world_map[int(wm.camera.x - wm.camera.dirx * move_speed)][
                int(wm.camera.y)] == 0): wm.camera.x -= wm.camera.dirx * move_speed

            if (world_map[int(wm.camera.x)][
                int(wm.camera.y - wm.camera.diry * move_speed)] == 0): wm.camera.y -= wm.camera.diry * move_speed

        if (keys[K_RIGHT] and not keys[K_DOWN]) or (keys[K_LEFT] and keys[K_DOWN]) \
                or (keys[K_d] and not keys[K_s]) or (keys[K_a] and keys[K_s]):
            # rotate to the right
            # both camera direction and camera plane must be rotated
            old_dir_x = wm.camera.dirx
            wm.camera.dirx = wm.camera.dirx * math.cos(- rot_speed) - wm.camera.diry * math.sin(- rot_speed)
            wm.camera.diry = old_dir_x * math.sin(- rot_speed) + wm.camera.diry * math.cos(- rot_speed)
            old_plane_x = wm.camera.planex
            wm.camera.planex = wm.camera.planex * math.cos(- rot_speed) - wm.camera.planey * math.sin(- rot_speed)
            wm.camera.planey = old_plane_x * math.sin(- rot_speed) + wm.camera.planey * math.cos(- rot_speed)

        if (keys[K_LEFT] and not keys[K_DOWN]) or (keys[K_RIGHT] and keys[K_DOWN]) \
                or (keys[K_a] and not keys[K_s]) or (keys[K_d] and keys[K_s]):
            # rotate to the left
            # both camera direction and camera plane must be rotated
            old_dir_x = wm.camera.dirx
            wm.camera.dirx = wm.camera.dirx * math.cos(rot_speed) - wm.camera.diry * math.sin(rot_speed)
            wm.camera.diry = old_dir_x * math.sin(rot_speed) + wm.camera.diry * math.cos(rot_speed)
            old_plane_x = wm.camera.planex
            wm.camera.planex = wm.camera.planex * math.cos(rot_speed) - wm.camera.planey * math.sin(rot_speed)
            wm.camera.planey = old_plane_x * math.sin(rot_speed) + wm.camera.planey * math.cos(rot_speed)
