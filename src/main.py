import controller
import pygame
import sys
from pygame.locals import *
from maps import *
import random
from multiprocessing import Process, Queue


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


# Static Vars
width, height = 20, 20
history_len = 10

map_maze = maze(width, height).tolist()
game = controller.Controller(map_maze, sprite_positions,
                             sprite_positions[0], random.choice(player_start))
pathing_q = Queue()
pathing_process = None
path_history = []
old_map_x, old_map_y = int(game.wm.camera.x), int(game.wm.camera.y)


def pathing_loop(cam_x, cam_y, ai_x, ai_y, output_q):
    path = a_star((int(cam_x), int(cam_y)), (int(ai_x), int(ai_y)), np.array(map_maze))
    output_q.put(path)


def parallel_path(cam_x, cam_y, ai_x, ai_y):
    p = Process(target=pathing_loop, args=(cam_x, cam_y, ai_x, ai_y, pathing_q))
    p.start()
    return p


while True:
    # Updates path history
    map_x, map_y = int(game.wm.camera.x), int(game.wm.camera.y)
    if (old_map_x, old_map_y) != (map_x, map_y):
        old_map_x, old_map_y = map_x, map_y
        path_history.insert(0, (map_x, map_y))
        if len(path_history) > history_len:
            path_history = path_history[:history_len]

    # Runs A*
    if pathing_process:
        if not pathing_q.empty():
            # get path data
            path = pathing_q.get()
            # print(len(path))
            pathing_process.join()
            pathing_process = None
    else:
        pathing_process = parallel_path(game.wm.camera.x, game.wm.camera.y, game.wm.ai_camera.x, game.wm.ai_camera.y)

    # Checks for collision between player and ai
    if get_collision(game.wm.camera, game.wm.ai_camera):
        print("Collision")

    # Standard keys setup
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sys.exit()
            if event.key == K_n:
                map_maze = maze(width, height).tolist()
                game.load_map(map_maze, sprite_positions, game.wm.camera, ai_camera=game.wm.ai_camera)
            if event.key == K_TAB:
                print("------------------------")
                print("FPS is {}".format(int(game.clock.get_fps())))
                print("Location is: {}, {}".format(int(game.wm.camera.x), int(game.wm.camera.y)))
                print("End is {} steps away".format(len(path)))
                print("Last {} steps are: {}".format(history_len, path_history))
                print("------------------------")
        elif event.type == KEYUP:
            pass
        else:
            pass

    # Run controller frame
    game.frame(game.wm.camera, game.wm.ai_camera)
