import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Drone sprite (stylized quadcopter)
        self.image = pygame.Surface((44, 44), pygame.SRCALPHA)
        cx, cy = 22, 22
        glow = (0, 255, 210)
        frame = (0, 120, 150)
        core_dark = (10, 40, 55)

        # Arms
        pygame.draw.line(self.image, frame, (8, cy), (36, cy), 4)
        pygame.draw.line(self.image, frame, (cx, 8), (cx, 36), 4)

        # Rotors
        for rx, ry in [(10, 10), (34, 10), (10, 34), (34, 34)]:
            pygame.draw.circle(self.image, (0, 0, 0, 120), (rx, ry), 7)
            pygame.draw.circle(self.image, glow, (rx, ry), 7, 2)
            pygame.draw.circle(self.image, (200, 255, 255), (rx, ry), 2)

        # Core
        pygame.draw.circle(self.image, (0, 0, 0, 140), (cx, cy), 12)
        pygame.draw.circle(self.image, glow, (cx, cy), 12, 2)
        pygame.draw.circle(self.image, core_dark, (cx, cy), 7)
        pygame.draw.circle(self.image, (255, 255, 255), (cx + 2, cy - 2), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.trail_positions = []
        self.speed = 6
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
        
        # Trail logic
        self.trail_positions.insert(0, tuple(self.pos))
        if len(self.trail_positions) > 10:
            self.trail_positions.pop()

    def draw(self, screen):
        # Draw trails
        for i, pos in enumerate(self.trail_positions):
            alpha = 140 - (i * 14)
            size = 44 - (i * 3)
            if size <= 0: continue
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 210, alpha), (size // 2, size // 2), max(1, size // 2), 2)
            screen.blit(s, s.get_rect(center=pos))
            
        screen.blit(self.image, self.rect)
