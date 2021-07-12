import pygame, data.pybble
from pygame.locals import *
from data import pybble
from game import Game
#from data import pytmx

TESTING = False

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
        self.renderer = pybble.TiledRenderer(filename)
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

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):

    # dictionary of hits
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    is_dirty = False

    # collide with x tiles
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[X] > 0:
            rect.right = tile.left
            collision_types['right'] = True
            is_dirty = True
        if movement[X] < 0:
            rect.left = tile.right
            collision_types['left'] = True
            is_dirty = True

    # collide with y tiles
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[Y] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
            is_dirty = True
        if movement[Y] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
            is_dirty = True

    return rect, collision_types, is_dirty

if __name__ == '__main__':
    import sys

    pygame.init()
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    pygame.display.set_caption('PyTMX Map Viewer')

    clock = pygame.time.Clock()
    FPS = 60

    map = SimpleTest('data/maps/untitled.tmx')

    map_world_rect = pygame.Rect(0, 0, map.renderer.width(), map.renderer.height())
    map_colliders = map.get_boundry()

    true_scroll = [0,0]
    x = 0
    y = 0

    is_moving = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}

    is_dirty = True

    player_world_rect = pygame.Rect(300 - 12, 300 - 12, 25, 25)

    camera_world_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())

    game = Game()

    time_scale = 1

    player_speed = 4/16

    delta_time = clock.tick(FPS) * time_scale

    while True:

        game.update_events()
        game.update_iu()
        game.update_player()
        game.update_game()
        game.update_render()

        pygame_events()
        player_movement = [0, 0]
        if is_moving['RIGHT']:
            player_movement[0] += player_speed * delta_time
            is_dirty = True
        if is_moving['LEFT']:
            player_movement[0] -= player_speed * delta_time
            is_dirty = True
        if is_moving['UP']:
            player_movement[1] -= player_speed * delta_time
            is_dirty = True
        if is_moving['DOWN']:
            player_movement[1] += player_speed * delta_time
            is_dirty = True

        player_world_rect.x += player_movement[0]
        player_world_rect.y += player_movement[1]
        #player_world_rect, map_colliders, is_dirty = move(player_world_rect, player_movement, map_colliders)

        # keep camera the size of screen
        camera_world_rect.width = screen.get_width()
        camera_world_rect.height = screen.get_height()

        # set camera center to player
        camera_world_rect.left = player_world_rect.left + (player_world_rect.width / 2) - (screen.get_width() / 2)
        camera_world_rect.top = player_world_rect.top + (player_world_rect.height / 2) - (screen.get_height() / 2)

        # square camera to map
        bind_rect_inside(map_world_rect, camera_world_rect)
        bind_rect_inside(camera_world_rect, player_world_rect)

        true_scroll[0] += camera_world_rect.x - true_scroll[0]
        true_scroll[1] += camera_world_rect.y - true_scroll[1]

        # this makes the tiles drawn at int positions so they don't get fractions of a pixel off when displayed
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0]) #int(scroll[0])
        scroll[1] = int(scroll[1]) #int(scroll[1])

        #player_position = pygame.Rect(player_rect.x - scroll[0], player_rect.y - scroll[1], player_rect.width, player_rect.height)
        camera_screen_rect = camera_world_rect.copy()
        camera_screen_rect.x -= true_scroll[0]
        camera_screen_rect.y -= true_scroll[1]

        player_screen_rect = player_world_rect.copy()
        player_screen_rect.x -= true_scroll[0]
        player_screen_rect.y -= true_scroll[1]



        if is_dirty:
            # draw map objects
            map.draw_background_layer(screen, scroll[0], scroll[1])
            map.draw_boundry_layer(screen, scroll[0], scroll[1])
            #map.draw(screen, scroll[0], scroll[1])

            # draw player
            pygame.draw.rect(screen, (255, 0, 0), (player_screen_rect))

            #pygame.draw.rect(screen, (0,0,255), camera_screen_rect, 5)

            #draw foreground objects above player
            map.draw_foreground_layer(screen, scroll[0], scroll[1])

            if TESTING:
                for tile in map_colliders:
                    pygame.draw.rect(screen, (0, 0, 255), tile, 5)

            # draw screen
            is_dirty = False
            pygame.display.flip()

        delta_time = clock.tick(FPS) * time_scale

