"""Main entry point – game loop, camera, and layer orchestration."""

import pygame
from config import WindowConfig, TileConfig, PlayerConfig
from player import Player
from tilemap import TileMap


def main():
    pygame.init()

    win_cfg = WindowConfig()
    tile_cfg = TileConfig()
    player_cfg = PlayerConfig()

    screen = pygame.display.set_mode((win_cfg.width, win_cfg.height))
    pygame.display.set_caption(win_cfg.title)
    clock = pygame.time.Clock()

    # Create world and player
    tile_map = TileMap(tile_cfg)
    player = Player(player_cfg, tile_cfg)

    running = True
    while running:
        dt = clock.tick(win_cfg.fps) / 1000.0  # seconds

        # ── Events ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # ── Update ────────────────────────────────────────────────────
        player.update(dt, tile_map.solid_tiles)

        # Camera: centre on player, clamped to map bounds
        world_w = tile_cfg.map_cols * tile_cfg.size
        world_h = tile_cfg.map_rows * tile_cfg.size

        camera_x = int(player.x + player.rect.width / 2 - win_cfg.width / 2)
        camera_y = int(player.y + player.rect.height / 2 - win_cfg.height / 2)
        camera_x = max(0, min(camera_x, world_w - win_cfg.width))
        camera_y = max(0, min(camera_y, world_h - win_cfg.height))

        # ── Render (layered) ──────────────────────────────────────────
        screen.fill((0, 0, 0))

        # Layer 1: grass + trees (ground)
        tile_map.draw_ground(screen, camera_x, camera_y)

        # Layer 2: player
        player.draw(screen, camera_x, camera_y)

        # Layer 3: bushes (overlay, on top of player)
        tile_map.draw_overlay(screen, camera_x, camera_y)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
