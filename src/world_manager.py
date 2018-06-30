import pygame
from pygame.locals import *
import math
import functools
    
tex_width = 64
tex_height = 64


class WorldManager(object):

    def __init__(self, world_map, sprite_positions, x, y, dirx, diry, planex, planey):
        self.sprites = [  
              load_image(pygame.image.load("pics/items/barrel.png").convert(), False, color_key=(0, 0, 0)),
              load_image(pygame.image.load("pics/items/pillar.png").convert(), False, color_key=(0, 0, 0)),
              load_image(pygame.image.load("pics/items/greenlight.png").convert(), False, color_key=(0, 0, 0)),
        ]
        
        self.background = None
        self.images = [  
              load_image(pygame.image.load("pics/walls/eagle.png").convert(), False),
              load_image(pygame.image.load("pics/walls/redbrick.png").convert(), False),
              load_image(pygame.image.load("pics/walls/purplestone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/greystone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/bluestone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/mossy.png").convert(), False),
              load_image(pygame.image.load("pics/walls/wood.png").convert(), False),
              load_image(pygame.image.load("pics/walls/colorstone.png").convert(), False),
    
              load_image(pygame.image.load("pics/walls/eagle.png").convert(), True),
              load_image(pygame.image.load("pics/walls/redbrick.png").convert(), True),
              load_image(pygame.image.load("pics/walls/purplestone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/greystone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/bluestone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/mossy.png").convert(), True),
              load_image(pygame.image.load("pics/walls/wood.png").convert(), True),
              load_image(pygame.image.load("pics/walls/colorstone.png").convert(), True),
              ]
        self.camera = Camera(x, y, dirx, diry, planex, planey)
        self.world_map = world_map
        self.sprite_positions = sprite_positions

    def draw(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        # draw background
        if self.background is None:
            self.background = pygame.transform.scale(pygame.image.load("pics/background.png").convert(), (w, h))
        surface.blit(self.background, (0, 0))
        z_buffer = []
        for x in range(w):
            # calculate ray position and direction
            camera_x = float(2 * x / float(w) - 1)  # x-coordinate in camera space
            ray_pos_x = self.camera.x
            ray_pos_y = self.camera.y
            ray_dir_x = self.camera.dirx + self.camera.planex * camera_x
            ray_dir_y = self.camera.diry + self.camera.planey * camera_x
            # which box of the map we're in
            map_x = int(ray_pos_x)
            map_y = int(ray_pos_y)
       
            # length of ray from current position to next x or y-side
            side_dist_x = 0.0
            side_dist_y = 0.0
       
            # length of ray from one x or y-side to next x or y-side
            delta_dist_x = math.sqrt(1 + (ray_dir_y * ray_dir_y) / (ray_dir_x * ray_dir_x))
            if ray_dir_y == 0:
                ray_dir_y = 0.00001
            delta_dist_y = math.sqrt(1 + (ray_dir_x * ray_dir_x) / (ray_dir_y * ray_dir_y))
            perp_wall_dist = 0.0
       
            # what direction to step in x or y-direction (either +1 or -1)
            step_x = 0
            step_y = 0

            hit = 0   # was there a wall hit?
            side = 0  # was a NS or a EW wall hit?
            
            # calculate step and initial sideDist
            if ray_dir_x < 0:
                step_x = - 1
                side_dist_x = (ray_pos_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - ray_pos_x) * delta_dist_x
                
            if ray_dir_y < 0:
                step_y = - 1
                side_dist_y = (ray_pos_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - ray_pos_y) * delta_dist_y
                
            # perform DDA
            while hit == 0:
                # jump to next map square, OR in x - direction, OR in y - direction
                if side_dist_x < side_dist_y:
        
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                # Check if ray has hit a wall
                if self.world_map[map_x][map_y] > 0:
                    hit = 1
            # Calculate distance projected on camera direction (oblique distance will give fisheye effect !)
            if side == 0:
                # perp_wall_dist = fabs((map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x)
                perp_wall_dist = (abs((map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x))
            else:
                perp_wall_dist = (abs((map_y - ray_pos_y + (1 - step_y) / 2) / ray_dir_y))
      
            # Calculate height of line to draw on surface
            if perp_wall_dist == 0:
                perp_wall_dist = 0.000001
            line_height = abs(int(h / perp_wall_dist))
       
            # calculate lowest and highest pixel to fill in current stripe
            draw_start = - line_height / 2 + h / 2
            draw_end = line_height / 2 + h / 2
        
            # texturing calculations
            tex_num = self.world_map[map_x][map_y] - 1  # 1 subtracted from it so that texture 0 can be used!
           
            # calculate value of wall_x
            wall_x = 0  # where exactly the wall was hit
            if side == 1:
                wall_x = ray_pos_x + ((map_y - ray_pos_y + (1 - step_y) / 2) / ray_dir_y) * ray_dir_x
            else:
                wall_x = ray_pos_y + ((map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x) * ray_dir_y
            wall_x -= math.floor(wall_x)
           
            # x coordinate on the texture
            tex_x = int(wall_x * float(tex_width))
            if side == 0 and ray_dir_x > 0:
                tex_x = tex_width - tex_x - 1
            if side == 1 and ray_dir_y < 0:
                tex_x = tex_width - tex_x - 1

            if side == 1:
                tex_num += 8
            if line_height > 10000:
                line_height = 10000
                draw_start = -10000 / 2 + h/2
            surface.blit(pygame.transform.scale(self.images[tex_num][tex_x], (1, line_height)), (x, draw_start))
            z_buffer.append(perp_wall_dist)

        # function to sort sprites
        def sprite_compare(s1, s2):
            import math
            s1_dist = math.sqrt((s1[0] - self.camera.x) ** 2 + (s1[1] - self.camera.y) ** 2)
            s2_dist = math.sqrt((s2[0] - self.camera.x) ** 2 + (s2[1] - self.camera.y) ** 2)
            if s1_dist > s2_dist:
                return -1
            elif s1_dist == s2_dist:
                return 0
            else:
                return 1

        # draw sprites
        self.sprite_positions.sort(key=functools.cmp_to_key(sprite_compare))
        for sprite in self.sprite_positions:
            # translate sprite position to relative to camera
            sprite_x = sprite[0] - self.camera.x
            sprite_y = sprite[1] - self.camera.y
             
            # transform sprite with the inverse camera matrix
            # [ self.camera.planex   self.camera.dirx ] -1 [ self.camera.diry      -self.camera.dirx ]
            # [               ]  =  1/(self.camera.planex*self.camera.diry-self.camera.dirx*self.camera.planey) *   [                 ]
            # [ self.camera.planey   self.camera.diry ]    [ -self.camera.planey  self.camera.planex ]
          
            inv_det = 1.0 / (self.camera.planex * self.camera.diry - self.camera.dirx * self.camera.planey) # required for correct matrix multiplication
          
            transform_x = inv_det * (self.camera.diry * sprite_x - self.camera.dirx * sprite_y)
            transform_y = inv_det * (-self.camera.planey * sprite_x + self.camera.planex * sprite_y) # this is actually the depth inside the surface, that what Z is in 3D
                
            sprite_surface_x = int((w / 2) * (1 + transform_x / transform_y))
          
            # calculate height of the sprite on surface
            sprite_height = abs(int(h / transform_y))  # using "transform_y" instead of the real distance prevents fisheye
            # calculate lowest and highest pixel to fill in current stripe
            draw_start_y = -sprite_height / 2 + h / 2
            draw_end_y = sprite_height / 2 + h / 2
          
            # calculate width of the sprite
            sprite_width = abs( int (h / transform_y))
            draw_start_x = -sprite_width / 2 + sprite_surface_x
            draw_end_x = sprite_width / 2 + sprite_surface_x
            
            if sprite_height < 1000:
                for stripe in range(int(draw_start_x), int(draw_end_x)):
                    tex_x = int(256 * (stripe - (-sprite_width / 2 + sprite_surface_x)) * tex_width / sprite_width) / 256
                    # the conditions in the if are:
                    #  1) it's in front of camera plane so you don't see things behind you
                    #  2) it's on the surface (left)
                    #  3) it's on the surface (right)
                    #  4) ZBuffer, with perpendicular distance
                    if (transform_y > 0 and stripe > 0 and stripe < w and transform_y < z_buffer[stripe]):
                        surface.blit(pygame.transform.scale(self.sprites[sprite[2]][int(tex_x)],
                                                            (1, sprite_height)), (stripe, draw_start_y))

    def new_map(self, world_map):
        self.world_map = world_map
    

class Camera(object):
    def __init__(self, x, y, dirx, diry, planex, planey):
        self.x = float(x)
        self.y = float(y)
        self.dirx = float(dirx)
        self.diry = float(diry)
        self.planex = float(planex)
        self.planey = float(planey)
        

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