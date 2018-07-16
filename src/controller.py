import pygame
from pygame.locals import *
import math
import world_manager
import time


class Controller(object):

    def __init__(self, world_map, sprite_positions, ai_sprite=None, cord=(22, 11.5, -1, 0, 0, .66)):
        pygame.mixer.init()
        # pygame.mixer.music.load("Muse_Uprising.mp3")
        # pygame.mixer.music.play(-1)
        size = 1920, 1080
        pygame.init()
        pygame.display.set_mode(size)
        pygame.display.set_caption("idk")
        self.screen = pygame.display.get_surface()
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()

        self.f = pygame.font.SysFont(pygame.font.get_default_font(), 42)

        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.wm = world_manager.WorldManager(world_map, sprite_positions, cord=cord, ai_sprite=ai_sprite)

    def load_map(self, world_map, sprite_positions, camera, ai_camera):
        self.world_map = world_map
        self.sprite_positions = sprite_positions

        self.wm = world_manager.WorldManager(world_map, sprite_positions, camera=camera, ai_camera=ai_camera)

        print("-----------------------------")
        print("World Manager: " + hex(id(self.wm)))
        print("Map:           " + hex(id(world_map)))
        print("Sprites:       " + hex(id(sprite_positions)))
        print("Ai Camera:     " + hex(id(ai_camera)))
        print("Camera:        " + hex(id(camera)))
        print("-----------------------------")

    def frame(self, camera, ai_camera, squares):
        self.clock.tick(30)

        world_map = self.world_map

        self.wm.draw(self.screen)

        pressed = [0, 0, 0, 0]

        # timing for input and FPS counter

        frame_time = float(self.clock.get_time()) / 1000.0  # frame_time is the time this frame has taken, in seconds
        t = time.clock()
        # print(self.clock.get_fps())
        text = self.f.render(str(round(self.clock.get_fps())), False, (255, 255, 0))
        self.screen.blit(text, text.get_rect(), text.get_rect())
        pygame.display.flip()

        # Speed modifiers
        move_speed = frame_time * 3.0  # the constant value is in squares / second
        rot_speed = frame_time * 2.0  # the constant value is in radians / second
        ai_move_speed = frame_time * 1.0

        # Get pressed keys
        keys = pygame.key.get_pressed()

        if keys[K_w]:
            # Move forward if no wall in front of you
            pressed[0] = 1.0
            move_x = camera.x + camera.dirx * move_speed

            if (world_map[int(move_x)][int(camera.y)] == 0
                    and world_map[int(move_x + 0.1)][int(camera.y)] == 0):
                camera.x += camera.dirx * move_speed
            move_y = camera.y + camera.diry * move_speed

            if (world_map[int(camera.x)][int(move_y)] == 0
                    and world_map[int(camera.x)][int(move_y + 0.1)] == 0):
                camera.y += camera.diry * move_speed

        if keys[K_s]:
            # Move backwards if no wall behind you
            pressed[1] = 1.0
            if (world_map[int(camera.x - camera.dirx * move_speed)]
                    [int(camera.y)] == 0):
                camera.x -= camera.dirx * move_speed

            if (world_map[int(camera.x)]
                    [int(camera.y - camera.diry * move_speed)] == 0):
                camera.y -= camera.diry * move_speed

        if (keys[K_d] and not keys[K_s]) or (keys[K_a] and keys[K_s]):
            # Rotate to the right
            pressed[2] = 1.0
            # Both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(- rot_speed) - camera.diry * math.sin(- rot_speed)
            camera.diry = old_dir_x * math.sin(- rot_speed) + camera.diry * math.cos(- rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(-rot_speed) - camera.planey * math.sin(- rot_speed)
            camera.planey = old_plane_x * math.sin(-rot_speed) + camera.planey * math.cos(- rot_speed)

        if (keys[K_a] and not keys[K_s]) or (keys[K_d] and keys[K_s]):
            # Rotate to the left
            pressed[3] = 1.0
            # Both camera direction and camera plane must be rotated
            old_dir_x = camera.dirx
            camera.dirx = camera.dirx * math.cos(rot_speed) - camera.diry * math.sin(rot_speed)
            camera.diry = old_dir_x * math.sin(rot_speed) + camera.diry * math.cos(rot_speed)
            old_plane_x = camera.planex
            camera.planex = camera.planex * math.cos(rot_speed) - camera.planey * math.sin(rot_speed)
            camera.planey = old_plane_x * math.sin(rot_speed) + camera.planey * math.cos(rot_speed)

        # Enemy controls
        # if squares[0][0] - squares[1][0] != 0:

        # if keys[K_UP]:
        # Move forward if no wall in front of you
        move_x = ai_camera.x + (squares[0] + .5 - round(ai_camera.x, 1)) * ai_move_speed
        # move_x = ai_camera.x + ai_camera.dirx * ai_move_speed

        if (world_map[int(move_x)][int(camera.y)] == 0
                and world_map[int(move_x + 0.1)][int(ai_camera.y)] == 0):
            ai_camera.x += (squares[0] + .5 - round(ai_camera.x, 1)) * ai_move_speed
        move_y = ai_camera.y + (squares[1] + .5 - round(ai_camera.y, 1)) * ai_move_speed

        if (world_map[int(ai_camera.x)][int(move_y)] == 0
                and world_map[int(ai_camera.x)][int(move_y + 0.1)] == 0):
            ai_camera.y += (squares[1] + .5 - round(ai_camera.y, 1)) * ai_move_speed

        # print("Gabe Tracker: ({}, {}) moving to {}".format(round(ai_camera.x, 1), round(ai_camera.y, 1), squares))

        '''
        if keys[K_DOWN]:
            # Move backwards if no wall behind you
            if (world_map[int(ai_camera.x - ai_camera.dirx * ai_move_speed)]
                    [int(ai_camera.y)] == 0):
                ai_camera.x -= ai_camera.dirx * ai_move_speed

            if (world_map[int(ai_camera.x)]
                    [int(ai_camera.y - ai_camera.diry * ai_move_speed)] == 0):
                ai_camera.y -= ai_camera.diry * ai_move_speed

        if (keys[K_RIGHT] and not keys[K_DOWN]) or (keys[K_LEFT] and keys[K_DOWN]):
            # Rotate to the right
            # Both camera direction and camera plane must be rotated
            old_dir_x = ai_camera.dirx
            ai_camera.dirx = ai_camera.dirx * math.cos(- rot_speed) - ai_camera.diry * math.sin(- rot_speed)
            ai_camera.diry = old_dir_x * math.sin(- rot_speed) + ai_camera.diry * math.cos(- rot_speed)
            old_plane_x = ai_camera.planex
            ai_camera.planex = ai_camera.planex * math.cos(- rot_speed) - ai_camera.planey * math.sin(- rot_speed)
            ai_camera.planey = old_plane_x * math.sin(- rot_speed) + ai_camera.planey * math.cos(- rot_speed)

        if (keys[K_LEFT] and not keys[K_DOWN]) or (keys[K_RIGHT] and keys[K_DOWN]):
            # Rotate to the left
            # Both camera direction and camera plane must be rotated
            old_dir_x = ai_camera.dirx
            ai_camera.dirx = ai_camera.dirx * math.cos(rot_speed) - ai_camera.diry * math.sin(rot_speed)
            ai_camera.diry = old_dir_x * math.sin(rot_speed) + ai_camera.diry * math.cos(rot_speed)
            old_plane_x = ai_camera.planex
            ai_camera.planex = ai_camera.planex * math.cos(rot_speed) - ai_camera.planey * math.sin(rot_speed)
            ai_camera.planey = old_plane_x * math.sin(rot_speed) + ai_camera.planey * math.cos(rot_speed)
        '''

        ai_camera.sprite[0] = ai_camera.x
        ai_camera.sprite[1] = ai_camera.y

        return pressed
