import controller
import pygame
import sys
from pygame.locals import *
from maps import *
import random
import time
import numpy as np
from numpy.random import random_integers as rnd


def maze(width=70, height=70, complexity=1, density=1):
    # Only odd shapes
    shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (shape[0] + shape[1])))
    density = int(density * (shape[0] // 2 * shape[1] // 2))
    # Build actual maze
    Z = np.zeros(shape, dtype=np.int8)
    # Fill borders
    Z[0, :] = Z[-1, :] = 2
    Z[:, 0] = Z[:, -1] = 2
    # Make isles
    for i in range(density):
        x, y = rnd(0, shape[1] // 2) * 2, rnd(0, shape[0] // 2) * 2
        Z[y, x] = 2
        for j in range(complexity):
            neighbours = []
            if x > 1:
                neighbours.append((y, x - 2))
            if x < shape[1] - 2:
                neighbours.append((y, x + 2))
            if y > 1:
                neighbours.append((y - 2, x))
            if y < shape[0] - 2:
                neighbours.append((y + 2, x))
            if len(neighbours):
                y_, x_ = neighbours[rnd(0, len(neighbours) - 1)]
                if Z[y_, x_] == 0:
                    Z[y_, x_] = 2
                    Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 2
                    x, y = x_, y_
    return Z


def a_star(start, goal, gen_maze):
    #  The set of nodes already evaluated
    closedSet = []

    #  The set of currently discovered nodes that are not evaluated yet.
    #  Initially, only the start node is known.
    openSet = [start]

    #  For each node, which node it can most efficiently be reached from.
    #  If a node can be reached from many nodes, cameFrom will eventually contain the
    #  most efficient previous step.
    # cameFrom = np.zeros(gen_maze.shape(), dtype=np.int8) # an empty map
    cameFrom = {}

    #  For each node, the total cost of getting from the start node to the goal
    #  by passing by that node. That value is partly known, partly heuristic.
    fScore = np.ones(gen_maze.shape) # map with default value of Infinity

    #  For the first node, that value is completely heuristic.
    fScore[start] = heuristic(start, goal)

    while openSet:
        current = min(openSet) # the node in openSet having the lowest fScore[] value
        neighbors = neigh(current, gen_maze, len(gen_maze), len(gen_maze[0]))
        if current == goal:
            return reconstruct_path(cameFrom, current)

        openSet.remove(current)
        closedSet.append(current)

        # print(neighbors)
        for neighbor in neighbors:
            if neighbor in closedSet:
                continue  # Ignore the neighbor which is already evaluated.

            if neighbor not in openSet:	#  Discover a new node
                openSet.append(neighbor)

            #  This path is the best until now. Record it!
            cameFrom[neighbor] = current
            fScore[neighbor] = heuristic(neighbor, goal)


def reconstruct_path(cameFrom, current):
    total_path = [current]
    while current in cameFrom:
        current = cameFrom[current]
        total_path.append(current)
    total_path.reverse()
    return total_path


# manhattan distance
def heuristic(s, d):
    sx, sy = s
    dx, dy = d
    return abs(dx - sx) + abs(dy - sy)


def neigh(v, m, row, col):
    n = []
    if v[0] > 0:
        node = (v[0] - 1, v[1])
        if m[v[0] - 1][v[1]] != 2:
            n.append(node)
    if v[1] > 0:
        node = (v[0], v[1] - 1)
        if m[v[0]][v[1] - 1] != 2:
            n.append(node)
    if v[0] < row - 1:
        node = (v[0] + 1, v[1])
        if m[v[0] + 1][v[1]] != 2:
            n.append(node)
    if v[1] < col - 1:
        node = (v[0], v[1] + 1)
        if m[v[0]][v[1] + 1] != 2:
            n.append(node)
    return n


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


new_maze = maze()
game = controller.Controller(new_maze, sprite_positions,
                             sprite_positions[0], random.choice(player_start))
clock = time.clock()
map_x, map_y = int(game.wm.camera.x), int(game.wm.camera.y)
path = a_star((map_x, map_y), (69, 69), np.array(new_maze))

while True:

    if time.clock() - clock >= 3:
        map_x, map_y = int(game.wm.camera.x), int(game.wm.camera.y)
        path = a_star((map_x, map_y), (69, 69), np.array(new_maze))
        clock = time.clock()

    # game.wm.camera.x = path[1][0] + .5
    # game.wm.camera.y = path[1][1] + .5

    if get_collision(game.wm.camera, game.wm.ai_camera):
        print("Collision")

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sys.exit()
            if event.key == K_m:
                game.load_map(new_maze, sprite_positions, game.wm.camera, ai_camera=game.wm.ai_camera)
            if event.key == K_n:
                game.load_map(new_maze, sprite_positions, game.wm.camera, ai_camera=game.wm.ai_camera)
            if event.key == K_TAB:
                print(game.clock.get_fps())
        elif event.type == KEYUP:
            pass
        else:
            pass

    game.frame(game.wm.camera, game.wm.ai_camera)

