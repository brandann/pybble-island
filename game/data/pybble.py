import pygame

#region pybble
clock = pygame.time.Clock()
FPS = 60
######################################################
#
#  Simple Test - Super simple way to render a tiled map
#
######################################################
class TiledRenderer(object):

    def __init__(self, filename):
        tm = load_pygame(filename)

        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.pixel_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    def get_layers(self):
        layers = {}
        for l in self.tmx_data.visible_layers:
            if isinstance(l,TiledTileLayer):
                layers[l.name] = l
        return layers

    def render_map_layer(self, surface, delta_x, delta_y, layer):
        # fill the background color of our render surface
        if self.tmx_data.background_color:
            surface.fill(pygame.Color(self.tmx_data.background_color))

        if isinstance(layer, TiledTileLayer):
            self.render_tile_layer(surface, layer, delta_x, delta_y)

    def render_map(self, surface, delta_x = 0, delta_y = 0):

        # fill the background color of our render surface
        if self.tmx_data.background_color:
            surface.fill(pygame.Color(self.tmx_data.background_color))

        # iterate over all the visible layers, then draw them
        for layer in self.tmx_data.visible_layers:
            # each layer can be handled differently by checking their type
            colliders = []
            if isinstance(layer, TiledTileLayer):
                return self.render_tile_layer(surface, layer, delta_x, delta_y)

    def render_tile_layer(self, surface, layer, delta_x = 0, delta_y = 0):

        # deref these heavily used references for speed
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        surface_blit = surface.blit

        # iterate over the tiles in the layer, and blit them
        for x, y, image in layer.tiles():
            surface_blit(image, (x * tw - delta_x, y * th - delta_y))

    def get_layer_colliders(self, layer):
        colliders = []
        for x, y, image in layer.tiles():
            colliders.append(pygame.Rect(x*self.tmx_data.tilewidth,y*self.tmx_data.tileheight,self.tmx_data.tilewidth, self.tmx_data.tileheight))
        return  colliders

    def render_image_layer(self, surface, layer):

        if layer.image:
            surface.blit(layer.image, (0, 0))

    def width(self):
        return self.pixel_size[0]
    def height(self):
        return self.pixel_size[1]


######################################################
#
#  Simple Test - Basic app to display a rendered Tiled map
#
######################################################
class SimpleTest(object):

    def __init__(self, filename):
        self.renderer = None
        self.layers = {}
        self.BACKGROUND = 'background'
        self.BOUNDRY = 'boundries'
        self.ASTAR = 'astar'
        self.FOREGROUND = 'foreground'
        self.GAMEOBJECTS = 'gameobjects'
        self.load_map(filename)

    def load_map(self, filename):
        self.renderer = TiledRenderer(filename)
        self.layers = self.renderer.get_layers()

    def draw(self, surface, delta_x = 0, delta_y = 0):
        # first we make a temporary surface that will accommodate the entire
        # size of the map.
        # because this demo does not implement scrolling, we render the
        # entire map each frame
        temp = pygame.Surface(surface.get_size())

        # render the map onto the temporary surface
        self.renderer.render_map(temp, delta_x, delta_y)

        surface.blit(temp, (0,0))

        # now resize the temporary surface to the size of the display
        # this will also 'blit' the temp surface to the display
        #pygame.transform.smoothscale(temp, surface.get_size(), surface)

    def size(self):
        return self.renderer.size

    def draw_background_layer(self, surface, delta_x, delta_y):
        self.renderer.render_map_layer(surface, delta_x, delta_y, self.layers[self.BACKGROUND])

    def draw_boundry_layer(self, surface, delta_x, delta_y):
        self.renderer.render_map_layer(surface, delta_x, delta_y, self.layers[self.BOUNDRY])

    def draw_foreground_layer(self, surface, delta_x, delta_y):
        self.renderer.render_map_layer(surface, delta_x, delta_y, self.layers[self.FOREGROUND])

    def create_object_layer(self):
        objects = []
        return objects

    def create_astar_layer(self):
        astar_map = []
        return astar_map

    def get_boundry(self):
        return self.renderer.get_layer_colliders(self.layers[self.BOUNDRY])

def bind_rect_inside(outer_rect, inner_rect):
    if inner_rect.left < outer_rect.left:
        inner_rect.left = outer_rect.left
    if inner_rect.right > outer_rect.right:
        inner_rect.right = outer_rect.right
    if inner_rect.top < outer_rect.top:
        inner_rect.top = outer_rect.top
    if inner_rect.bottom > outer_rect.bottom:
        inner_rect.bottom = outer_rect.bottom



def move(rect, movement, tiles):

    # dictionary of hits
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

    # collide with x tiles
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        if movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    # collide with y tiles
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        if movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True

    return rect, collision_types
#endregion

#region DaFluffyPotato
import pygame, math, os
from pygame.locals import *

global e_colorkey
e_colorkey = (255, 255, 255)


def set_global_colorkey(colorkey):
    global e_colorkey
    e_colorkey = colorkey


# physics core

# 2d collisions test
def collision_test(object_1, object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_1):
            collision_list.append(obj)
    return collision_list


# 2d physics object
class physics_obj(object):

    def __init__(self, x, y, x_size, y_size):
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x = x
        self.y = y

    def move(self, movement, platforms, ramps=[]):
        self.x += movement[0]
        self.rect.x = int(self.x)
        block_hit_list = collision_test(self.rect, platforms)
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False, 'slant_bottom': False,
                           'data': []}
        # added collision data to "collision_types". ignore the poorly chosen variable name
        for block in block_hit_list:
            markers = [False, False, False, False]
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
                markers[0] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
                markers[1] = True
            collision_types['data'].append([block, markers])
            self.x = self.rect.x
        self.y += movement[1]
        self.rect.y = int(self.y)
        block_hit_list = collision_test(self.rect, platforms)
        for block in block_hit_list:
            markers = [False, False, False, False]
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
                markers[2] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
                markers[3] = True
            collision_types['data'].append([block, markers])
            self.change_y = 0
            self.y = self.rect.y
        return collision_types


# 3d collision detection
# todo: add 3d physics-based movement

