import controller
import pygame
import sys
from pygame.locals import *
from maps import *
import random
import numpy as np

world_map = np.zeros((70, 70), np.int64)
world_map[:, 0] = 2
world_map[:, -1] = 2
world_map[0, :] = 2
world_map[-1, :] = 2

world_map = world_map.tolist()

game = controller.Controller(world_map, sprite_positions, ai_sprite=sprite_positions[0], cord=random.choice(player_start))


def get_collision(camera_one, camera_two):
    def get_collider(camera, box_size=1):
        return [camera.x - (box_size / 2), camera.x + (box_size / 2),
                camera.y - (box_size / 2), camera.y + (box_size / 2)]

    collider_one = get_collider(camera_one)
    collider_two = get_collider(camera_two)
    if collider_one[0] <= collider_two[0] <= collider_one[1] or \
            collider_one[0] <= collider_two[1] <= collider_one[1]:
        if collider_one[2] <= collider_two[2] <= collider_one[3] or \
                collider_one[2] <= collider_two[3] <= collider_one[3]:
            return True
    return False


while True:

    if get_collision(game.wm.camera, game.wm.ai_camera):
        print("Collision")

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sys.exit()
            if event.key == K_m:
                game.load_map(world_map_empty, sprite_positions, game.wm.camera, ai_camera=game.wm.ai_camera)
            if event.key == K_n:
                game.load_map(world_map_full, sprite_positions, game.wm.camera, ai_camera=game.wm.ai_camera)
            if event.key == K_TAB:
                print(game.clock.get_fps())
        elif event.type == KEYUP:
            pass
        else:
            pass

    game.frame(game.wm.camera, game.wm.ai_camera)
