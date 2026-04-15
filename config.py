import pygame
from dataclasses import dataclass


@dataclass
class GameConfig:
    WINDOW_WIDTH: int = 800
    WINDOW_HEIGHT: int = 600
    TILE_SIZE: int = 32
    MAP_WIDTH: int = 20
    MAP_HEIGHT: int = 15
    PLAYER_SPEED: int = 200
    FPS: int = 60

    PLAYER_SPRITE: str = "sprite/character/player.png"
    GRASS_SPRITE: str = "sprite/environment/grass.png"
    BUSH_SPRITE: str = "sprite/environment/bush.png"
    TREE_SPRITE: str = "sprite/environment/tree.png"


@dataclass
class TileType:
    GRASS: int = 0
    BUSH: int = 1
    TREE: int = 2
