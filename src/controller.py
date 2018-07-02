import pygame
from pygame.locals import *
import math
import world_manager
import time
import sys


class Controller(object):

    def __init__(self, world_map, sprite_positions, cord=(22, 11.5, -1, 0, 0, .66)):
        self.t = time.clock()  # time of current frame
        self.old_time = 0.0  # time of previous frame
        pygame.mixer.init()
        # pygame.mixer.music.load("Muse_Uprising.mp3")
        # pygame.mixer.music.play(-1)
        size = w, h = 1920, 1080
        pygame.init()
        self.window = pygame.display.set_mode(size)
        pygame.display.set_caption("idk")
        self.screen = pygame.display.get_surface()
        # pixScreen = pygame.surfarray.pixels2d(screen)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.f = pygame.font.SysFont(pygame.font.get_default_font(), 42)

        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.wm = world_manager.WorldManager(world_map, sprite_positions, cord=cord)

    def load_map(self, world_map, sprite_positions, camera):
        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.wm = world_manager.WorldManager(world_map, sprite_positions, camera=camera)

        print("---------------")
        print("World Manager: " + hex(id(self.wm)))
        print("Map:           " + hex(id(world_map)))
        print("Sprites:       " + hex(id(sprite_positions)))
        print("Camera:        " + hex(id(camera)))
        print("---------------")

    def frame(self, camera):
        self.clock.tick(30)

        world_map = self.world_map

        self.wm.draw(self.screen)
        # self.wm.draw(self.screen).draw_sprites(camera)

        # timing for input and FPS counter

        frame_time = float(self.clock.get_time()) / 1000.0  # frame_time is the time this frame has taken, in seconds
        t = time.clock()
        text = self.f.render(str(round(self.clock.get_fps())), False, (255, 255, 0))
        self.screen.blit(text, text.get_rect(), text.get_rect())
        pygame.display.flip()

        # speed modifiers
        move_speed = frame_time * 6.0  # the constant value is in squares / second
        rot_speed = frame_time * 2.0  # the constant value is in radians / second

        keys = pygame.key.get_pressed()
        if keys[K_w]:
            # move forward if no wall in front of you
            move_x = camera.x + camera.dirx * move_speed

            if (world_map[int(move_x)][int(camera.y)] == 0
                    and world_map[int(move_x + 0.1)][int(camera.y)] == 0):
                camera.x += camera.dirx * move_speed
            move_y = camera.y + camera.diry * move_speed

            if (world_map[int(camera.x)][int(move_y)] == 0
                    and world_map[int(camera.x)][int(move_y + 0.1)] == 0):
                camera.y += camera.diry * move_speed

        if keys[K_s]:
            # move backwards if no wall behind you
            if (world_map[int(camera.x - camera.dirx * move_speed)]
                    [int(camera.y)] == 0):
                camera.x -= camera.dirx * move_speed

            if (world_map[int(camera.x)]
                    [int(camera.y - camera.diry * move_speed)] == 0):
                camera.y -= camera.diry * move_speed

        if (keys[K_d] and not keys[K_s]) or (keys[K_a] and keys[K_s]):
            # rotate to the right
            # both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(- rot_speed) - camera.diry * math.sin(- rot_speed)
            camera.diry = old_dir_x * math.sin(- rot_speed) + camera.diry * math.cos(- rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(-rot_speed) - camera.planey * math.sin(- rot_speed)
            camera.planey = old_plane_x * math.sin(-rot_speed) + camera.planey * math.cos(- rot_speed)

        if (keys[K_a] and not keys[K_s]) or (keys[K_d] and keys[K_s]):
            # rotate to the left
            # both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(rot_speed) - camera.diry * math.sin(rot_speed)
            camera.diry = old_dir_x * math.sin(rot_speed) + camera.diry * math.cos(rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(rot_speed) - camera.planey * math.sin(rot_speed)
            camera.planey = old_plane_x * math.sin(rot_speed) + camera.planey * math.cos(rot_speed)

        # Enemy controls

        if keys[K_UP]:
            # move forward if no wall in front of you
            move_x = camera.x + camera.dirx * move_speed

            if (world_map[int(move_x)][int(camera.y)] == 0
                    and world_map[int(move_x + 0.1)][int(camera.y)] == 0):
                camera.x += camera.dirx * move_speed
            move_y = camera.y + camera.diry * move_speed

            if (world_map[int(camera.x)][int(move_y)] == 0
                    and self.world_map[int(camera.x)][int(move_y + 0.1)] == 0):
                camera.y += camera.diry * move_speed

        if keys[K_DOWN]:
            # move backwards if no wall behind you
            if (world_map[int(camera.x - camera.dirx * move_speed)]
                    [int(camera.y)] == 0):
                camera.x -= camera.dirx * move_speed

            if (world_map[int(camera.x)]
                    [int(camera.y - camera.diry * move_speed)] == 0):
                camera.y -= camera.diry * move_speed

        if (keys[K_RIGHT] and not keys[K_DOWN]) or (keys[K_LEFT] and keys[K_DOWN]):
            # rotate to the right
            # both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(- rot_speed) - camera.diry * math.sin(- rot_speed)
            camera.diry = old_dir_x * math.sin(- rot_speed) + camera.diry * math.cos(- rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(- rot_speed) - camera.planey * math.sin(- rot_speed)
            camera.planey = old_plane_x * math.sin(- rot_speed) + camera.planey * math.cos(- rot_speed)

        if (keys[K_LEFT] and not keys[K_DOWN]) or (keys[K_RIGHT] and keys[K_DOWN]):
            # rotate to the left
            # both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(rot_speed) - camera.diry * math.sin(rot_speed)
            camera.diry = old_dir_x * math.sin(rot_speed) + camera.diry * math.cos(rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(rot_speed) - camera.planey * math.sin(rot_speed)
            camera.planey = old_plane_x * math.sin(rot_speed) + camera.planey * math.cos(rot_speed)