class cuboid(object):

    def __init__(self, x, y, z, x_size, y_size, z_size):
        self.x = x
        self.y = y
        self.z = z
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size

    def set_pos(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def collidecuboid(self, cuboid_2):
        cuboid_1_xy = pygame.Rect(self.x, self.y, self.x_size, self.y_size)
        cuboid_1_yz = pygame.Rect(self.y, self.z, self.y_size, self.z_size)
        cuboid_2_xy = pygame.Rect(cuboid_2.x, cuboid_2.y, cuboid_2.x_size, cuboid_2.y_size)
        cuboid_2_yz = pygame.Rect(cuboid_2.y, cuboid_2.z, cuboid_2.y_size, cuboid_2.z_size)
        if (cuboid_1_xy.colliderect(cuboid_2_xy)) and (cuboid_1_yz.colliderect(cuboid_2_yz)):
            return True
        else:
            return False


# entity stuff

def simple_entity(x, y, e_type):
    return entity(x, y, 1, 1, e_type)


def flip(img, boolean=True):
    return pygame.transform.flip(img, boolean, False)


def blit_center(surf, surf2, pos):
    x = int(surf2.get_width() / 2)
    y = int(surf2.get_height() / 2)
    surf.blit(surf2, (pos[0] - x, pos[1] - y))


class entity(object):
    global animation_database, animation_higher_database

    def __init__(self, x, y, size_x, size_y, e_type):  # x, y, size_x, size_y, type
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.obj = physics_obj(x, y, size_x, size_y)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = [0, 0]
        self.rotation = 0
        self.type = e_type  # used to determine animation set among other things
        self.action_timer = 0
        self.action = ''
        self.set_action('idle')  # overall action for the entity
        self.entity_data = {}
        self.alpha = None

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def move(self, momentum, platforms, ramps=[]):
        collisions = self.obj.move(momentum, platforms, ramps)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size_x, self.size_y)

    def set_flip(self, boolean):
        self.flip = boolean

    def set_animation_tags(self, tags):
        self.animation_tags = tags

    def set_animation(self, sequence):
        self.animation = sequence
        self.animation_frame = 0

    def set_action(self, action_id, force=False):
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_database[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def get_entity_angle(self, entity_2):
        x1 = self.x + int(self.size_x / 2)
        y1 = self.y + int(self.size_y / 2)
        x2 = entity_2.x + int(entity_2.size_x / 2)
        y2 = entity_2.y + int(entity_2.size_y / 2)
        angle = math.atan((y2 - y1) / (x2 - x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        x = self.x + int(self.size_x / 2)
        y = self.y + int(self.size_y / 2)
        return [x, y]

    def clear_animation(self):
        self.animation = None

    def set_image(self, image):
        self.image = image

    def set_offset(self, offset):
        self.offset = offset

    def set_frame(self, amount):
        self.animation_frame = amount

    def handle(self):
        self.action_timer += 1
        self.change_frame(1)

    def change_frame(self, amount):
        self.animation_frame += amount
        if self.animation != None:
            while self.animation_frame < 0:
                if 'loop' in self.animation_tags:
                    self.animation_frame += len(self.animation)
                else:
                    self.animation = 0
            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                else:
                    self.animation_frame = len(self.animation) - 1

    def get_current_img(self):
        if self.animation == None:
            if self.image != None:
                return flip(self.image, self.flip)
            else:
                return None
        else:
            return flip(animation_database[self.animation[self.animation_frame]], self.flip)

    def get_drawn_img(self):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image, self.flip).copy()
        else:
            image_to_render = flip(animation_database[self.animation[self.animation_frame]], self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width() / 2
            center_y = image_to_render.get_height() / 2
            image_to_render = pygame.transform.rotate(image_to_render, self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            return image_to_render, center_x, center_y

    def display(self, surface, scroll):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image, self.flip).copy()
        else:
            image_to_render = flip(animation_database[self.animation[self.animation_frame]], self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width() / 2
            center_y = image_to_render.get_height() / 2
            image_to_render = pygame.transform.rotate(image_to_render, self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface, image_to_render, (
            int(self.x) - scroll[0] + self.offset[0] + center_x, int(self.y) - scroll[1] + self.offset[1] + center_y))


# animation stuff

global animation_database
animation_database = {}

global animation_higher_database
animation_higher_database = {}


# a sequence looks like [[0,1],[1,1],[2,1],[3,1],[4,2]]
# the first numbers are the image name(as integer), while the second number shows the duration of it in the sequence
def animation_sequence(sequence, base_path, colorkey=(255, 255, 255), transparency=255):
    global animation_database
    result = []
    for frame in sequence:
        image_id = base_path + base_path.split('/')[-2] + '_' + str(frame[0])
        image = pygame.image.load(image_id + '.png').convert()
        image.set_colorkey(colorkey)
        image.set_alpha(transparency)
        animation_database[image_id] = image.copy()
        for i in range(frame[1]):
            result.append(image_id)
    return result


def get_frame(ID):
    global animation_database
    return animation_database[ID]


def load_animations(path):
    global animation_higher_database, e_colorkey
    f = open(path + 'entity_animations.txt', 'r')
    data = f.read()
    f.close()
    for animation in data.split('\n'):
        sections = animation.split(' ')
        anim_path = sections[0]
        entity_info = anim_path.split('/')
        entity_type = entity_info[0]
        animation_id = entity_info[1]
        timings = sections[1].split(';')
        tags = sections[2].split(';')
        sequence = []
        n = 0
        for timing in timings:
            sequence.append([n, int(timing)])
            n += 1
        anim = animation_sequence(sequence, path + anim_path, e_colorkey)
        if entity_type not in animation_higher_database:
            animation_higher_database[entity_type] = {}
        animation_higher_database[entity_type][animation_id] = [anim.copy(), tags]


# particles

def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3


global particle_images
particle_images = {}


def load_particle_images(path):
    global particle_images, e_colorkey
    file_list = os.listdir(path)
    for folder in file_list:
        try:
            img_list = os.listdir(path + '/' + folder)
            img_list = particle_file_sort(img_list)
            images = []
            for img in img_list:
                images.append(pygame.image.load(path + '/' + folder + '/' + img).convert())
            for img in images:
                img.set_colorkey(e_colorkey)
            particle_images[folder] = images.copy()
        except:
            pass


class particle(object):

    def __init__(self, x, y, particle_type, motion, decay_rate, start_frame, custom_color=None):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion
        self.decay_rate = decay_rate
        self.color = custom_color
        self.frame = start_frame

    def draw(self, surface, scroll):
        global particle_images
        if self.frame > len(particle_images[self.type]) - 1:
            self.frame = len(particle_images[self.type]) - 1
        if self.color == None:
            blit_center(surface, particle_images[self.type][int(self.frame)], (self.x - scroll[0], self.y - scroll[1]))
        else:
            blit_center(surface, swap_color(particle_images[self.type][int(self.frame)], (255, 255, 255), self.color),
                        (self.x - scroll[0], self.y - scroll[1]))

    def update(self):
        self.frame += self.decay_rate
        running = True
        if self.frame > len(particle_images[self.type]) - 1:
            running = False
        self.x += self.motion[0]
        self.y += self.motion[1]
        return running


# other useful functions

def swap_color(img, old_c, new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    surf.set_colorkey(e_colorkey)
    return surf


#endregion

#region util_pygame
# -*- coding: utf-8 -*-
"""

util_pygame.py

#######################################################

Copyright (C) 2012-2017, Leif Theden <leif.theden@gmail.com>

This file is part of pytmx.

pytmx is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

pytmx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with pytmx.  If not, see <http://www.gnu.org/licenses/>.
"""
import itertools
import logging

#import pytmx

logger = logging.getLogger(__name__)

try:
    from pygame.transform import flip, rotate
    import pygame
except ImportError:
    logger.error('cannot import pygame (is it installed?)')
    raise

__all__ = ['load_pygame', 'pygame_image_loader', 'simplify', 'build_rects']


def handle_transformation(tile, flags):
    if flags.flipped_diagonally:
        tile = flip(rotate(tile, 270), 1, 0)
    if flags.flipped_horizontally or flags.flipped_vertically:
        tile = flip(tile, flags.flipped_horizontally, flags.flipped_vertically)
    return tile


def smart_convert(original, colorkey, pixelalpha):
    """
    this method does several interactive_tests on a surface to determine the optimal
    flags and pixel format for each tile surface.

    this is done for the best rendering speeds and removes the need to
    convert() the images on your own
    """
    # tiled set a colorkey
    if colorkey:
        tile = original.convert()
        tile.set_colorkey(colorkey, pygame.RLEACCEL)
        # TODO: if there is a colorkey, count the colorkey pixels to determine if RLEACCEL sould be used

    # no colorkey, so use a mask to determine if there are transparent pixels
    else:
        tile_size = original.get_size()
        threshold = 254  # the default

        try:
            # count the number of pixels in the tile that are not transparent
            px = pygame.mask.from_surface(original, threshold).count()
        except:
            # pygame_sdl2 will fail because the mask module is not included
            # in this case, just convert_alpha and return it
            return original.convert_alpha()

        # there are no transparent pixels in the image
        if px == tile_size[0] * tile_size[1]:
            tile = original.convert()

        # there are transparent pixels, and set for perpixel alpha
        elif pixelalpha:
            tile = original.convert_alpha()

        # there are transparent pixels, and we won't handle them
        else:
            tile = original.convert()

    return tile


def pygame_image_loader(filename, colorkey, **kwargs):
    """ pytmx image loader for pygame

    :param filename:
    :param colorkey:
    :param kwargs:
    :return:
    """
    if colorkey:
        colorkey = pygame.Color('#{0}'.format(colorkey))

    pixelalpha = kwargs.get('pixelalpha', True)
    image = pygame.image.load(filename)

    def load_image(rect=None, flags=None):
        if rect:
            try:
                tile = image.subsurface(rect)
            except ValueError:
                logger.error('Tile bounds outside bounds of tileset image')
                raise
        else:
            tile = image.copy()

        if flags:
            tile = handle_transformation(tile, flags)

        tile = smart_convert(tile, colorkey, pixelalpha)
        return tile

    return load_image


def load_pygame(filename, *args, **kwargs):
    """ Load a TMX file, images, and return a TiledMap class

    PYGAME USERS: Use me.

    this utility has 'smart' tile loading.  by default any tile without
    transparent pixels will be loaded for quick blitting.  if the tile has
    transparent pixels, then it will be loaded with per-pixel alpha.  this is
    a per-tile, per-image check.

    if a color key is specified as an argument, or in the tmx data, the
    per-pixel alpha will not be used at all. if the tileset's image has colorkey
    transparency set in Tiled, the util_pygam will return images that have their
    transparency already set.

    TL;DR:
    Don't attempt to convert() or convert_alpha() the individual tiles.  It is
    already done for you.
    """
    kwargs['image_loader'] = pygame_image_loader
    return TiledMap(filename, *args, **kwargs)


def build_rects(tmxmap, layer, tileset=None, real_gid=None):
    """generate a set of non-overlapping rects that represents the distribution
       of the specified gid.

    useful for generating rects for use in collision detection

    Use at your own risk: this is experimental...will change in future

    GID Note: You will need to add 1 to the GID reported by Tiled.

    :param tmxmap: TiledMap object
    :param layer: int or string name of layer
    :param tileset: int or string name of tileset
    :param real_gid: Tiled GID of the tile + 1 (see note)
    :return: List of pygame Rect objects
    """
    if isinstance(tileset, int):
        try:
            tileset = tmxmap.tilesets[tileset]
        except IndexError:
            msg = "Tileset #{0} not found in map {1}."
            logger.debug(msg.format(tileset, tmxmap))
            raise IndexError

    elif isinstance(tileset, str):
        try:
            tileset = [t for t in tmxmap.tilesets if t.name == tileset].pop()
        except IndexError:
            msg = "Tileset \"{0}\" not found in map {1}."
            logger.debug(msg.format(tileset, tmxmap))
            raise ValueError

    elif tileset:
        msg = "Tileset must be either a int or string. got: {0}"
        logger.debug(msg.format(type(tileset)))
        raise TypeError

    gid = None
    if real_gid:
        try:
            gid, flags = tmxmap.map_gid(real_gid)[0]
        except IndexError:
            msg = "GID #{0} not found"
            logger.debug(msg.format(real_gid))
            raise ValueError

    if isinstance(layer, int):
        layer_data = tmxmap.get_layer_data(layer)
    elif isinstance(layer, str):
        try:
            layer = [l for l in tmxmap.layers if l.name == layer].pop()
            layer_data = layer.data
        except IndexError:
            msg = "Layer \"{0}\" not found in map {1}."
            logger.debug(msg.format(layer, tmxmap))
            raise ValueError

    p = itertools.product(range(tmxmap.width), range(tmxmap.height))
    if gid:
        points = [(x, y) for (x, y) in p if layer_data[y][x] == gid]
    else:
        points = [(x, y) for (x, y) in p if layer_data[y][x]]

    rects = simplify(points, tmxmap.tilewidth, tmxmap.tileheight)
    return rects


def simplify(all_points, tilewidth, tileheight):
    """Given a list of points, return list of rects that represent them
    kludge:

    "A kludge (or kluge) is a workaround, a quick-and-dirty solution,
    a clumsy or inelegant, yet effective, solution to a problem, typically
    using parts that are cobbled together."

    -- wikipedia

    turn a list of points into a rects
    adjacent rects will be combined.

    plain english:
        the input list must be a list of tuples that represent
        the areas to be combined into rects
        the rects will be blended together over solid groups

        so if data is something like:

        0 1 1 1 0 0 0
        0 1 1 0 0 0 0
        0 0 0 0 0 4 0
        0 0 0 0 0 4 0
        0 0 0 0 0 0 0
        0 0 1 1 1 1 1

        you'll have the 4 rects that mask the area like this:

        ..######......
        ..####........
        ..........##..
        ..........##..
        ..............
        ....##########

        pretty cool, right?

    there may be cases where the number of rectangles is not as low as possible,
    but I haven't found that it is excessively bad.  certainly much better than
    making a list of rects, one for each tile on the map!
    """

    def pick_rect(points, rects):
        ox, oy = sorted([(sum(p), p) for p in points])[0][1]
        x = ox
        y = oy
        ex = None

        while 1:
            x += 1
            if not (x, y) in points:
                if ex is None:
                    ex = x - 1

                if (ox, y + 1) in points:
                    if x == ex + 1:
                        y += 1
                        x = ox

                    else:
                        y -= 1
                        break
                else:
                    if x <= ex: y -= 1
                    break

        c_rect = pygame.Rect(ox * tilewidth, oy * tileheight,
                             (ex - ox + 1) * tilewidth,
                             (y - oy + 1) * tileheight)

        rects.append(c_rect)

        rect = pygame.Rect(ox, oy, ex - ox + 1, y - oy + 1)
        kill = [p for p in points if rect.collidepoint(p)]
        [points.remove(i) for i in kill]

        if points:
            pick_rect(points, rects)

    rect_list = []
    while all_points:
        pick_rect(all_points, rect_list)

    return rect_list
#endregion

#region pytmx
"""
pytmx.py

#######################################################

Copyright (C) 2012-2020, Leif Theden <leif.theden@gmail.com>

This file is part of pytmx.

pytmx is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

pytmx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with pytmx.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import os
from collections import defaultdict, namedtuple
from io import BytesIO
from itertools import chain, product
from math import cos, radians, sin
from operator import attrgetter
from xml.etree import ElementTree

__all__ = (
    'TiledElement',
    'TiledMap',
    'TiledTileset',
    'TiledTileLayer',
    'TiledObject',
    'TiledObjectGroup',
    'TiledImageLayer',
    'TileFlags',
    'convert_to_bool',
    'parse_properties')

logger = logging.getLogger(__name__)

# internal flags
TRANS_FLIPX = 1
TRANS_FLIPY = 2
TRANS_ROT = 4

# Tiled gid flags
GID_TRANS_FLIPX = 1 << 31
GID_TRANS_FLIPY = 1 << 30
GID_TRANS_ROT = 1 << 29

# error message format strings go here
duplicate_name_fmt = 'Cannot set user {} property on {} "{}"; Tiled property already exists.'

flag_names = (
    'flipped_horizontally',
    'flipped_vertically',
    'flipped_diagonally')

AnimationFrame = namedtuple('AnimationFrame', ['gid', 'duration'])
Point = namedtuple("Point", ["x", "y"])
TileFlags = namedtuple('TileFlags', flag_names)


def default_image_loader(filename, flags, **kwargs):
    """ This default image loader just returns filename, rect, and any flags
    """

    def load(rect=None, flags=None):
        return filename, rect, flags

    return load


def decode_gid(raw_gid):
    """ Decode a GID from TMX data

    as of 0.7.0 it determines if the tile should be flipped when rendered
    as of 0.8.0 bit 30 determines if GID is rotated

    :param raw_gid: 32-bit number from TMX layer data
    :return: gid, flags
    """
    flags = TileFlags(
        raw_gid & GID_TRANS_FLIPX == GID_TRANS_FLIPX,
        raw_gid & GID_TRANS_FLIPY == GID_TRANS_FLIPY,
        raw_gid & GID_TRANS_ROT == GID_TRANS_ROT)
    gid = raw_gid & ~(GID_TRANS_FLIPX | GID_TRANS_FLIPY | GID_TRANS_ROT)
    return gid, flags


def convert_to_bool(value):
    """ Convert a few common variations of "true" and "false" to boolean

    :param Any value: string to test
    :rtype: boolean
    :raises: ValueError
    """
    value = str(value).strip()
    if value:
        value = value.lower()[0]
        if value in ("1", "y", "t"):
            return True
        if value in ("-", "0", "n", "f"):
            return False
    else:
        return False
    raise ValueError('cannot parse "{}" as bool'.format(value))


def rotate(points, origin, angle):
    sin_t = sin(radians(angle))
    cos_t = cos(radians(angle))
    new_points = list()
    for point in points:
        p = (
            origin.x + (cos_t * (point.x - origin.x) - sin_t * (point.y - origin.y)),
            origin.y + (sin_t * (point.x - origin.x) + cos_t * (point.y - origin.y)),
        )
        new_points.append(p)
    return new_points


# used to change the unicode string returned from xml to
# proper python variable types.
types = defaultdict(lambda: str)

types.update({
    "version": str,
    "tiledversion": str,
    "orientation": str,
    "renderorder": str,
    "width": float,
    "height": float,
    "tilewidth": int,
    "tileheight": int,
    "hexsidelength": float,
    "staggeraxis": str,
    "staggerindex": str,
    "backgroundcolor": str,
    "nextobjectid": int,
    "firstgid": int,
    "source": str,
    "name": str,
    "spacing": int,
    "margin": int,
    "tilecount": int,
    "columns": int,
    "format": str,
    "trans": str,
    "tile": int,
    "terrain": str,
    "probability": float,
    "tileid": int,
    "duration": int,
    "color": str,
    "id": int,
    "opacity": float,
    "visible": convert_to_bool,
    "offsetx": int,
    "offsety": int,
    "encoding": str,
    "compression": str,
    "draworder": str,
    "points": str,
    "fontfamily": str,
    "pixelsize": float,
    "wrap": convert_to_bool,
    "bold": convert_to_bool,
    "italic": convert_to_bool,
    "underline": convert_to_bool,
    "strikeout": convert_to_bool,
    "kerning": convert_to_bool,
    "halign": str,
    "valign": str,
    "gid": int,
    "type": str,
    "x": float,
    "y": float,
    "value": str,
    "rotation": float,
})

# casting for properties type
prop_type = {
    'string': str,
    'int': int,
    'float': float,
    'bool': convert_to_bool,
    'color': str,
    'file': str,
    'object': int,
}


def parse_properties(node):
    """ Parse a Tiled xml node and return a dict that represents a tiled "property"

    :param node: etree element
    :return: dict
    """
    d = dict()
    for child in node.findall('properties'):
        for subnode in child.findall('property'):
            cls = None
            try:
                if "type" in subnode.keys():
                    cls = prop_type[subnode.get("type")]
            except AttributeError:
                logger.info("Type {} Not a built-in type. Defaulting to string-cast.".format(subnode.get("type")))
            d[subnode.get('name')] = subnode.get('value') or subnode.text
            if cls is not None:
                d[subnode.get('name')] = cls(subnode.get('value'))
    return d


class TiledElement(object):
    """ Base class for all pytmx types
    """
    allow_duplicate_names = False

    def __init__(self):
        self.properties = dict()

    @classmethod
    def from_xml_string(cls, xml_string):
        """Return a TileElement object from a xml string

        :param xml_string: string containing xml data
        :rtype: TiledElement instance
        """
        return cls().parse_xml(ElementTree.fromstring(xml_string))

    def _cast_and_set_attributes_from_node_items(self, items):
        for key, value in items:
            casted_value = types[key](value)
            setattr(self, key, casted_value)

    def _contains_invalid_property_name(self, items):
        if self.allow_duplicate_names:
            return False

        for k, v in items:
            # i'm not sure why, but this hasattr causes problems on python 2.7 with unicode
            try:
                # this will be called in py 3+
                _hasattr = hasattr(self, k)
            except UnicodeError:
                # this will be called in py 2.7
                _hasattr = hasattr(self, k.encode('utf-8'))

            if _hasattr:
                msg = duplicate_name_fmt.format(k, self.__class__.__name__, self.name)
                logger.error(msg)
                return True
        return False

    @staticmethod
    def _log_property_error_message():
        msg = 'Some name are reserved for {0} objects and cannot be used.'
        logger.error(msg)

    def _set_properties(self, node):
        """ Create dict containing Tiled object attributes from xml data

        read the xml attributes and tiled "properties" from a xml node and fill
        in the values into the object's dictionary.  Names will be checked to
        make sure that they do not conflict with reserved names.

        :param node: etree element
        :return: dict
        """
        self._cast_and_set_attributes_from_node_items(node.items())
        properties = parse_properties(node)
        if (not self.allow_duplicate_names and
                self._contains_invalid_property_name(properties.items())):
            self._log_property_error_message()
            raise ValueError(
                "Reserved names and duplicate names are not allowed. Please rename your property inside the .tmx-file")

        self.properties = properties

    def __getattr__(self, item):
        try:
            return self.properties[item]
        except KeyError:
            if self.properties.get("name", None):
                raise AttributeError("Element '{0}' has no property {1}".format(self.name, item))
            else:
                raise AttributeError("Element has no property {0}".format(item))

    def __repr__(self):
        if hasattr(self, "id"):
            return '<{}[{}]: "{}">'.format(self.__class__.__name__, self.id, self.name)
        else:
            return '<{}: "{}">'.format(self.__class__.__name__, self.name)


class TiledMap(TiledElement):
    """Contains the layers, objects, and images from a Tiled TMX map

    This class is meant to handle most of the work you need to do to use a map.
    """

    def __init__(self, filename=None, image_loader=default_image_loader, **kwargs):
        """ Create new TiledMap

        :param filename: filename of tiled map to load
        :param image_loader: function that will load images (see below)
        :param optional_gids: load specific tile image GID, even if never used
        :param invert_y: invert the y axis
        :param load_all_tiles: load all tile images, even if never used
        :param allow_duplicate_names: allow duplicates in objects' metatdata

        image_loader:
          this must be a reference to a function that will accept a tuple:
          (filename of image, bounding rect of tile in image, flags)
          the function must return a reference to to the tile.
        """
        TiledElement.__init__(self)
        self.filename = filename
        self.image_loader = image_loader

        # optional keyword arguments checked here
        self.optional_gids = kwargs.get('optional_gids', set())
        self.load_all_tiles = kwargs.get('load_all', True)
        self.invert_y = kwargs.get('invert_y', True)

        # allow duplicate names to be parsed and loaded
        TiledElement.allow_duplicate_names = \
            kwargs.get('allow_duplicate_names', False)

        self.layers = list()  # all layers in proper order
        self.tilesets = list()  # TiledTileset objects
        self.tile_properties = dict()  # tiles that have properties
        self.layernames = dict()
        self.objects_by_id = dict()
        self.objects_by_name = dict()

        # only used tiles are actually loaded, so there will be a difference
        # between the GIDs in the Tiled map data (tmx) and the data in this
        # object and the layers.  This dictionary keeps track of that.
        self.gidmap = defaultdict(list)
        self.imagemap = dict()  # mapping of gid and trans flags to real gids
        self.tiledgidmap = dict()  # mapping of tiledgid to pytmx gid
        self.maxgid = 1

        # should be filled in by a loader function
        self.images = list()

        # defaults from the TMX specification
        self.version = '0.0'
        self.tiledversion = ''
        self.orientation = 'orthogonal'
        self.renderorder = 'right-down'
        self.width = 0  # width of map in tiles
        self.height = 0  # height of map in tiles
        self.tilewidth = 0  # width of a tile in pixels
        self.tileheight = 0  # height of a tile in pixels
        self.hexsidelength = 0
        self.staggeraxis = None
        self.staggerindex = None
        self.background_color = None
        self.nextobjectid = 0

        # initialize the gid mapping
        self.imagemap[(0, 0)] = 0

        if filename:
            self.parse_xml(ElementTree.parse(self.filename).getroot())

    def __repr__(self):
        return '<{0}: "{1}">'.format(self.__class__.__name__, self.filename)

    # iterate over layers and objects in map
    def __iter__(self):
        return chain(self.layers, self.objects)

    def _set_properties(self, node):
        TiledElement._set_properties(self, node)

        # TODO: make class/layer-specific type casting
        # layer height and width must be int, but TiledElement.set_properties()
        # make a float by default, so recast as int here
        self.height = int(self.height)
        self.width = int(self.width)

    def parse_xml(self, node):
        """ Parse a map from ElementTree xml node

        :param node: ElementTree xml node
        :return: self
        """
        self._set_properties(node)
        self.background_color = node.get('backgroundcolor',
                                         self.background_color)

        # ***         do not change this load order!         *** #
        # ***    gid mapping errors will occur if changed    *** #
        for subnode in node.findall('layer'):
            self.add_layer(TiledTileLayer(self, subnode))

        for subnode in node.findall('imagelayer'):
            self.add_layer(TiledImageLayer(self, subnode))

        # this will only find objectgroup layers, not including tile colliders
        for subnode in node.findall('objectgroup'):
            objectgroup = TiledObjectGroup(self, subnode)
            self.add_layer(objectgroup)
            for obj in objectgroup:
                self.objects_by_id[obj.id] = obj
                self.objects_by_name[obj.name] = obj

        for subnode in node.findall('tileset'):
            self.add_tileset(TiledTileset(self, subnode))

        # "tile objects", objects with a GID, require their attributes to be
        # set after the tileset is loaded, so this step must be performed last
        # also, this step is performed for objects to load their tiles.

        # tiled stores the origin of GID objects by the lower right corner
        # this is different for all other types, so i just adjust it here
        # so all types loaded with pytmx are uniform.

        # iterate through tile objects and handle the image
        for o in [o for o in self.objects if o.gid]:

            # gids might also have properties assigned to them
            # in that case, assign the gid properties to the object as well
            p = self.get_tile_properties_by_gid(o.gid)
            if p:
                for key in p:
                    o.properties.setdefault(key, p[key])

            if self.invert_y:
                o.y -= o.height

        self.reload_images()
        return self

    def reload_images(self):
        """ Load the map images from disk

        This method will use the image loader passed in the constructor
        to do the loading or will use a generic default, in which case no
        images will be loaded.

        :return: None
        """
        self.images = [None] * self.maxgid

        # iterate through tilesets to get source images
        for ts in self.tilesets:

            # skip tilesets without a source
            if ts.source is None:
                continue

            path = os.path.join(os.path.dirname(self.filename), ts.source)
            colorkey = getattr(ts, 'trans', None)
            loader = self.image_loader(path, colorkey, tileset=ts)

            p = product(range(ts.margin,
                              ts.height + ts.margin - ts.tileheight + 1,
                              ts.tileheight + ts.spacing),
                        range(ts.margin,
                              ts.width + ts.margin - ts.tilewidth + 1,
                              ts.tilewidth + ts.spacing))

            # iterate through the tiles
            for real_gid, (y, x) in enumerate(p, ts.firstgid):
                rect = (x, y, ts.tilewidth, ts.tileheight)
                gids = self.map_gid(real_gid)

                # gids is None if the tile is never used
                # but give another chance to load the gid anyway
                if gids is None:
                    if self.load_all_tiles or real_gid in self.optional_gids:
                        # TODO: handle flags? - might never be an issue, though
                        gids = [self.register_gid(real_gid, flags=0)]

                if gids:
                    # flags might rotate/flip the image, so let the loader
                    # handle that here
                    for gid, flags in gids:
                        self.images[gid] = loader(rect, flags)

        # load image layer images
        for layer in (i for i in self.layers if isinstance(i, TiledImageLayer)):
            source = getattr(layer, 'source', None)
            if source:
                colorkey = getattr(layer, 'trans', None)
                real_gid = len(self.images)
                gid = self.register_gid(real_gid)
                layer.gid = gid
                path = os.path.join(os.path.dirname(self.filename), source)
                loader = self.image_loader(path, colorkey)
                image = loader()
                self.images.append(image)

        # load images in tiles.
        # instead of making a new gid, replace the reference to the tile that
        # was loaded from the tileset
        for real_gid, props in self.tile_properties.items():
            source = props.get('source', None)
            if source:
                colorkey = props.get('trans', None)
                path = os.path.join(os.path.dirname(self.filename), source)
                loader = self.image_loader(path, colorkey)
                image = loader()
                self.images[real_gid] = image

    def get_tile_image(self, x, y, layer):
        """ Return the tile image for this location

        :param x: x coordinate
        :param y: y coordinate
        :param layer: layer number
        :rtype: surface if found, otherwise 0
        """
        if not (x >= 0 and y >= 0):
            raise ValueError("Tile coordinates must be non-negative, were ({0}, {1})".format(x, y))

        try:
            layer = self.layers[layer]
        except IndexError:
            raise ValueError("Layer not found")

        assert (isinstance(layer, TiledTileLayer))

        try:
            gid = layer.data[y][x]
        except (IndexError, ValueError):
            raise ValueError("GID not found")
        except TypeError:
            msg = "Tiles must be specified in integers."
            logger.debug(msg)
            raise TypeError(msg)

        else:
            return self.get_tile_image_by_gid(gid)

    def get_tile_image_by_gid(self, gid):
        """ Return the tile image for this location

        :param gid: GID of image
        :rtype: surface if found, otherwise ValueError
        """
        try:
            assert (int(gid) >= 0)
            return self.images[gid]
        except TypeError:
            msg = "GIDs must be expressed as a number.  Got: {0}"
            logger.debug(msg.format(gid))
            raise TypeError(msg.format(gid))
        except (AssertionError, IndexError):
            msg = "Coords: ({0},{1}) in layer {2} has invalid GID: {3}"
            logger.debug(msg.format(gid))
            raise ValueError(msg.format(gid))

    def get_tile_gid(self, x, y, layer):
        """ Return the tile image GID for this location

        :param x: x coordinate
        :param y: y coordinate
        :param layer: layer number
        :rtype: surface if found, otherwise ValueError
        """
        if not (x >= 0 and y >= 0 and layer >= 0):
            raise ValueError(
                "Tile coordinates and layers must be non-negative, were ({0}, {1}), layer={2}".format(x, y, layer))

        try:
            return self.layers[int(layer)].data[int(y)][int(x)]
        except (IndexError, ValueError):
            msg = "Coords: ({0},{1}) in layer {2} is invalid"
            logger.debug(msg.format(x, y, layer))
            raise ValueError(msg.format(x, y, layer))

    def get_tile_properties(self, x, y, layer):
        """ Return the tile image GID for this location

        :param x: x coordinate
        :param y: y coordinate
        :param layer: layer number
        :rtype: python dict if found, otherwise None
        """
        if not (x >= 0 and y >= 0 and layer >= 0):
            raise ValueError(
                "Tile coordinates and layers must be non-negative, were ({0}, {1}), layer={2}".format(x, y, layer))

        try:
            gid = self.layers[int(layer)].data[int(y)][int(x)]
        except (IndexError, ValueError):
            msg = "Coords: ({0},{1}) in layer {2} is invalid."
            logger.debug(msg.format(x, y, layer))
            raise Exception(msg.format(x, y, layer))

        else:
            try:
                return self.tile_properties[gid]
            except (IndexError, ValueError):
                msg = "Coords: ({0},{1}) in layer {2} has invalid GID: {3}"
                logger.debug(msg.format(x, y, layer, gid))
                raise Exception(msg.format(x, y, layer, gid))
            except KeyError:
                return None

    def get_tile_locations_by_gid(self, gid):
        """ Search map for tile locations by the GID

        Return (int, int, int) tuples, where the layer is index of
        the visible tile layers.

        Note: Not a fast operation.  Cache results if used often.

        :param gid: GID to be searched for
        :rtype: generator of tile locations
        """
        for l in self.visible_tile_layers:
            for x, y, _gid in [i for i in self.layers[l].iter_data() if i[2] == gid]:
                yield x, y, l

    def get_tile_properties_by_gid(self, gid):
        """ Get the tile properties of a tile GID

        :param gid: GID
        :rtype: python dict if found, otherwise None
        """
        try:
            return self.tile_properties[gid]
        except KeyError:
            return None

    def set_tile_properties(self, gid, properties):
        """ Set the tile properties of a tile GID

        :param gid: GID
        :param properties: python dict of properties for GID
        """
        self.tile_properties[gid] = properties

    def get_tile_properties_by_layer(self, layer):
        """ Get the tile properties of each GID in layer

        :param layer: layer number
        :rtype: iterator of (gid, properties) tuples
        """
        try:
            assert (int(layer) >= 0)
            layer = int(layer)
        except (TypeError, AssertionError):
            msg = "Layer must be a positive integer.  Got {0} instead."
            logger.debug(msg.format(type(layer)))
            raise ValueError

        p = product(range(self.width), range(self.height))
        layergids = set(self.layers[layer].data[y][x] for x, y in p)

        for gid in layergids:
            try:
                yield gid, self.tile_properties[gid]
            except KeyError:
                continue

    def add_layer(self, layer):
        """ Add a layer (TileTileLayer, TiledImageLayer, or TiledObjectGroup)

        :param layer: TileTileLayer, TiledImageLayer, TiledObjectGroup object
        """
        assert (
            isinstance(layer,
                       (TiledTileLayer, TiledImageLayer, TiledObjectGroup)))

        self.layers.append(layer)
        self.layernames[layer.name] = layer

    def add_tileset(self, tileset):
        """ Add a tileset to the map

        :param tileset: TiledTileset
        """
        assert (isinstance(tileset, TiledTileset))
        self.tilesets.append(tileset)

    def get_layer_by_name(self, name):
        """Return a layer by name

        :param name: Name of layer.  Case-sensitive.
        :rtype: Layer object if found, otherwise ValueError
        """
        try:
            return self.layernames[name]
        except KeyError:
            msg = 'Layer "{0}" not found.'
            logger.debug(msg.format(name))
            raise ValueError(msg.format(name))

    def get_object_by_id(self, obj_id):
        """Find an object

        :param name: Name of object.  Case-sensitive.
        :rtype: Object if found, otherwise ValueError
        """
        return self.objects_by_id[obj_id]

    def get_object_by_name(self, name):
        """Find an object

        :param name: Name of object.  Case-sensitive.
        :rtype: Object if found, otherwise ValueError
        """
        return self.objects_by_name[name]

    def get_tileset_from_gid(self, gid):
        """ Return tileset that owns the gid

        Note: this is a slow operation, so if you are expecting to do this
              often, it would be worthwhile to cache the results of this.

        :param gid: gid of tile image
        :rtype: TiledTileset if found, otherwise ValueError
        """
        try:
            tiled_gid = self.tiledgidmap[gid]
        except KeyError:
            raise ValueError("Tile GID not found")

        for tileset in sorted(self.tilesets, key=attrgetter('firstgid'),
                              reverse=True):
            if tiled_gid >= tileset.firstgid:
                return tileset

        raise ValueError("Tileset not found")

    def get_tile_colliders(self):
        """Return iterator of (gid, dict) pairs of tiles with colliders"""
        for gid, props in self.tile_properties.items():
            colliders = props.get("colliders")
            if colliders:
                yield gid, colliders

    @property
    def objectgroups(self):
        """Return iterator of all object groups

        :rtype: Iterator
        """
        return (layer for layer in self.layers
                if isinstance(layer, TiledObjectGroup))

    @property
    def objects(self):
        """Return iterator of all the objects associated with this map

        :rtype: Iterator
        """
        return chain(*self.objectgroups)

    @property
    def visible_layers(self):
        """Return iterator of Layer objects that are set 'visible'

        :rtype: Iterator
        """
        return (l for l in self.layers if l.visible)

    @property
    def visible_tile_layers(self):
        """Return iterator of layer indexes that are set 'visible'

        :rtype: Iterator
        """
        return (i for (i, l) in enumerate(self.layers)
                if l.visible and isinstance(l, TiledTileLayer))

    @property
    def visible_object_groups(self):
        """Return iterator of object group indexes that are set 'visible'

        :rtype: Iterator
        """
        return (i for (i, l) in enumerate(self.layers)
                if l.visible and isinstance(l, TiledObjectGroup))

    def register_gid(self, tiled_gid, flags=None):
        """ Used to manage the mapping of GIDs between the tmx and pytmx

        :param tiled_gid: GID that is found in TMX data
        :rtype: GID that pytmx uses for the the GID passed
        """
        if flags is None:
            flags = TileFlags(0, 0, 0)

        if tiled_gid:
            try:
                return self.imagemap[(tiled_gid, flags)][0]
            except KeyError:
                gid = self.maxgid
                self.maxgid += 1
                self.imagemap[(tiled_gid, flags)] = (gid, flags)
                self.gidmap[tiled_gid].append((gid, flags))
                self.tiledgidmap[gid] = tiled_gid
                return gid

        else:
            return 0

    def map_gid(self, tiled_gid):
        """ Used to lookup a GID read from a TMX file's data

        :param tiled_gid: GID that is found in TMX data
        :rtype: (GID, flags) for the the GID passed, None if not found
        """
        try:
            return self.gidmap[int(tiled_gid)]
        except KeyError:
            return None
        except TypeError:
            msg = "GIDs must be an integer"
            logger.debug(msg)
            raise TypeError(msg)

    def map_gid2(self, tiled_gid):
        """ WIP.  need to refactor the gid code

        :param tiled_gid:
        :return:
        """
        tiled_gid = int(tiled_gid)

        # gidmap is a default dict, so cannot trust to raise KeyError
        if tiled_gid in self.gidmap:
            return self.gidmap[tiled_gid]
        else:
            gid = self.register_gid(tiled_gid)
            return [(gid, None)]


class TiledTileset(TiledElement):
    """ Represents a Tiled Tileset

    External tilesets are supported.  GID/ID's from Tiled are not guaranteed to
    be the same after loaded.
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent
        self.offset = (0, 0)

        # defaults from the specification
        self.firstgid = 0
        self.source = None
        self.name = None
        self.tilewidth = 0
        self.tileheight = 0
        self.spacing = 0
        self.margin = 0
        self.tilecount = 0
        self.columns = 0

        # image properties
        self.trans = None
        self.width = 0
        self.height = 0

        self.parse_xml(node)

    def parse_xml(self, node):
        """ Parse a Tileset from ElementTree xml element

        A bit of mangling is done here so that tilesets that have external
        TSX files appear the same as those that don't

        :param node: ElementTree element
        :return: self
        """
        import os

        # if true, then node references an external tileset
        source = node.get('source', None)
        if source:
            if source[-4:].lower() == ".tsx":

                # external tilesets don't save this, store it for later
                self.firstgid = int(node.get('firstgid'))

                # we need to mangle the path - tiled stores relative paths
                dirname = os.path.dirname(self.parent.filename)
                path = os.path.abspath(os.path.join(dirname, source))
                if not os.path.exists(path):
                    # raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
                    raise Exception(
                        "Cannot find tileset file {0} from {1}, should be at {2}".format(source, self.parent.filename,
                                                                                         path))

                try:
                    node = ElementTree.parse(path).getroot()
                except IOError as io:
                    msg = "Error loading external tileset: {0}"
                    logger.error(msg.format(path))
                    raise Exception(msg.format(path)) from io
            else:
                msg = "Found external tileset, but cannot handle type: {0}"
                logger.error(msg.format(self.source))
                raise Exception(msg.format(self.source))

        self._set_properties(node)

        # since tile objects [probably] don't have a lot of metadata,
        # we store it separately in the parent (a TiledMap instance)
        register_gid = self.parent.register_gid
        for child in node.iter('tile'):
            tiled_gid = int(child.get("id"))

            p = {k: types[k](v) for k, v in child.items()}
            p.update(parse_properties(child))

            # images are listed as relative to the .tsx file, not the .tmx file:
            if source and "path" in p:
                p["path"] = os.path.join(os.path.dirname(source), p["path"])

            # handle tiles that have their own image
            image = child.find('image')
            if image is None:
                p['width'] = self.tilewidth
                p['height'] = self.tileheight
            else:
                tile_source = image.get('source')
                # images are listed as relative to the .tsx file, not the .tmx file:
                if source and tile_source:
                    tile_source = os.path.join(os.path.dirname(source), tile_source)
                p['source'] = tile_source
                p['trans'] = image.get('trans', None)
                p['width'] = image.get('width')
                p['height'] = image.get('height')

            # handle tiles with animations
            anim = child.find('animation')
            frames = list()
            p['frames'] = frames
            if anim is not None:
                for frame in anim.findall("frame"):
                    duration = int(frame.get('duration'))
                    gid = register_gid(int(frame.get('tileid')) + self.firstgid)
                    frames.append(AnimationFrame(gid, duration))

            for objgrp_node in child.findall("objectgroup"):
                objectgroup = TiledObjectGroup(self.parent, objgrp_node)
                p["colliders"] = objectgroup

            for gid, flags in self.parent.map_gid2(tiled_gid + self.firstgid):
                self.parent.set_tile_properties(gid, p)

        # handle the optional 'tileoffset' node
        self.offset = node.find('tileoffset')
        if self.offset is None:
            self.offset = (0, 0)
        else:
            self.offset = (self.offset.get('x', 0), self.offset.get('y', 0))

        image_node = node.find('image')
        if image_node is not None:
            self.source = image_node.get('source')

            # When loading from tsx, tileset image path is relative to the tsx file, not the tmx:
            if source:
                self.source = os.path.join(os.path.dirname(source), self.source)

            self.trans = image_node.get('trans', None)
            self.width = int(image_node.get('width'))
            self.height = int(image_node.get('height'))

        return self


class TiledTileLayer(TiledElement):
    """ Represents a TileLayer

    To just get the tile images, use TiledTileLayer.tiles()
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent
        self.data = list()

        # defaults from the specification
        self.name = None
        self.width = 0
        self.height = 0
        self.opacity = 1.0
        self.visible = True
        self.offsetx = 0
        self.offsety = 0

        self.parse_xml(node)

    def __iter__(self):
        return self.iter_data()

    def iter_data(self):
        """ Iterate over layer data

        Yields X, Y, GID tuples for each tile in the layer

        :return: Generator
        """
        for y, row in enumerate(self.data):
            for x, gid in enumerate(row):
                yield x, y, gid

    def tiles(self):
        """ Iterate over tile images of this layer

        This is an optimised generator function that returns
        (tile_x, tile_y, tile_image) tuples,

        :rtype: Generator
        :return: (x, y, image) tuples
        """
        images = self.parent.images
        for x, y, gid in [i for i in self.iter_data() if i[2]]:
            yield x, y, images[gid]

    def _set_properties(self, node):
        TiledElement._set_properties(self, node)

        # TODO: make class/layer-specific type casting
        # layer height and width must be int, but TiledElement.set_properties()
        # make a float by default, so recast as int here
        self.height = int(self.height)
        self.width = int(self.width)

    def parse_xml(self, node):
        """ Parse a Tile Layer from ElementTree xml node

        :param node: ElementTree xml node
        :return: self
        """
        import struct
        import array

        self._set_properties(node)
        data = None
        next_gid = None
        data_node = node.find('data')
        chunk_nodes = data_node.findall('chunk')
        if chunk_nodes:
            msg = 'TMX map size: infinite is not supported.'
            logger.error(msg)
            raise Exception

        encoding = data_node.get('encoding', None)
        if encoding == 'base64':
            from base64 import b64decode

            data = b64decode(data_node.text.strip())

        elif encoding == 'csv':
            next_gid = map(int, "".join(
                line.strip() for line in data_node.text.strip()).split(","))

        elif encoding:
            msg = 'TMX encoding type: {0} is not supported.'
            logger.error(msg.format(encoding))
            raise Exception(msg.format(encoding))

        compression = data_node.get('compression', None)
        if compression == 'gzip':
            import gzip

            with gzip.GzipFile(fileobj=BytesIO(data)) as fh:
                data = fh.read()

        elif compression == 'zlib':
            import zlib

            data = zlib.decompress(data)

        elif compression:
            msg = 'TMX compression type: {0} is not supported.'
            logger.error(msg.format(compression))
            raise Exception(msg.format(compression))

        # if data is None, then it was not decoded or decompressed, so
        # we assume here that it is going to be a bunch of tile elements
        # TODO: this will/should raise an exception if there are no tiles
        if encoding == next_gid is None:
            def get_children(parent):
                for child in parent.findall('tile'):
                    yield int(child.get('gid'))

            next_gid = get_children(data_node)

        elif data:
            if type(data) == bytes:
                fmt = struct.Struct('<L')
                iterator = (data[i:i + 4] for i in range(0, len(data), 4))
                next_gid = (fmt.unpack(i)[0] for i in iterator)
            else:
                msg = 'layer data not in expected format ({})'
                logger.error(msg.format(type(data)))
                raise Exception(msg.format(type(data)))

        init = lambda: [0] * self.width
        reg = self.parent.register_gid

        # H (16-bit) may be a limitation for very detailed maps
        self.data = tuple(array.array('H', init()) for i in range(self.height))
        for (y, x) in product(range(self.height), range(self.width)):
            self.data[y][x] = reg(*decode_gid(next(next_gid)))

        return self


class TiledObjectGroup(TiledElement, list):
    """ Represents a Tiled ObjectGroup

    Supports any operation of a normal list.
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent

        # defaults from the specification
        self.name = None
        self.color = None
        self.opacity = 1
        self.visible = 1
        self.offsetx = 0
        self.offsety = 0
        self.draworder = "index"

        self.parse_xml(node)

    def parse_xml(self, node):
        """ Parse an Object Group from ElementTree xml node

        :param node: ElementTree xml node
        :return: self
        """
        self._set_properties(node)
        self.extend(TiledObject(self.parent, child)
                    for child in node.findall('object'))

        return self


class TiledObject(TiledElement):
    """ Represents a any Tiled Object

    Supported types: Box, Ellipse, Tile Object, Polyline, Polygon
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent

        # defaults from the specification
        self.id = 0
        self.name = None
        self.type = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.rotation = 0
        self.gid = 0
        self.visible = 1
        self.closed = True
        self.template = None

        self.parse_xml(node)

    @property
    def image(self):
        if self.gid:
            return self.parent.images[self.gid]
        return None

    def parse_xml(self, node):
        """ Parse an Object from ElementTree xml node

        :param node: ElementTree xml node
        :return: self
        """

        def read_points(text):
            """parse a text string of float tuples and return [(x,...),...]
            """
            return tuple(tuple(map(float, i.split(','))) for i in text.split())

        self._set_properties(node)

        # correctly handle "tile objects" (object with gid set)
        if self.gid:
            self.gid = self.parent.register_gid(self.gid)

        points = None
        polygon = node.find('polygon')
        if polygon is not None:
            points = read_points(polygon.get('points'))
            self.closed = True

        polyline = node.find('polyline')
        if polyline is not None:
            points = read_points(polyline.get('points'))
            self.closed = False

        if points:
            x1 = x2 = y1 = y2 = 0
            for x, y in points:
                if x < x1: x1 = x
                if x > x2: x2 = x
                if y < y1: y1 = y
                if y > y2: y2 = y
            self.width = abs(x1) + abs(x2)
            self.height = abs(y1) + abs(y2)
            self.points = tuple(
                [Point(i[0] + self.x, i[1] + self.y) for i in points])

        return self

    def apply_transformations(self):
        """Return all points for object, taking in account rotation"""
        if hasattr(self, "points"):
            return rotate(self.points, self, self.rotation)
        else:
            return rotate(self.as_points, self, self.rotation)

    @property
    def as_points(self):
        return [
            Point(*i)
            for i in [
                (self.x, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height),
                (self.x + self.width, self.y),
            ]
        ]


class TiledImageLayer(TiledElement):
    """ Represents Tiled Image Layer

    The image associated with this layer will be loaded and assigned a GID.
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)
        self.parent = parent
        self.source = None
        self.trans = None
        self.gid = 0

        # defaults from the specification
        self.name = None
        self.opacity = 1
        self.visible = 1

        self.parse_xml(node)

    @property
    def image(self):
        if self.gid:
            return self.parent.images[self.gid]
        return None

    def parse_xml(self, node):
        """ Parse an Image Layer from ElementTree xml node

        :param node: ElementTree xml node
        :return: self
        """
        self._set_properties(node)
        self.name = node.get('name', None)
        self.opacity = node.get('opacity', self.opacity)
        self.visible = node.get('visible', self.visible)
        image_node = node.find('image')
        self.source = image_node.get('source', None)
        self.trans = image_node.get('trans', None)
        return self


class TiledProperty(TiledElement):
    """ Represents Tiled Property
    """

    def __init__(self, parent, node):
        TiledElement.__init__(self)

        # defaults from the specification
        self.name = None
        self.type = None
        self.value = None

        self.parse_xml(node)

    def parse_xml(self, node):
        pass
#endregion