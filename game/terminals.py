import pygame
import random

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
        # Scarier "virus" sprite: spiked cell + nucleus + eyes
        self.base_size = 52
        self._seed = random.randint(0, 10_000_000)
        self._phase = random.random() * 6.28
        self.image = self._render_virus(int(self.base_size))
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.speed = 2.2
        self.health = 30

    def _render_virus(self, size: int) -> pygame.Surface:
        rnd = random.Random(self._seed)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        outer_r = int(size * 0.34)
        inner_r = int(size * 0.22)

        # Outer glow
        for i in range(5, 0, -1):
            a = 18 * i
            pygame.draw.circle(s, (255, 40, 70, a), (cx, cy), outer_r + i * 3)

        # Spikes
        spike_count = 12
        for i in range(spike_count):
            ang = (i / spike_count) * 6.28318 + rnd.uniform(-0.12, 0.12)
            tip_r = outer_r + rnd.randint(10, 16)
            base_r = outer_r - rnd.randint(2, 5)
            bw = rnd.randint(5, 7)
            tip = (cx + int(tip_r * pygame.math.Vector2(1, 0).rotate_rad(ang).x),
                   cy + int(tip_r * pygame.math.Vector2(1, 0).rotate_rad(ang).y))
            left = (cx + int(base_r * pygame.math.Vector2(1, 0).rotate_rad(ang + 0.25).x),
                    cy + int(base_r * pygame.math.Vector2(1, 0).rotate_rad(ang + 0.25).y))
            right = (cx + int(base_r * pygame.math.Vector2(1, 0).rotate_rad(ang - 0.25).x),
                     cy + int(base_r * pygame.math.Vector2(1, 0).rotate_rad(ang - 0.25).y))
            pygame.draw.polygon(s, (120, 0, 20, 220), [tip, left, right])
            pygame.draw.polygon(s, (255, 70, 90, 200), [tip, left, right], 2)
            pygame.draw.circle(s, (255, 70, 90, 180), tip, max(2, bw // 2))

        # Body
        pygame.draw.circle(s, (40, 0, 8, 240), (cx, cy), outer_r)
        pygame.draw.circle(s, (255, 70, 90, 210), (cx, cy), outer_r, 2)
        pygame.draw.circle(s, (120, 0, 20, 160), (cx - 5, cy - 6), int(outer_r * 0.72))

        # Veins/cracks
        for _ in range(6):
            a = rnd.uniform(0, 6.28318)
            p1 = pygame.Vector2(cx, cy) + pygame.Vector2(rnd.uniform(-4, 4), rnd.uniform(-4, 4))
            p2 = pygame.Vector2(cx, cy) + pygame.Vector2(1, 0).rotate_rad(a) * rnd.uniform(inner_r, outer_r - 2)
            pygame.draw.line(s, (200, 30, 60, 140), p1, p2, 2)
            pygame.draw.line(s, (60, 0, 0, 180), p1, p2, 1)

        # Nucleus
        pygame.draw.circle(s, (0, 0, 0, 160), (cx + 4, cy + 3), inner_r + 4)
        pygame.draw.circle(s, (180, 0, 40, 220), (cx + 4, cy + 3), inner_r + 2)
        pygame.draw.circle(s, (255, 120, 140, 220), (cx + 2, cy + 1), int(inner_r * 0.65))

        # Eyes (subtle, creepy)
        eye_y = cy - 6
        for ex in (cx - 8, cx + 8):
            pygame.draw.circle(s, (0, 0, 0, 210), (ex, eye_y), 6)
            pygame.draw.circle(s, (255, 220, 230, 220), (ex, eye_y), 4)
            pygame.draw.circle(s, (10, 0, 0, 255), (ex + 1, eye_y + 1), 2)
            pygame.draw.circle(s, (255, 255, 255, 255), (ex - 1, eye_y - 1), 1)

        return s

    def update(self, player_pos):
        # Move towards player
        direction = (player_pos - self.pos)
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.center = self.pos

        # Subtle pulse (re-render at two sizes)
        self._phase += 0.12
        pulse = 1.0 + 0.04 * (1 if int(self._phase) % 2 == 0 else -1)
        size = int(self.base_size * pulse)
        size = max(40, min(60, size))
        self.image = self._render_virus(size)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
