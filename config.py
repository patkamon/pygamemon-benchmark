from dataclasses import dataclass
import pygame


@dataclass
class GameConfig:
    WINDOW_WIDTH: int = 960
    WINDOW_HEIGHT: int = 720
    FPS: int = 60
    TILE_SIZE: int = 48
    MAP_WIDTH: int = 20
    MAP_HEIGHT: int = 15
    PLAYER_SPEED: float = 200.0


@dataclass
class TileType:
    GRASS: int = 0
    BUSH: int = 1
    TREE: int = 2


TILE_TYPES = TileType()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
