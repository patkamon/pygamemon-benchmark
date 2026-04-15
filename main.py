import pygame
import sys
from config import GameConfig
from game import Player, TileMap


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (GameConfig.WINDOW_WIDTH, GameConfig.WINDOW_HEIGHT)
    )
    pygame.display.set_caption("Pokémon-style Game")
    clock = pygame.time.Clock()

    tilemap = TileMap(GameConfig.MAP_WIDTH, GameConfig.MAP_HEIGHT)
    player_start = tilemap.get_player_start()
    player = Player(player_start[0], player_start[1], tilemap)

    camera_x = 0
    camera_y = 0

    running = True
    while running:
        dt = clock.tick(GameConfig.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        player.update(dt)

        camera_x = player.rect.centerx - GameConfig.WINDOW_WIDTH // 2
        camera_y = player.rect.centery - GameConfig.WINDOW_HEIGHT // 2

        camera_x = max(
            0,
            min(
                camera_x,
                GameConfig.MAP_WIDTH * GameConfig.TILE_SIZE - GameConfig.WINDOW_WIDTH,
            ),
        )
        camera_y = max(
            0,
            min(
                camera_y,
                GameConfig.MAP_HEIGHT * GameConfig.TILE_SIZE - GameConfig.WINDOW_HEIGHT,
            ),
        )

        screen.fill((0, 0, 0))

        tilemap.render_grass(screen, camera_x, camera_y)

        screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

        tilemap.render_tiles(screen, camera_x, camera_y)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
