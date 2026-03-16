import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255), (4, 4), 4)
        pygame.draw.circle(self.image, (255, 255, 255), (4, 4), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.direction = direction
        self.speed = 10

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        # If bullet is off-screen, it should be removed (handled by group)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
