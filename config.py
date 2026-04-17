import pygame
from dataclasses import dataclass

SCALE = 3
TILE_SIZE = 16 * SCALE

@dataclass
class Config:
    WIDTH: int = 800
    HEIGHT: int = 600
    FPS: int = 60
    TITLE: str = "Pokémon-Style Movement"
    PLAYER_SPEED: float = 200.0
