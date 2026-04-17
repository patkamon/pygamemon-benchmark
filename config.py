"""Centralized configuration for the Pokémon-style movement game."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowConfig:
    """Window / display settings."""
    width: int = 800
    height: int = 600
    title: str = "Pokemon-Style Movement"
    fps: int = 60


@dataclass(frozen=True)
class TileConfig:
    """Tile map settings."""
    size: int = 48          # rendered tile size (pixels)
    raw_size: int = 16      # source asset tile size
    scale: int = 3          # size / raw_size
    map_cols: int = 25      # tiles wide
    map_rows: int = 20      # tiles tall


@dataclass(frozen=True)
class PlayerConfig:
    """Player movement & animation settings."""
    speed: float = 200.0          # pixels per second
    sheet_cols: int = 3           # spritesheet columns
    sheet_rows: int = 3           # spritesheet rows
    frame_width: int = 16        # single frame width in sheet
    frame_height: int = 21       # single frame height in sheet
    anim_speed: float = 0.15     # seconds per animation frame
    scale: int = 3               # render scale factor


# Tile type constants
TILE_GRASS = 0
TILE_BUSH = 1
TILE_TREE = 2
