import pygame
from config import TILE_SIZE, SCALE

MAP_DATA = [
    "TTTTTTTTTTTTTTTTTTTTTT",
    "T....B...........B...T",
    "T........T...........T",
    "T..B.................T",
    "T.......B......T.....T",
    "T.....T..............T",
    "T..............B.....T",
    "T.......T............T",
    "TTTTTTTTTTTTTTTTTTTTTT"
]

class CameraGroup(pygame.sprite.Group):
    def __init__(self, display_surface):
        super().__init__()
        self.display_surface = display_surface
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, target, grass_surface, map_width, map_height):
        # Calculate offset based on target (player)
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height
        
        # 1. Draw Grass
        self.display_surface.blit(grass_surface, -self.offset)
        
        # Draw Sprites Y-Sorted within their layers
        # Player and Tree are layer 2
        # Bush is layer 3
        # We sort by (z_index, rect.centery)
        for sprite in sorted(self.sprites(), key=lambda s: (s.z_index, s.rect.centery)):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, surface, z_index):
        super().__init__(groups)
        self.image = surface
        self.z_index = z_index
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, 0) # Default, overridden by Tree

class TileMap:
    def __init__(self):
        self.scale = SCALE
        
        try:
            grass_img = pygame.image.load('sprite/environment/grass.png').convert()
            bush_img = pygame.image.load('sprite/environment/bush.png').convert_alpha()
            tree_img = pygame.image.load('sprite/environment/tree.png').convert_alpha()
        except:
            grass_img = pygame.Surface((16, 16)); grass_img.fill((0, 255, 0))
            bush_img = pygame.Surface((16, 16), pygame.SRCALPHA); bush_img.fill((0, 100, 0, 150))
            tree_img = pygame.Surface((16, 32), pygame.SRCALPHA); tree_img.fill((139, 69, 19))
            
        self.grass_img = pygame.transform.scale(grass_img, (grass_img.get_width() * self.scale, grass_img.get_height() * self.scale))
        self.bush_img = pygame.transform.scale(bush_img, (bush_img.get_width() * self.scale, bush_img.get_height() * self.scale))
        self.tree_img = pygame.transform.scale(tree_img, (tree_img.get_width() * self.scale, tree_img.get_height() * self.scale))

        self.visible_sprites = None
        self.obstacle_sprites = []
        
        self.map_width = len(MAP_DATA[0]) * TILE_SIZE
        self.map_height = len(MAP_DATA) * TILE_SIZE
        
        # Create a giant surface for grass to draw efficiently
        self.grass_surface = pygame.Surface((self.map_width, self.map_height))
        
    def build_map(self, visible_sprites):
        self.visible_sprites = visible_sprites
        for row_idx, row in enumerate(MAP_DATA):
            for col_idx, col in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                
                # Grass everywhere
                self.grass_surface.blit(self.grass_img, (x, y))
                
                if col == 'B':
                    # Layer 3 (Bush) - renders on top of player
                    Tile((x, y), [self.visible_sprites], self.bush_img, z_index=3)
                elif col == 'T':
                    # Tree is solid, layer 2
                    # 16x32 original, 48x96 scaled. It spans 2 vertical tiles.
                    # Placing it so its bottom aligns with the grid.
                    tree_y = y - self.tree_img.get_height() + TILE_SIZE
                    tree = Tile((x, tree_y), [self.visible_sprites], self.tree_img, z_index=2)
                    
                    # Obstacle hitboxes for collision
                    # A tree's solid base is roughly the bottom tile of its sprite.
                    base_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.obstacle_sprites.append(base_rect)

        return self.map_width, self.map_height, self.grass_surface
