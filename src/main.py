# from controller import Controller
import controller
import pygame
import sys
from pygame.locals import *
from maps import *

sprite_positions = [
    [0, 0, 3],  # AI must be mutable

    (20.5, 11.5, 2),  # green light in front of playerstart
    # green lights in every room
    (18.5, 4.5, 2),
    (10.0, 4.5, 2),
    (10.0, 12.5, 2),
    (3.5, 6.5, 2),
    (3.5, 20.5, 2),
    (3.5, 14.5, 2),
    (14.5, 20.5, 2),

    # row of pillars in front of wall: fisheye test
    (18.5, 10.5, 1),
    (18.5, 11.5, 1),
    (18.5, 12.5, 1),

    # some barrels around the map
    (21.5, 1.5, 0),
    (15.5, 1.5, 0),
    (16.0, 1.8, 0),
    (16.2, 1.2, 0),
    (3.5, 2.5, 0),
    (9.5, 15.5, 0),
    (10.0, 15.1, 0),
    (10.5, 15.8, 0)
]

sprite_zero = []

game = controller.Controller(world_map_empty, sprite_positions, ai_sprite=sprite_positions[0])

space = 0

while True:
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

    # if space < 70:
    #     world_map_large[space][3] = 1
    # space += 1

    game.frame(game.wm.camera, game.wm.ai_camera)
