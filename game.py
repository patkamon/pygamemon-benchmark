import pygame
from config import GameConfig, TileType


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, tilemap: "TileMap"):
        super().__init__()
        self.tilemap = tilemap

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = GameConfig.PLAYER_SPEED
        self.velocity = pygame.math.Vector2(0, 0)

        self.spritesheet = pygame.image.load(GameConfig.PLAYER_SPRITE).convert_alpha()
        self.frame_width = self.spritesheet.get_width() // 3
        self.frame_height = self.spritesheet.get_height() // 3

        self.animation_row = 0
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15

        self.direction = pygame.math.Vector2(0, 1)

        self.update_sprite()

    def update_sprite(self):
        frame_x = self.animation_frame * self.frame_width
        frame_y = self.animation_row * self.frame_height
        frame = self.spritesheet.subsurface(
            pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        )
        self.image = pygame.transform.scale(frame, (32, 32))

    def get_direction_from_input(self) -> pygame.math.Vector2:
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x = 1

        if direction.length() > 0:
            direction = direction.normalize()

        return direction

    def update(self, dt: float):
        self.velocity = self.get_direction_from_input()

        if self.velocity.length() > 0:
            self.direction = self.velocity

            if self.direction.y < 0:
                self.animation_row = 2
            elif self.direction.x < 0:
                self.animation_row = 1
            else:
                self.animation_row = 0

            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3

            new_x = self.rect.x + self.velocity.x * self.speed * dt
            new_y = self.rect.y + self.velocity.y * self.speed * dt

            if self.tilemap.is_walkable(new_x, self.rect.y):
                self.rect.x = new_x
            if self.tilemap.is_walkable(self.rect.x, new_y):
                self.rect.y = new_y

        self.update_sprite()


class TileMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tile_size = GameConfig.TILE_SIZE

        self.grass = pygame.image.load(GameConfig.GRASS_SPRITE).convert_alpha()
        self.grass = pygame.transform.scale(
            self.grass, (self.tile_size, self.tile_size)
        )

        self.bush = pygame.image.load(GameConfig.BUSH_SPRITE).convert_alpha()
        self.bush = pygame.transform.scale(self.bush, (self.tile_size, self.tile_size))

        self.tree = pygame.image.load(GameConfig.TREE_SPRITE).convert_alpha()
        self.tree = pygame.transform.scale(self.tree, (self.tile_size, self.tile_size))

        self.map_data = [[TileType.GRASS for _ in range(width)] for _ in range(height)]

        self._setup_default_map()

    def _setup_default_map(self):
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    self.map_data[y][x] = TileType.TREE
                elif (x + y) % 7 == 0:
                    self.map_data[y][x] = TileType.TREE
                elif (x + y) % 5 == 0:
                    self.map_data[y][x] = TileType.BUSH

    def is_walkable(self, x: float, y: float) -> bool:
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return False

        tile_type = self.map_data[tile_y][tile_x]
        return tile_type != TileType.TREE

    def render_grass(
        self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0
    ):
        start_x = max(0, camera_x // self.tile_size)
        end_x = min(self.width, (camera_x + surface.get_width()) // self.tile_size + 1)
        start_y = max(0, camera_y // self.tile_size)
        end_y = min(
            self.height, (camera_y + surface.get_height()) // self.tile_size + 1
        )

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.map_data[y][x] == TileType.GRASS:
                    surface.blit(
                        self.grass,
                        (x * self.tile_size - camera_x, y * self.tile_size - camera_y),
                    )

    def render_tiles(
        self, surface: pygame.Surface, camera_x: int = 0, camera_y: int = 0
    ):
        start_x = max(0, camera_x // self.tile_size)
        end_x = min(self.width, (camera_x + surface.get_width()) // self.tile_size + 1)
        start_y = max(0, camera_y // self.tile_size)
        end_y = min(
            self.height, (camera_y + surface.get_height()) // self.tile_size + 1
        )

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.map_data[y][x]
                pos_x = x * self.tile_size - camera_x
                pos_y = y * self.tile_size - camera_y

                if tile_type == TileType.BUSH:
                    surface.blit(self.bush, (pos_x, pos_y))
                elif tile_type == TileType.TREE:
                    surface.blit(self.tree, (pos_x, pos_y - self.tile_size // 2))

    def get_player_start(self) -> tuple:
        center_x = self.width // 2
        center_y = self.height // 2
        return center_x * self.tile_size, center_y * self.tile_size
