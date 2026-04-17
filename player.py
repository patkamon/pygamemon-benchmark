"""Player entity – movement, animation, and collision."""

import os
import pygame
from config import PlayerConfig, TileConfig

# Direction indices into the 3‑row spritesheet.
# Row 0 = facing down, Row 1 = facing left, Row 2 = facing up
# Column 0 = stand, Columns 0‑2 = walk cycle
DIR_DOWN = 0
DIR_LEFT = 1
DIR_UP = 2
DIR_RIGHT = 3  # will mirror DIR_LEFT frames


class Player:
    """Handles the player sprite, input‑driven movement, animation, and
    tile‑based collision against solid tiles."""

    def __init__(self, cfg: PlayerConfig, tile_cfg: TileConfig):
        self.cfg = cfg
        self.tile_cfg = tile_cfg

        # Position (world‑space, floats for sub‑pixel accuracy)
        start_x = (tile_cfg.map_cols // 2) * tile_cfg.size
        start_y = (tile_cfg.map_rows // 2) * tile_cfg.size
        self.x: float = float(start_x)
        self.y: float = float(start_y)

        # Animation state
        self.direction = DIR_DOWN
        self.frame_index = 0
        self.anim_timer: float = 0.0
        self.moving = False

        # Load and slice the spritesheet
        self.frames = self._load_frames()

        # Collision rect (slightly smaller than visual for forgiving feel)
        w = cfg.frame_width * cfg.scale
        h = cfg.frame_height * cfg.scale
        self.rect = pygame.Rect(self.x, self.y, w, h)

    # ------------------------------------------------------------------
    # Asset loading
    # ------------------------------------------------------------------
    def _load_frames(self) -> dict[int, list[pygame.Surface]]:
        """Slice the 3×3 spritesheet into per‑direction frame lists."""
        path = os.path.join("sprite", "character", "player.png")
        sheet = pygame.image.load(path).convert_alpha()

        fw = self.cfg.frame_width
        fh = self.cfg.frame_height
        scale = self.cfg.scale

        frames: dict[int, list[pygame.Surface]] = {
            DIR_DOWN: [],
            DIR_LEFT: [],
            DIR_UP: [],
            DIR_RIGHT: [],
        }

        row_dir = [DIR_DOWN, DIR_LEFT, DIR_UP]
        for row, direction in enumerate(row_dir):
            for col in range(self.cfg.sheet_cols):
                sub = sheet.subsurface(pygame.Rect(col * fw, row * fh, fw, fh))
                scaled = pygame.transform.scale(sub, (fw * scale, fh * scale))
                frames[direction].append(scaled)

        # Right = horizontally flipped left frames
        frames[DIR_RIGHT] = [
            pygame.transform.flip(f, True, False) for f in frames[DIR_LEFT]
        ]

        return frames

    # ------------------------------------------------------------------
    # Per‑frame update
    # ------------------------------------------------------------------
    def update(self, dt: float, solid_tiles: set[tuple[int, int]]):
        """Read keyboard input, move with collision, and animate.

        Parameters
        ----------
        dt : float
            Delta‑time in seconds (frame‑independent movement).
        solid_tiles : set of (col, row)
            Set of tile coordinates that block movement.
        """
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.direction = DIR_LEFT
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.direction = DIR_RIGHT
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            self.direction = DIR_UP
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            self.direction = DIR_DOWN

        self.moving = dx != 0 or dy != 0

        if self.moving:
            # Normalise diagonal so speed is consistent
            length = (dx * dx + dy * dy) ** 0.5
            dx /= length
            dy /= length

            speed = self.cfg.speed * dt

            # Move X then check collision
            new_x = self.x + dx * speed
            test_rect = self.rect.copy()
            test_rect.x = int(new_x)
            if not self._collides(test_rect, solid_tiles):
                self.x = new_x

            # Move Y then check collision
            new_y = self.y + dy * speed
            test_rect = self.rect.copy()
            test_rect.x = int(self.x)
            test_rect.y = int(new_y)
            if not self._collides(test_rect, solid_tiles):
                self.y = new_y

            # Animate walk cycle
            self.anim_timer += dt
            if self.anim_timer >= self.cfg.anim_speed:
                self.anim_timer -= self.cfg.anim_speed
                self.frame_index = (self.frame_index + 1) % self.cfg.sheet_cols
        else:
            # Idle — show standing frame
            self.frame_index = 0
            self.anim_timer = 0.0

        self.rect.topleft = (int(self.x), int(self.y))

    # ------------------------------------------------------------------
    # Collision helpers
    # ------------------------------------------------------------------
    def _collides(self, rect: pygame.Rect, solid_tiles: set[tuple[int, int]]) -> bool:
        """Return True if *rect* overlaps any tile in *solid_tiles*."""
        ts = self.tile_cfg.size
        # Determine which tile columns/rows the rect touches
        left_col = rect.left // ts
        right_col = rect.right // ts
        top_row = rect.top // ts
        bottom_row = rect.bottom // ts

        for col in range(left_col, right_col + 1):
            for row in range(top_row, bottom_row + 1):
                if (col, row) in solid_tiles:
                    return True
        return False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the current animation frame offset by camera."""
        frame = self.frames[self.direction][self.frame_index]
        surface.blit(frame, (int(self.x) - camera_x, int(self.y) - camera_y))
