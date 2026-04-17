import pygame
import sys
from config import Config
from player import Player
from tilemap import TileMap, CameraGroup

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        
        # Setup groups
        self.visible_sprites = CameraGroup(self.screen)
        
        # Setup map
        self.tilemap = TileMap()
        self.map_w, self.map_h, self.grass_surface = self.tilemap.build_map(self.visible_sprites)
        
        # Setup player - placed in center of map roughly
        start_x = self.map_w // 2
        start_y = self.map_h // 2
        self.player = Player((start_x, start_y), [self.visible_sprites])

    def run(self):
        while True:
            # Delta time in seconds
            dt = self.clock.tick(Config.FPS) / 1000.0
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            # Update
            self.visible_sprites.update(dt, self.tilemap.obstacle_sprites)
            
            # Render
            self.screen.fill('black')
            self.visible_sprites.custom_draw(self.player, self.grass_surface, self.map_w, self.map_h)
            
            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.run()
