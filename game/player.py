import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Create a glowing neon green square
        pygame.draw.rect(self.image, (0, 255, 150), (0, 0, 32, 32), 2, border_radius=4)
        pygame.draw.rect(self.image, (0, 100, 50), (4, 4, 24, 24), border_radius=2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 5
        self.health = 100
        self.max_health = 100

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move.x += 1
        
        if move.length() > 0:
            move = move.normalize() * self.speed
            self.pos += move
            self.rect.center = self.pos

    def update(self, screen_width, screen_height):
        self.handle_input()
        # Keep player on screen
        self.pos.x = max(16, min(screen_width - 16, self.pos.x))
        self.pos.y = max(16, min(screen_height - 16, self.pos.y))
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)
