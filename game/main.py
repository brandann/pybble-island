import pygame, data.pybble, sys
from pygame.locals import *
from data import pybble
#from data import pytmx
#from game import Game

TESTING = False

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

pygame.init()
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
pygame.display.set_caption('PyTMX Map Viewer')

map = pybble.SimpleTest('data/maps/untitled.tmx')

map_world_rect = pygame.Rect(0, 0, map.renderer.width(), map.renderer.height())
map_colliders = map.get_boundry()

true_scroll = [0,0]
x = 0
y = 0

is_moving = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}

player_world_rect = pygame.Rect(300 - 12, 300 - 12, 25, 25)

camera_world_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())

#game = Game()

time_scale = 1

player_speed = 3/16

delta_time = pybble.clock.tick(pybble.FPS) * time_scale

while True:

    # game.update_events()
    # game.update_iu()
    # game.update_player()
    # game.update_game()
    # game.update_render()

    pygame_events()
    player_movement = [0, 0]
    if is_moving['RIGHT']:
        player_movement[0] += player_speed * delta_time
    if is_moving['LEFT']:
        player_movement[0] -= player_speed * delta_time
    if is_moving['UP']:
        player_movement[1] -= player_speed * delta_time
    if is_moving['DOWN']:
        player_movement[1] += player_speed * delta_time

    player_world_rect.x += player_movement[0]
    player_world_rect.y += player_movement[1]
    player_world_rect, hit_colliders = pybble.move(player_world_rect, player_movement, map_colliders)

    # keep camera the size of screen
    camera_world_rect.width = screen.get_width()
    camera_world_rect.height = screen.get_height()

    # set camera center to player
    camera_world_rect.left = player_world_rect.left + (player_world_rect.width / 2) - (screen.get_width() / 2)
    camera_world_rect.top = player_world_rect.top + (player_world_rect.height / 2) - (screen.get_height() / 2)

    # square camera to map
    pybble.bind_rect_inside(map_world_rect, camera_world_rect)
    pybble.bind_rect_inside(camera_world_rect, player_world_rect)

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
    pygame.display.flip()

    delta_time = pybble.clock.tick(pybble.FPS) * time_scale

