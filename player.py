import pygame
from config import Config, SCALE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.z_index = 2 # Player on Layer 2
        
        # Load sprite sheet
        try:
            sheet = pygame.image.load('sprite/character/player.png').convert_alpha()
        except:
            sheet = pygame.Surface((48, 63), pygame.SRCALPHA)
            sheet.fill((255, 0, 0))

        original_width, original_height = sheet.get_size()
        frame_width = original_width // 3
        frame_height = original_height // 3
        
        self.frames = {
            'down': [],
            'up': [],
            'right': [],
            'left': []
        }
        
        for row, direction in enumerate(['down', 'right', 'up']):
            for col in range(3):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                image = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                image.blit(sheet, (0, 0), rect)
                image = pygame.transform.scale(image, (frame_width * SCALE, frame_height * SCALE))
                self.frames[direction].append(image)
                if direction == 'right':
                    flipped = pygame.transform.flip(image, True, False)
                    self.frames['left'].append(flipped)
                    
        self.direction = 'down'
        self.frame_index = 1
        self.image = self.frames[self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        
        # Collision hitbox - roughly lower half of the body
        self.hitbox = self.rect.inflate(int(-frame_width * SCALE * 0.4), int(-frame_height * SCALE * 0.6))
        # Keep it bottom-aligned
        self.hitbox.midbottom = self.rect.midbottom
        
        self.position = pygame.math.Vector2(self.hitbox.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = Config.PLAYER_SPEED
        self.animation_speed = 6.0
        self.is_moving = False

    def input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
            self.direction = 'up'
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1
            self.direction = 'down'
            
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
            self.direction = 'left'
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1
            self.direction = 'right'

        if self.velocity.magnitude() > 0:
            self.velocity = self.velocity.normalize()
            self.is_moving = True
        else:
            self.is_moving = False

    def animate(self, dt):
        if self.is_moving:
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.frames[self.direction]):
                self.frame_index = 0
        else:
            self.frame_index = 1 # Standing frame is usually the middle one
            
        self.image = self.frames[self.direction][int(self.frame_index)]

    def move(self, dt, solid_rects):
        # Frame-independent movement logic as per pygame-patterns skill
        self.position.x += self.velocity.x * self.speed * dt
        self.hitbox.centerx = round(self.position.x)
        self.check_collision_x(solid_rects)

        self.position.y += self.velocity.y * self.speed * dt
        self.hitbox.centery = round(self.position.y)
        self.check_collision_y(solid_rects)
        
        self.rect.midbottom = self.hitbox.midbottom

    def check_collision_x(self, solid_rects):
        for obstacle in solid_rects:
            if self.hitbox.colliderect(obstacle):
                if self.velocity.x > 0: # right
                    self.hitbox.right = obstacle.left
                elif self.velocity.x < 0: # left
                    self.hitbox.left = obstacle.right
                self.position.x = self.hitbox.centerx

    def check_collision_y(self, solid_rects):
        for obstacle in solid_rects:
            if self.hitbox.colliderect(obstacle):
                if self.velocity.y > 0: # down
                    self.hitbox.bottom = obstacle.top
                elif self.velocity.y < 0: # up
                    self.hitbox.top = obstacle.bottom
                self.position.y = self.hitbox.centery

    def update(self, dt, solid_rects):
        self.input()
        self.move(dt, solid_rects)
        self.animate(dt)
