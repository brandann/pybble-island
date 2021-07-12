import pygame, data.pybble
from pygame.locals import *
from data import pybble

#region GAME
class Game:

    def update_events(self):
        return

    def update_iu(self):
        return

    def update_player(self):
        return

    def update_game(self):
        return

    def update_render(self):
        return
#end region

######################################################
#
#  Simple Test - Basic app to display a rendered Tiled map
#
######################################################
class SimpleTest(object):

    def __init__(self, filename):
        self.renderer = None
        self.load_map(filename)

    def load_map(self, filename):
        self.renderer = pybble.TiledRenderer(filename)

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

def pygame_events():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                is_moving['RIGHT'] = True
            if event.key == K_LEFT:
                is_moving['LEFT'] = True
            if event.key == K_UP:
                is_moving['UP'] = True
            if event.key == K_DOWN:
                is_moving['DOWN'] = True
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                is_moving['RIGHT'] = False
            if event.key == K_LEFT:
                is_moving['LEFT'] = False
            if event.key == K_UP:
                is_moving['UP'] = False
            if event.key == K_DOWN:
                is_moving['DOWN'] = False

def bind_rect_inside(outer_rect, inner_rect):
    if inner_rect.left < outer_rect.left:
        inner_rect.left = outer_rect.left
    if inner_rect.right > outer_rect.right:
        inner_rect.right = outer_rect.right
    if inner_rect.top < outer_rect.top:
        inner_rect.top = outer_rect.top
    if inner_rect.bottom > outer_rect.bottom:
        inner_rect.bottom = outer_rect.bottom