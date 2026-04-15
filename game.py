from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame

from config import GameConfig


Vec2 = pygame.math.Vector2


def load_image(path: Path) -> pygame.Surface:
    image = pygame.image.load(path)
    return image.convert_alpha()


def scale_image(image: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    return pygame.transform.scale(image, size)


@dataclass
class Camera:
    viewport_size: tuple[int, int]
    world_pixel_size: tuple[int, int]
    position: Vec2 = None

    def __post_init__(self) -> None:
        if self.position is None:
            self.position = Vec2()

    def update(self, target: pygame.Rect, delta_time: float, follow_strength: float) -> None:
        desired_x = target.centerx - self.viewport_size[0] / 2
        desired_y = target.centery - self.viewport_size[1] / 2

        max_x = max(0, self.world_pixel_size[0] - self.viewport_size[0])
        max_y = max(0, self.world_pixel_size[1] - self.viewport_size[1])
        desired = Vec2(max(0, min(desired_x, max_x)), max(0, min(desired_y, max_y)))

        self.position += (desired - self.position) * min(1.0, follow_strength * delta_time)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(-round(self.position.x), -round(self.position.y))


class TileMap:
    def __init__(self, config: GameConfig) -> None:
        self.config = config
        self.tile_size = config.world.tile_size
        self.layout = config.world.layout
        self.width = len(self.layout[0])
        self.height = len(self.layout)
        self.pixel_width = self.width * self.tile_size
        self.pixel_height = self.height * self.tile_size

        self.grass = scale_image(load_image(config.assets.grass_tile), (self.tile_size, self.tile_size))
        self.bush = scale_image(load_image(config.assets.bush_tile), (self.tile_size, self.tile_size))
        self.tree = scale_image(load_image(config.assets.tree_tile), (self.tile_size, self.tile_size * 2))

        self.bush_tiles: list[tuple[int, int]] = []
        self.tree_tiles: list[tuple[int, int]] = []
        self.tree_colliders: list[pygame.Rect] = []
        self._parse_layout()

    def _parse_layout(self) -> None:
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                if cell == "b":
                    self.bush_tiles.append((x, y))
                elif cell == "t":
                    self.tree_tiles.append((x, y))
                    self.tree_colliders.append(
                        pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                    )

    def get_spawn_position(self) -> Vec2:
        return Vec2(self.pixel_width / 2, self.pixel_height / 2)

    def render_ground(self, surface: pygame.Surface, camera: Camera) -> None:
        for y in range(self.height):
            for x in range(self.width):
                world_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                surface.blit(self.grass, camera.apply(world_rect))

    def render_bushes(self, surface: pygame.Surface, camera: Camera) -> None:
        for x, y in self.bush_tiles:
            world_rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
            surface.blit(self.bush, camera.apply(world_rect))

    def render_trees(self, surface: pygame.Surface, camera: Camera) -> None:
        for x, y in self.tree_tiles:
            world_rect = pygame.Rect(x * self.tile_size, y * self.tile_size - self.tile_size, self.tile_size, self.tile_size * 2)
            surface.blit(self.tree, camera.apply(world_rect))


class Player:
    def __init__(self, config: GameConfig, start_position: Vec2) -> None:
        self.config = config
        self.position = Vec2(start_position)
        self.direction = Vec2()
        self.facing = "down"
        self.animation_time = 0.0
        self.frame_index = 1
        self.frames = self._load_frames()
        initial_frame = self.frames["down"][self.frame_index]
        self.image = initial_frame
        self.rect = self.image.get_rect(center=(round(self.position.x), round(self.position.y)))
        self.hitbox = self._create_hitbox()

    def _load_frames(self) -> dict[str, list[pygame.Surface]]:
        sheet = load_image(self.config.assets.player_sheet)
        frame_width = sheet.get_width() // 3
        frame_height = sheet.get_height() // 3
        scaled_size = (
            frame_width * (self.config.world.tile_size // frame_width if self.config.world.tile_size >= frame_width else 1),
            frame_height * (self.config.world.tile_size // frame_width if self.config.world.tile_size >= frame_width else 1),
        )
        if scaled_size[0] != self.config.world.tile_size:
            scale_factor = self.config.world.tile_size / frame_width
            scaled_size = (round(frame_width * scale_factor), round(frame_height * scale_factor))

        rows = []
        for row in range(3):
            row_frames = []
            for col in range(3):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                row_frames.append(scale_image(frame, scaled_size))
            rows.append(row_frames)

        right_frames = rows[1]
        left_frames = [pygame.transform.flip(frame, True, False) for frame in right_frames]
        return {
            "up": rows[0],
            "right": right_frames,
            "down": rows[2],
            "left": left_frames,
        }

    def _create_hitbox(self) -> pygame.Rect:
        width = round(self.rect.width * self.config.player.hitbox_width_ratio)
        height = round(self.rect.height * self.config.player.hitbox_height_ratio)
        hitbox = pygame.Rect(0, 0, width, height)
        hitbox.midbottom = self.rect.midbottom
        return hitbox

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        move_x = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        move_y = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        self.direction = Vec2(move_x, move_y)

        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            if abs(self.direction.x) >= abs(self.direction.y):
                self.facing = "right" if self.direction.x > 0 else "left"
            else:
                self.facing = "down" if self.direction.y > 0 else "up"

    def update(self, delta_time: float, colliders: list[pygame.Rect], world_bounds: pygame.Rect) -> None:
        self.handle_input()
        velocity = self.direction * self.config.player.speed * delta_time

        self.hitbox.x += round(velocity.x)
        self._resolve_collisions(colliders, axis="x")

        self.hitbox.y += round(velocity.y)
        self._resolve_collisions(colliders, axis="y")

        self.hitbox.clamp_ip(world_bounds)
        self.rect.midbottom = self.hitbox.midbottom
        self.position.update(self.rect.center)
        self._update_animation(delta_time)

    def _resolve_collisions(self, colliders: list[pygame.Rect], axis: str) -> None:
        for collider in colliders:
            if not self.hitbox.colliderect(collider):
                continue
            if axis == "x":
                if self.direction.x > 0:
                    self.hitbox.right = collider.left
                elif self.direction.x < 0:
                    self.hitbox.left = collider.right
            else:
                if self.direction.y > 0:
                    self.hitbox.bottom = collider.top
                elif self.direction.y < 0:
                    self.hitbox.top = collider.bottom

    def _update_animation(self, delta_time: float) -> None:
        moving = self.direction.length_squared() > 0
        if moving:
            self.animation_time += delta_time * self.config.player.animation_fps
            self.frame_index = int(self.animation_time) % len(self.frames[self.facing])
        else:
            self.animation_time = 0.0
            self.frame_index = 1

        self.image = self.frames[self.facing][self.frame_index]
        current_midbottom = self.rect.midbottom
        self.rect = self.image.get_rect()
        self.rect.midbottom = current_midbottom

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        surface.blit(self.image, camera.apply(self.rect))


def main() -> None:
    pygame.init()
    config = GameConfig()
    screen = pygame.display.set_mode((config.display.width, config.display.height))
    pygame.display.set_caption(config.display.title)
    clock = pygame.time.Clock()

    tile_map = TileMap(config)
    player = Player(config, tile_map.get_spawn_position())
    world_bounds = pygame.Rect(0, 0, tile_map.pixel_width, tile_map.pixel_height)
    camera = Camera(
        viewport_size=(config.display.width, config.display.height),
        world_pixel_size=(tile_map.pixel_width, tile_map.pixel_height),
    )

    running = True
    while running:
        delta_time = clock.tick(config.display.fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update(delta_time, tile_map.tree_colliders, world_bounds)
        camera.update(player.rect, delta_time, config.world.camera_lerp)

        screen.fill(config.display.background_color)
        tile_map.render_ground(screen, camera)
        player.draw(screen, camera)
        tile_map.render_bushes(screen, camera)
        tile_map.render_trees(screen, camera)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
