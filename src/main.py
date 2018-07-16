import controller
from maps import *
import sys
import random
from multiprocessing import Process, Queue
import pygame
from pygame.locals import *
import numpy as np
import tensorflow as tf


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


def pathing_loop(cam_x, cam_y, ai_x, ai_y, output_q):
    path = a_star((int(cam_x), int(cam_y)), (int(ai_x), int(ai_y)), np.array(map_maze))
    output_q.put(path)


def parallel_path(cam_x, cam_y, ai_x, ai_y):
    p = Process(target=pathing_loop, args=(cam_x, cam_y, ai_x, ai_y, pathing_q))
    p.start()
    return p


# Static Vars
width, height = 70, 70
history_len = 10

map_maze = maze(width, height).tolist()
game = controller.Controller(map_maze, sprite_positions,
                             sprite_positions[0], random.choice(player_start))
pathing_q = Queue()
pathing_process = None
path_history = []  # np.zeros([10, 2], np.int8).tolist()
old_map_x, old_map_y = int(game.wm.camera.x), int(game.wm.camera.y)

tf.reset_default_graph()


class Model:
    def __init__(self, history_len=10, hidden_size=128, map_max_size=(70, 70),
                 optimizer=tf.train.AdamOptimizer(learning_rate=0.001)):
        self.loc_history = tf.placeholder(tf.float32, [None, history_len, 2])
        loc_history = tf.reshape(self.loc_history, [-1, history_len * 2])
        self.distance = tf.placeholder(tf.float32, [None, ])
        distance = tf.expand_dims(self.distance, axis=1)
        self.controls = tf.placeholder(tf.float32, [None, 4])
        self.direction = tf.placeholder(tf.float32, [None, 2])
        inputs = [loc_history, distance, self.controls, self.direction]
        inputs = tf.concat(inputs, axis=1)
        print('Inputs shape:', inputs.shape)

        hidden_layer = tf.layers.dense(inputs, hidden_size, tf.nn.sigmoid)
        hidden_layer2 = tf.layers.dense(hidden_layer, hidden_size, tf.nn.sigmoid)
        # TODO: Add layers as needed.

        x = tf.layers.dense(hidden_layer2, 1, tf.nn.sigmoid) * map_max_size[0]
        y = tf.layers.dense(hidden_layer2, 1, tf.nn.sigmoid) * map_max_size[1]

        self.output = tf.concat([x, y], axis=1)
        print('Out shape:', self.output.shape)

        self.player_loc = tf.placeholder(tf.float32, [None, 2])
        self.loss = tf.sqrt(tf.reduce_sum(tf.square(self.output - self.player_loc), reduction_indices=1))
        print("Loss shape:", self.loss.shape)

        self.train = optimizer.minimize(self.loss)


# Array full of (old_state_data, actual_player_position)
path = []
game_buffer = []
previous_inputs = []
sess = tf.Session()
m = Model()
sess.run(tf.global_variables_initializer())
while True:
    # Get player location
    map_x, map_y = int(game.wm.camera.x), int(game.wm.camera.y)

    # if previous state inputs:
    #   append (previous_inputs, current_player_position) to buffer
    #   if it has been n many steps:
    #       train agent with buffer
    #       empty buffer

    if previous_inputs and len(path_history) >= history_len:
        previous_inputs.append((map_x, map_y))
        game_buffer.append(previous_inputs)
        if len(game_buffer) >= 10:
            # Train
            feed_dict = {
                m.loc_history: [item[0] for item in game_buffer],
                m.distance: [item[1] for item in game_buffer],
                m.controls: [item[2] for item in game_buffer],
                m.direction: [item[3] for item in game_buffer],
                m.player_loc: [item[4] for item in game_buffer],
            }
            sess.run(m.train, feed_dict)
            game_buffer = []

    # Updates path history
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
        if 'outputs' in locals():
            dest_x, dest_y = outputs[0][0], outputs[0][1]
        else:
            dest_x, dest_y = game.wm.camera.x, game.wm.camera.y
        pathing_process = parallel_path(dest_x, dest_y, game.wm.ai_camera.x, game.wm.ai_camera.y)

    # Checks for collision between player and ai
    if get_collision(game.wm.camera, game.wm.ai_camera):
        print("Collision")

    # Standard keys setup
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sess.close()
                print("Closing")
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

    if path and len(path) > 1:
        next_square = path[-2]
    else:
        next_square = (0, 0)
    # Run controller frame
    keys_pressed = game.frame(game.wm.camera, game.wm.ai_camera, next_square)
    # print(keys_pressed)

    # run model, predict location
    if len(path_history) >= 10:
        feed_dict = {
            m.loc_history: [path_history],
            m.distance: [len(path)],
            m.controls: [keys_pressed],
            m.direction: [(game.wm.camera.dirx, game.wm.camera.diry)]
        }
        outputs = sess.run(m.output, feed_dict)
        print(outputs, '=', (map_x, map_y), '?')
    # keep track of state inputs used (previous state inputs)
    previous_inputs = [np.array(path_history), len(path), np.array(keys_pressed), np.array([game.wm.camera.dirx, game.wm.camera.diry])]

