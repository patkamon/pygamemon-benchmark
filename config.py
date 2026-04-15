from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class DisplayConfig:
    width: int = 960
    height: int = 640
    title: str = "Pokemon-Style Movement"
    background_color: tuple[int, int, int] = (0, 0, 0)
    fps: int = 60


@dataclass(frozen=True)
class WorldConfig:
    tile_size: int = 48
    map_width: int = 20
    map_height: int = 14
    camera_lerp: float = 10.0
    layout: tuple[str, ...] = (
        "....................",
        "...b.......t........",
        "..bbb...........t...",
        "......tt............",
        "..........bbb.......",
        "...t.............b..",
        "....................",
        "....bbb.....tt......",
        "..............b.....",
        "..t.................",
        ".........bbb........",
        ".....t.........t....",
        "........b...........",
        "....................",
    )


@dataclass(frozen=True)
class PlayerConfig:
    speed: float = 185.0
    animation_fps: float = 8.0
    hitbox_width_ratio: float = 0.55
    hitbox_height_ratio: float = 0.35


@dataclass(frozen=True)
class AssetConfig:
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    player_sheet: Path = field(init=False)
    grass_tile: Path = field(init=False)
    bush_tile: Path = field(init=False)
    tree_tile: Path = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "player_sheet", self.root / "sprite/character/player.png")
        object.__setattr__(self, "grass_tile", self.root / "sprite/environment/grass.png")
        object.__setattr__(self, "bush_tile", self.root / "sprite/environment/bush.png")
        object.__setattr__(self, "tree_tile", self.root / "sprite/environment/tree.png")


@dataclass(frozen=True)
class GameConfig:
    display: DisplayConfig = field(default_factory=DisplayConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    player: PlayerConfig = field(default_factory=PlayerConfig)
    assets: AssetConfig = field(default_factory=AssetConfig)
