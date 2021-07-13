import pygame, data.pybble, sys
from pygame.locals import *
from data import pybble
#from data import pytmx
#from game import Game

class Game():
    from data import pybble
    def __init__(self, screen):

        self.TESTING = False
        self.screen = screen

        self.map = pybble.SimpleTest('data/maps/untitled.tmx')
        self.map_world_rect = pygame.Rect(0, 0, self.map.renderer.width(), self.map.renderer.height())
        self.map_colliders = self.map.get_boundry()
        self.true_scroll = [0, 0]
        self.is_moving = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}
        self.player_world_rect = pygame.Rect(300 - 12, 300 - 12, 25, 25)
        self.camera_world_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.time_scale = 1
        self.player_speed = 3 / 16
        self.delta_time = pybble.clock.tick(pybble.FPS) * self.time_scale

    def update_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    self.is_moving['RIGHT'] = True
                if event.key == K_LEFT:
                    self.is_moving['LEFT'] = True
                if event.key == K_UP:
                    self.is_moving['UP'] = True
                if event.key == K_DOWN:
                    self.is_moving['DOWN'] = True
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.is_moving['RIGHT'] = False
                if event.key == K_LEFT:
                    self.is_moving['LEFT'] = False
                if event.key == K_UP:
                    self.is_moving['UP'] = False
                if event.key == K_DOWN:
                    self.is_moving['DOWN'] = False

    def update_ui(self):
        pass

    def update_player(self):
        player_movement = [0, 0]
        if self.is_moving['RIGHT']:
            player_movement[0] += self.player_speed * self.delta_time
        if self.is_moving['LEFT']:
            player_movement[0] -= self.player_speed * self.delta_time
        if self.is_moving['UP']:
            player_movement[1] -= self.player_speed * self.delta_time
        if self.is_moving['DOWN']:
            player_movement[1] += self.player_speed * self.delta_time

        # player_world_rect.x += player_movement[0] # <- this is not needed, the move function does it for us
        # player_world_rect.y += player_movement[1] # <- this is not needed, the move function does it for us
        self.player_world_rect, hit_colliders = pybble.move(self.player_world_rect, player_movement, self.map_colliders)

    def update_game(self):
        # keep camera the size of screen
        self.camera_world_rect.width = screen.get_width()
        self.camera_world_rect.height = screen.get_height()

        # set camera center to player
        self.camera_world_rect.left = self.player_world_rect.left + (self.player_world_rect.width / 2) - (screen.get_width() / 2)
        self.camera_world_rect.top = self.player_world_rect.top + (self.player_world_rect.height / 2) - (screen.get_height() / 2)

        # square camera to map
        pybble.bind_rect_inside(self.map_world_rect, self.camera_world_rect)
        pybble.bind_rect_inside(self.camera_world_rect, self.player_world_rect)

    def update_render(self):
        self.true_scroll[0] += self.camera_world_rect.x - self.true_scroll[0]
        self.true_scroll[1] += self.camera_world_rect.y - self.true_scroll[1]

        # this makes the tiles drawn at int positions so they don't get fractions of a pixel off when displayed
        scroll = self.true_scroll.copy()
        scroll[0] = int(scroll[0])  # int(scroll[0])
        scroll[1] = int(scroll[1])  # int(scroll[1])

        # player_position = pygame.Rect(player_rect.x - scroll[0], player_rect.y - scroll[1], player_rect.width, player_rect.height)
        camera_screen_rect = self.camera_world_rect.copy()
        camera_screen_rect.x -= self.true_scroll[0]
        camera_screen_rect.y -= self.true_scroll[1]

        player_screen_rect = self.player_world_rect.copy()
        player_screen_rect.x -= self.true_scroll[0]
        player_screen_rect.y -= self.true_scroll[1]

        # draw map objects
        self.map.draw_background_layer(self.screen, scroll[0], scroll[1])
        self.map.draw_boundry_layer(self.screen, scroll[0], scroll[1])

        # draw player
        pygame.draw.rect(self.screen, (255, 0, 0), (player_screen_rect))

        # draw foreground objects above player
        self.map.draw_foreground_layer(self.screen, scroll[0], scroll[1])

        if self.TESTING:
            for tile in self.map_colliders:
                pygame.draw.rect(screen, (0, 0, 255), tile, 5)

        # draw screen
        pygame.display.flip()

    def clean_frame(self):
        self.delta_time = pybble.clock.tick(pybble.FPS) * self.time_scale
        pass # anything to reset before next frame

pygame.init()
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
pygame.display.set_caption('PyTMX Map Viewer')

game = Game(screen)

while True:

    game.update_events()
    game.update_ui()
    game.update_player()
    game.update_game()
    game.update_render()
    game.clean_frame()

