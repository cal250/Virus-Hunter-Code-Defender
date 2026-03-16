import pygame
import random

class HUD:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Consolas", 18)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        self.glow_color = (0, 255, 200)
        self.crt_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self._create_crt_grid()
        self.matrix_font = pygame.font.SysFont("Consolas", 14)
        self.matrix_chars = "01ABCDEF!@#$%^&*"

    def _create_crt_grid(self):
        for y in range(0, self.screen_height, 3):
            pygame.draw.line(self.crt_surface, (0, 0, 0, 60), (0, y), (self.screen_width, y))

    def _draw_matrix(self, screen):
        # Majestic decryption matrix effect
        for _ in range(5):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            char = random.choice(self.matrix_chars)
            color = (0, 100, 50) if random.random() > 0.1 else (0, 255, 100)
            txt = self.matrix_font.render(char, True, color)
            screen.blit(txt, (x, y))

    def draw(self, screen, player, mission_text, scan_progress, level):
        # Matrix effect on Level 1
        if level == 1:
            self._draw_matrix(screen)
            
        # Health Bar
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20), border_radius=5)
        health_width = (player.health / player.max_health) * 200
        pygame.draw.rect(screen, (0, 255, 100), (20, 20, health_width, 20), border_radius=5)
        
        health_text = self.font.render(f"CORE INTEGRITY: {player.health}%", True, (200, 255, 200))
        screen.blit(health_text, (20, 45))

        # Mission Info
        mission_title = self.title_font.render("MISSION OBJECTIVE", True, self.glow_color)
        screen.blit(mission_title, (self.screen_width - 250, 20))
        
        mission_desc = self.font.render(mission_text, True, (150, 200, 200))
        screen.blit(mission_desc, (self.screen_width - 250, 50))

        # Scan Progress Bar
        if scan_progress > 0:
            p_rect = (self.screen_width // 2 - 150, self.screen_height - 50, 300, 10)
            pygame.draw.rect(screen, (50, 50, 50), p_rect)
            pygame.draw.rect(screen, self.glow_color, (p_rect[0], p_rect[1], 3 * scan_progress, 10))
            scan_text = self.font.render(f"DECRYPTING SYSTEM... {scan_progress}%", True, self.glow_color)
            screen.blit(scan_text, (self.screen_width // 2 - 80, self.screen_height - 80))

        # CRT Overlay
        screen.blit(self.crt_surface, (0, 0))

    def draw_pointer(self, screen, player_pos, target_pos):
        direction = pygame.Vector2(target_pos) - pygame.Vector2(player_pos)
        if direction.length() < 100: return
        
        direction = direction.normalize()
        pointer_pos = pygame.Vector2(player_pos) + direction * 60
        
        pygame.draw.circle(screen, self.glow_color, pointer_pos, 5)
        p1 = pointer_pos + direction * 10
        p2 = pointer_pos + direction.rotate(135) * 8
        p3 = pointer_pos + direction.rotate(-135) * 8
        pygame.draw.polygon(screen, self.glow_color, [p1, p2, p3])

class TerminalUI:
    @staticmethod
    def draw_box(screen, rect, title):
        pygame.draw.rect(screen, (5, 15, 25), rect)
        pygame.draw.rect(screen, (0, 200, 255), rect, 2)
        font = pygame.font.SysFont("Consolas", 20, bold=True)
        text = font.render(title, True, (0, 200, 255))
        screen.blit(text, (rect[0] + 10, rect[1] + 10))
