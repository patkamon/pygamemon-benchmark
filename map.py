import pygame
from config import GameConfig, TILE_TYPES


class TileMap:
    def __init__(
        self,
        width: int,
        height: int,
        tile_size: int,
        grass_surf: pygame.Surface,
        bush_surf: pygame.Surface,
        tree_surf: pygame.Surface,
    ):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grass_surf = grass_surf
        self.bush_surf = bush_surf
        self.tree_surf = tree_surf

        self.map_data = [[TILE_TYPES.GRASS for _ in range(width)] for _ in range(height)]
        self.collision_tiles: list[pygame.Rect] = []
        self.bush_rects: list[pygame.Rect] = []
        self._setup_map()
        self._generate_collision_tiles()

    def _setup_map(self):
        for x in range(self.width):
            for y in range(self.height):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.map_data[y][x] = TILE_TYPES.TREE

        for x in range(5, 10):
            for y in range(3, 6):
                self.map_data[y][x] = TILE_TYPES.BUSH

        for x in range(12, 15):
            for y in range(7, 10):
                self.map_data[y][x] = TILE_TYPES.BUSH

        self.map_data[5][8] = TILE_TYPES.TREE
        self.map_data[9][5] = TILE_TYPES.TREE
        self.map_data[3][15] = TILE_TYPES.TREE
        self.map_data[7][12] = TILE_TYPES.TREE
        self.map_data[10][10] = TILE_TYPES.TREE
        self.map_data[12][6] = TILE_TYPES.TREE
        self.map_data[4][13] = TILE_TYPES.TREE

    def _generate_collision_tiles(self):
        self.collision_tiles = []
        self.bush_rects = []

        for y in range(self.height):
            for x in range(self.width):
                tile = self.map_data[y][x]
                rect = pygame.Rect(
                    x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size
                )

                if tile == TILE_TYPES.TREE:
                    self.collision_tiles.append(rect)
                elif tile == TILE_TYPES.BUSH:
                    self.bush_rects.append(rect)

    def get_collision_tiles(self) -> list[pygame.Rect]:
        return self.collision_tiles

    def get_bush_rects(self) -> list[pygame.Rect]:
        return self.bush_rects

    def get_player_start_position(self) -> tuple[float, float]:
        return (
            self.width // 2 * self.tile_size,
            self.height // 2 * self.tile_size,
        )

    def draw_grass(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        for y in range(self.height):
            for x in range(self.width):
                draw_x = x * self.tile_size - camera_x
                draw_y = y * self.tile_size - camera_y
                surface.blit(self.grass_surf, (draw_x, draw_y))

    def draw_bushes(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        bush_height = self.bush_surf.get_height()
        bush_width = self.bush_surf.get_width()
        y_offset = self.tile_size - bush_height

        for y in range(self.height):
            for x in range(self.width):
                if self.map_data[y][x] == TILE_TYPES.BUSH:
                    draw_x = x * self.tile_size - camera_x
                    draw_y = y * self.tile_size + y_offset - camera_y
                    surface.blit(self.bush_surf, (draw_x, draw_y))

    def draw_trees(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        tree_height = self.tree_surf.get_height()
        tree_width = self.tree_surf.get_width()
        y_offset = self.tile_size - tree_height

        for y in range(self.height):
            for x in range(self.width):
                if self.map_data[y][x] == TILE_TYPES.TREE:
                    draw_x = x * self.tile_size - camera_x
                    draw_y = y * self.tile_size + y_offset - camera_y
                    surface.blit(self.tree_surf, (draw_x, draw_y))

    def draw(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        self.draw_grass(surface, camera_x, camera_y)
        self.draw_trees(surface, camera_x, camera_y)
