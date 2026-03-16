import pygame

class Terminal(pygame.sprite.Sprite):
    def __init__(self, x, y, terminal_type="scan", title="SYSTEM SCANNER"):
        super().__init__()
        self.terminal_type = terminal_type
        self.title = title
        self.image = pygame.Surface((64, 48), pygame.SRCALPHA)
        
        # Draw a cyberpunk terminal icon
        pygame.draw.rect(self.image, (0, 150, 255), (0, 0, 64, 48), 2, border_radius=5)
        pygame.draw.rect(self.image, (0, 50, 100), (4, 4, 56, 40), border_radius=3)
        # Screen glow
        pygame.draw.line(self.image, (0, 200, 255), (10, 10), (54, 10), 2)
        pygame.draw.line(self.image, (0, 200, 255), (10, 15), (40, 15), 1)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.active = False
        self.interaction_range = 80

    def is_near(self, player):
        dist = pygame.Vector2(self.rect.center).distance_to(player.pos)
        return dist < self.interaction_range

    def update(self, player):
        self.active = self.is_near(player)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.active:
            # Draw "Press E" prompt
            font = pygame.font.SysFont("Consolas", 16)
            prompt = font.render(f"PRESS E: {self.title}", True, (255, 255, 0))
            rect = prompt.get_rect(midbottom=(self.rect.centerx, self.rect.top - 10))
            screen.blit(prompt, rect)
            
            # Subtle glow
            pygame.draw.circle(screen, (0, 200, 255), self.rect.center, self.interaction_range, 1)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="virus"):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Glowing red triangle for virus
        points = [(12, 0), (0, 24), (24, 24)]
        pygame.draw.polygon(self.image, (255, 50, 50), points, 2)
        pygame.draw.polygon(self.image, (100, 0, 0), [(12, 4), (4, 20), (20, 20)])
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 2
        self.health = 30

    def update(self, player_pos):
        # Move towards player
        direction = (player_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)
