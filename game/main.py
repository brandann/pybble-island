import pygame, sys
from pygame.locals import *
from data import pybble

class Game():
    from data import pybble
    def __init__(self, screen):

        self.TESTING = True
        self.screen = screen

        self.game_object_list = []

        slime = pybble.GameObject(100,100,32,32,'slime')
        slime.load_animations('data/images/slime/', None)
        self.game_object_list.append(slime)

        idle_guy = pybble.GameObject(200,100,12,32,'player')
        idle_guy.load_animations('data/images/player/')
        self.game_object_list.append(idle_guy)
        # self.game_object_list.remove(idle_guy)

        self.player = pybble.GameObject(300,300,12,32,'player')
        self.player.load_animations('data/images/player/')

        self.map = pybble.SimpleTest('data/maps/untitled.tmx')
        self.map_world_rect = pygame.Rect(0, 0, self.map.renderer.width(), self.map.renderer.height())
        self.map_colliders = self.map.get_boundry()
        self.true_scroll = [0, 0]
        self.is_moving = {"LEFT": False, "RIGHT": False, "UP": False, "DOWN": False}
        self.camera_world_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        self.time_scale = 1
        self.player_speed = 3 / 16
        self.delta_time = self.get_delta_time()
        self.frame_tick = 0

    def get_delta_time(self):
        return pybble.clock.tick(pybble.FPS) * self.time_scale

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
            self.player.flip = False
            self.player.set_animation('run')
        if self.is_moving['LEFT']:
            player_movement[0] -= self.player_speed * self.delta_time
            self.player.flip = True
            self.player.set_animation('run')
        if self.is_moving['UP']:
            player_movement[1] -= self.player_speed * self.delta_time
            self.player.set_animation('run')
        if self.is_moving['DOWN']:
            player_movement[1] += self.player_speed * self.delta_time
            self.player.set_animation('run')
        if player_movement[0] == 0 and player_movement[1] == 0:
            self.player.set_animation('idle')

        col = self.player.move(player_movement, self.map_colliders)

    def update_game(self):
        # keep camera the size of screen
        self.camera_world_rect.width = screen.get_width()
        self.camera_world_rect.height = screen.get_height()

        # set camera center to player
        self.camera_world_rect.left = self.player.get_rect().left + (self.player.get_rect().width / 2) - (screen.get_width() / 2)
        self.camera_world_rect.top = self.player.get_rect().top + (self.player.get_rect().height / 2) - (screen.get_height() / 2)

        # square camera to map
        pybble.bind_rect_inside(self.map_world_rect, self.camera_world_rect)
        pybble.bind_rect_inside(self.camera_world_rect, self.player.get_rect())

        for g in self.game_object_list:
            self.move_torawrd_player(g, self.player)

    def update_render(self):
        self.true_scroll[0] += self.camera_world_rect.x - self.true_scroll[0]
        self.true_scroll[1] += self.camera_world_rect.y - self.true_scroll[1]

        # this makes the tiles drawn at int positions so they don't get fractions of a pixel off when displayed
        scroll = self.true_scroll.copy()
        scroll[0] = int(scroll[0])  # int(scroll[0])
        scroll[1] = int(scroll[1])  # int(scroll[1])

        camera_screen_rect = self.camera_world_rect.copy()
        camera_screen_rect.x -= self.true_scroll[0]
        camera_screen_rect.y -= self.true_scroll[1]

        player_screen_rect = self.player.get_rect().copy()
        player_screen_rect.x -= self.true_scroll[0]
        player_screen_rect.y -= self.true_scroll[1]

        # draw map objects
        self.map.draw_background_layer(self.screen, scroll[0], scroll[1])
        self.map.draw_boundry_layer(self.screen, scroll[0], scroll[1])

        # draw player
        self.player.draw(self.screen, self.true_scroll)

        # draw foreground objects above player
        self.map.draw_foreground_layer(self.screen, scroll[0], scroll[1])

        for g in self.game_object_list:
            g.draw(self.screen, self.true_scroll)

        if self.TESTING:
            for tile in self.map_colliders:
                pygame.draw.rect(screen, pybble.Blue, (tile.x-scroll[0], tile.y-scroll[1],tile.width, tile.height), 1)
            pygame.draw.rect(self.screen, pybble.Red, (player_screen_rect), 1)
            for g in self.game_object_list:
                gc = g.get_rect()
                pygame.draw.rect(screen, pybble.Yellow, (gc.x - scroll[0], gc.y - scroll[1], gc.width, gc.height),1)
                gwc = g.world_to_screen(scroll).center
                # pwc = self.player.world_to_screen(scroll).center
                # pygame.draw.line(self.screen, pybble.Yellow, (gwc[0], gwc[1]), (pwc[0], pwc[1]))
                p = self.player.get_rect()
                dist = pybble.Vector_VBetween( ((gc.x, gc.y)) , (p.x, p.y) )
                g_normal = pybble.Vector_Normalize(dist)
                g_normal = pybble.Vector_Multiply(g_normal, 100)
                g_end = pybble.Vector_Add( gwc, (g_normal[0], g_normal[1]))
                pygame.draw.line(self.screen, pybble.Yellow, gwc, (g_end[0], g_end[1]))

        # draw screen
        pygame.display.flip()

    def finalize(self):
        self.delta_time = self.get_delta_time()
        self.frame_tick += 1 * self.time_scale
        self.player.change_frame(1 * self.time_scale)
        pass # anything to reset before next frame

    def move_torawrd_player(self, go, player):
        go_rect = go.get_rect()
        pl_rect = player.get_rect()
        dist = pybble.Vector_Distance((go_rect.x, go_rect.y), (pl_rect.x, pl_rect.y))


pygame.init()
screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
pygame.display.set_caption('Pybble Island - Nybble Studios @rirukiru')

pybble.load_animations('data/images/animations/')

game = Game(screen)

while True:

    game.update_events()
    game.update_ui()
    game.update_player()
    game.update_game()
    game.update_render()
    game.finalize()

