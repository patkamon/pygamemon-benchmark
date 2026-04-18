import pygame
from config import GameConfig, TILE_TYPES


class Player:
    FRAME_WIDTH = 16
    FRAME_HEIGHT = 16
    SCALE = 3
    SCALED_WIDTH = FRAME_WIDTH * SCALE
    SCALED_HEIGHT = FRAME_HEIGHT * SCALE

    ROW_DOWN = 0
    ROW_UP = 1
    ROW_RIGHT = 2

    def __init__(self, x: float, y: float, spritesheet: pygame.Surface):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
        self.speed = GameConfig.PLAYER_SPEED
        self.direction = "down"
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.spritesheet = spritesheet
        self.frames = self._load_frames()

    def _load_frames(self) -> dict:
        frames = {}
        frame_width = Player.FRAME_WIDTH
        frame_height = Player.FRAME_HEIGHT
        scale = Player.SCALE

        for row in range(3):
            for col in range(3):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                rect = pygame.Rect(
                    col * frame_width, row * frame_height, frame_width, frame_height
                )
                frame.blit(self.spritesheet, (0, 0), rect)
                scaled = pygame.transform.scale(
                    frame, (frame_width * scale, frame_height * scale)
                )
                direction_map = {0: "down", 1: "up", 2: "right"}
                direction = direction_map[row]
                if direction not in frames:
                    frames[direction] = []
                frames[direction].append(scaled)
        return frames

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, collision_tiles: list[pygame.Rect]):
        dx = 0.0
        dy = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1.0
            self.direction = "up"
            self.is_moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1.0
            self.direction = "down"
            self.is_moving = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1.0
            self.direction = "right"
            self.is_moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1.0
            self.direction = "right"
            self.is_moving = True
        else:
            self.is_moving = False

        if dx != 0 or dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                dx /= length
                dy /= length

            new_x = self.x + dx * self.speed * dt
            new_y = self.y + dy * self.speed * dt

            new_rect_x = pygame.Rect(new_x, self.y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
            new_rect_y = pygame.Rect(self.x, new_y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)

            can_move_x = True
            can_move_y = True

            for tile_rect in collision_tiles:
                if new_rect_x.colliderect(tile_rect):
                    can_move_x = False
                if new_rect_y.colliderect(tile_rect):
                    can_move_y = False

            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y

            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 3
        else:
            self.animation_frame = 0

        self.rect.x = self.x
        self.rect.y = self.y

    def get_current_frame(self) -> pygame.Surface:
        frames = self.frames[self.direction]
        return frames[self.animation_frame]

    def draw(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        frame = self.get_current_frame()
        surface.blit(frame, (self.x - camera_x, self.y - camera_y))
