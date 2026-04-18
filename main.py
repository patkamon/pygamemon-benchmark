import pygame
import sys
from config import GameConfig
from player import Player
from map import TileMap


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Pokémon-Style Movement Game")
        self.clock = pygame.time.Clock()
        self.running = True

        self.grass_surf = self._load_image("sprite/environment/grass.png")
        self.bush_surf = self._load_image("sprite/environment/bush.png")
        self.tree_surf = self._load_image("sprite/environment/tree.png")
        self.player_spritesheet = self._load_image("sprite/character/player.png")

        self.grass_surf = pygame.transform.scale(
            self.grass_surf, (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
        )
        bush_orig_height = self.bush_surf.get_height()
        bush_orig_width = self.bush_surf.get_width()
        aspect = bush_orig_width / bush_orig_height
        new_height = GameConfig.TILE_SIZE * 2
        new_width = int(new_height * aspect)
        self.bush_surf = pygame.transform.scale(self.bush_surf, (new_width, new_height))

        tree_orig_height = self.tree_surf.get_height()
        tree_orig_width = self.tree_surf.get_width()
        tree_aspect = tree_orig_width / tree_orig_height
        tree_new_height = GameConfig.TILE_SIZE * 2
        tree_new_width = int(tree_new_height * tree_aspect)
        self.tree_surf = pygame.transform.scale(self.tree_surf, (tree_new_width, tree_new_height))

        self.tilemap = TileMap(
            GameConfig.MAP_WIDTH,
            GameConfig.MAP_HEIGHT,
            GameConfig.TILE_SIZE,
            self.grass_surf,
            self.bush_surf,
            self.tree_surf,
        )

        start_x, start_y = self.tilemap.get_player_start_position()
        self.player = Player(start_x, start_y, self.player_spritesheet)

        self.camera_x = 0.0
        self.camera_y = 0.0

    def _load_image(self, path: str) -> pygame.Surface:
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Failed to load image {path}: {e}")
            sys.exit(1)

    def _update_camera(self):
        target_x = self.player.x - GameConfig.WINDOW_WIDTH / 2 + GameConfig.TILE_SIZE / 2
        target_y = self.player.y - GameConfig.WINDOW_HEIGHT / 2 + GameConfig.TILE_SIZE / 2

        map_width_px = self.tilemap.width * GameConfig.TILE_SIZE
        map_height_px = self.tilemap.height * GameConfig.TILE_SIZE

        self.camera_x = max(0, min(target_x, map_width_px - GameConfig.WINDOW_WIDTH))
        self.camera_y = max(0, min(target_y, map_height_px - GameConfig.WINDOW_HEIGHT))

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def _update(self, dt: float):
        keys = pygame.key.get_pressed()
        collision_tiles = self.tilemap.get_collision_tiles()
        self.player.update(dt, keys, collision_tiles)
        self._update_camera()

    def _render(self):
        self.screen.fill((0, 0, 0))

        self.tilemap.draw_grass(self.screen, self.camera_x, self.camera_y)

        self.tilemap.draw_bushes(self.screen, self.camera_x, self.camera_y)

        self.player.draw(self.screen, self.camera_x, self.camera_y)

        self.tilemap.draw_trees(self.screen, self.camera_x, self.camera_y)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(GameConfig.FPS) / 1000.0

            self._handle_events()
            self._update(dt)
            self._render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
