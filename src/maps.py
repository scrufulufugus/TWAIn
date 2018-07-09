from numpy.random import random_integers as rnd
import numpy as np


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
        current = min(openSet)  # the node in openSet having the lowest fScore[] value
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


sprite_positions = [
    [19.5, 1.5, 3],  # AI must be mutable

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

player_start = [
    (1.5, 1.5, -1, 0, 0, .66)
    #(1.5, 1.5, 1, -1, 0, .66)
    #(27, 11.5, -1, 0, 0, .66)
]