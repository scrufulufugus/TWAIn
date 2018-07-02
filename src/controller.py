import pygame
from pygame.locals import *
import math
import world_manager
import time
import sys


class Controller(object):

    def __init__(self, world_map, sprite_positions, cord=(22, 11.5, -1, 0, 0, .66)):
        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.t = time.clock()  # time of current frame
        self.old_time = 0.0  # time of previous frame
        pygame.mixer.init()
        # pygame.mixer.music.load("Muse_Uprising.mp3")
        # pygame.mixer.music.play(-1)
        size = w, h = 1920, 1080
        pygame.init()
        self.window = pygame.display.set_mode(size)
        pygame.display.set_caption("Gh0stenstein")
        self.screen = pygame.display.get_surface()
        # pixScreen = pygame.surfarray.pixels2d(screen)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.f = pygame.font.SysFont(pygame.font.get_default_font(), 42)

        self.cord = cord
        self.wm = world_manager.WorldManager(self.world_map, self.sprite_positions, cord)

    def load_map(self, world_map, sprite_positions):
        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.wm = world_manager.WorldManager(world_map, sprite_positions, self.cord)

    def frame(self):
        self.clock.tick(30)
        self.cord = (self.wm.camera.x, self.wm.camera.y, self.wm.camera.dirx,
                     self.wm.camera.diry, self.wm.camera.planex, self.wm.camera.planey)
        # 0: x, 1: y, 2: dirx, 3: diry, 4: planex 5: planey

        self.wm.draw(self.screen)

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
        if keys[K_UP] or keys[K_w]:
            # move forward if no wall in front of you
            move_x = self.cord[0] + self.cord[2] * move_speed

            if (self.world_map[int(move_x)][int(self.cord[1])] == 0
                    and self.world_map[int(move_x + 0.1)][int(self.cord[1])] == 0):
                self.wm.camera.x += self.cord[2] * move_speed
            move_y = self.cord[1] + self.cord[3] * move_speed

            if (self.world_map[int(self.cord[0])][int(move_y)] == 0
                    and self.world_map[int(self.cord[0])][int(move_y + 0.1)] == 0):
                self.wm.camera.y += self.cord[3] * move_speed

        if keys[K_DOWN] or keys[K_s]:
            # move backwards if no wall behind you
            if (self.world_map[int(self.cord[0] - self.cord[2] * move_speed)]
                    [int(self.cord[1])] == 0):
                self.wm.camera.x -= self.cord[2] * move_speed

            if (self.world_map[int(self.cord[0])]
                    [int(self.cord[1] - self.cord[3] * move_speed)] == 0):
                self.wm.camera.y -= self.cord[3] * move_speed

        if (keys[K_RIGHT] and not keys[K_DOWN]) or (keys[K_LEFT] and keys[K_DOWN]) \
                or (keys[K_d] and not keys[K_s]) or (keys[K_a] and keys[K_s]):
            # rotate to the right
            # both camera direction and camera plane must be rotated
            old_dir_x = self.cord[2]
            self.wm.camera.dirx = self.cord[2] * math.cos(- rot_speed) - self.cord[3] * math.sin(- rot_speed)
            self.wm.camera.diry = old_dir_x * math.sin(- rot_speed) + self.cord[3] * math.cos(- rot_speed)
            old_plane_x = self.cord[4]
            self.wm.camera.planex = self.cord[4] * math.cos(- rot_speed) - self.cord[5] * math.sin(- rot_speed)
            self.wm.camera.planey = old_plane_x * math.sin(- rot_speed) + self.cord[5] * math.cos(- rot_speed)

        if (keys[K_LEFT] and not keys[K_DOWN]) or (keys[K_RIGHT] and keys[K_DOWN]) \
                or (keys[K_a] and not keys[K_s]) or (keys[K_d] and keys[K_s]):
            # rotate to the left
            # both camera direction and camera plane must be rotated
            old_dir_x = self.cord[2]
            self.wm.camera.dirx = self.cord[2] * math.cos(rot_speed) - self.cord[3] * math.sin(rot_speed)
            self.wm.camera.diry = old_dir_x * math.sin(rot_speed) + self.cord[3] * math.cos(rot_speed)
            old_plane_x = self.cord[4]
            self.wm.camera.planex = self.cord[4] * math.cos(rot_speed) - self.cord[5] * math.sin(rot_speed)
            self.wm.camera.planey = old_plane_x * math.sin(rot_speed) + self.cord[5] * math.cos(rot_speed)
