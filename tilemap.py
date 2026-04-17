"""Tile map – world data, rendering layers, and collision info."""

import os
import random
import pygame
from config import TileConfig, TILE_GRASS, TILE_BUSH, TILE_TREE


class TileMap:
    """Manages a 2D grid of tiles with separate render layers.

    Rendering order (from prompt):
        1. Grass  (background)
        2. —— player drawn by caller between layers ——
        3. Bush   (overlay, walkable, rendered ON TOP of player)
        4. Tree   (solid, rendered on background layer alongside grass)

    Trees block movement but visually sit in the background layer
    so they don't awkwardly cover the player from above.  Bushes
    are the overlay that renders on top of the player.
    """

    def __init__(self, cfg: TileConfig):
        self.cfg = cfg
        self.cols = cfg.map_cols
        self.rows = cfg.map_rows
        self.tile_size = cfg.size  # rendered size

        # Load tile assets
        self.grass_img = self._load_tile("grass.png", cfg.size, cfg.size)
        self.bush_img = self._load_tile("bush.png", cfg.size, cfg.size)
        # Tree is 16×32 → scale to tile_size × tile_size*2
        self.tree_img = self._load_tile("tree.png", cfg.size, cfg.size * 2)

        # Build the map layout
        self.grid: list[list[int]] = self._generate_map()

        # Pre‑compute set of solid tile positions for fast collision checks
        self.solid_tiles: set[tuple[int, int]] = set()
        self._build_solid_set()

    # ------------------------------------------------------------------
    # Asset loading
    # ------------------------------------------------------------------
    @staticmethod
    def _load_tile(filename: str, w: int, h: int) -> pygame.Surface:
        path = os.path.join("sprite", "environment", filename)
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))

    # ------------------------------------------------------------------
    # Map generation
    # ------------------------------------------------------------------
    def _generate_map(self) -> list[list[int]]:
        """Create a hand‑designed + procedural map similar to the reference."""
        grid = [[TILE_GRASS for _ in range(self.cols)] for _ in range(self.rows)]

        random.seed(42)  # deterministic for reproducibility

        # Place trees (solid obstacles) — scattered around the map
        tree_positions = [
            # Top area
            (7, 1), (11, 0),
            (15, 1), (20, 1),
            # Left column
            (2, 3), (1, 6), (1, 10),
            # Middle‑right
            (14, 5), (15, 5),
            (17, 8), (18, 8),
            # Bottom area
            (4, 12), (5, 12),
            (12, 14),
            (18, 13), (19, 13),
            (8, 16), (15, 16),
            (3, 18), (10, 18), (20, 17),
        ]
        for col, row in tree_positions:
            if 0 <= col < self.cols and 0 <= row < self.rows:
                grid[row][col] = TILE_TREE

        # Place bushes (walkable decoration) — clusters
        bush_positions = [
            # Top‑left cluster
            (3, 1), (4, 1), (5, 1),
            # Mid‑left
            (5, 5), (6, 5), (7, 5),
            # Centre scattering
            (10, 3), (11, 3), (12, 3),
            (8, 7), (9, 7),
            # Bottom clusters
            (5, 10), (6, 10), (7, 10),
            (13, 11), (14, 11),
            (9, 14), (10, 14), (11, 14),
            (17, 15), (18, 15), (19, 15),
            # Additional scatter for visual interest
            (21, 5),
            (2, 14),
            (22, 10),
        ]
        for col, row in bush_positions:
            if 0 <= col < self.cols and 0 <= row < self.rows:
                grid[row][col] = TILE_BUSH

        return grid

    def _build_solid_set(self):
        """Populate the set of (col, row) that block player movement."""
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == TILE_TREE:
                    self.solid_tiles.add((col, row))
                    # Tree sprite is 2 tiles tall; also block the row above
                    # if it exists (the visual top half)
                    if row > 0:
                        self.solid_tiles.add((col, row - 1))

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw_ground(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the background layer: grass everywhere + trees."""
        ts = self.tile_size
        # Calculate visible tile range for culling
        start_col = max(0, camera_x // ts)
        end_col = min(self.cols, (camera_x + surface.get_width()) // ts + 2)
        start_row = max(0, camera_y // ts)
        end_row = min(self.rows, (camera_y + surface.get_height()) // ts + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                sx = col * ts - camera_x
                sy = row * ts - camera_y

                # Always draw grass as the base
                surface.blit(self.grass_img, (sx, sy))

                # Draw trees on the ground layer
                if self.grid[row][col] == TILE_TREE:
                    # Tree is 2 tiles tall; draw so its base aligns with this row
                    tree_y = sy - ts  # shift up by one tile
                    surface.blit(self.tree_img, (sx, tree_y))

    def draw_overlay(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw the overlay layer: bushes ON TOP of the player."""
        ts = self.tile_size
        start_col = max(0, camera_x // ts)
        end_col = min(self.cols, (camera_x + surface.get_width()) // ts + 2)
        start_row = max(0, camera_y // ts)
        end_row = min(self.rows, (camera_y + surface.get_height()) // ts + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if self.grid[row][col] == TILE_BUSH:
                    sx = col * ts - camera_x
                    sy = row * ts - camera_y
                    surface.blit(self.bush_img, (sx, sy))
