import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        # Plasma Bolt looks - elongated and glowing
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        # Gradient effect for the bolt
        pygame.draw.ellipse(self.image, (255, 255, 255), (10, 2, 10, 4)) # Core
        pygame.draw.ellipse(self.image, (0, 255, 255), (0, 0, 20, 8), 2) # Glow outer
        
        # Rotate image to match direction
        angle = direction.angle_to(pygame.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.direction = direction
        self.speed = 18 # High velocity
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

    def draw(self, screen):
        # Draw a trail
        trail_start = self.pos - self.direction * 15
        pygame.draw.line(screen, (0, 150, 255), self.pos, trail_start, 2)
        screen.blit(self.image, self.rect)
