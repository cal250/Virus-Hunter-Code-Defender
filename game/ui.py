import pygame
import random

class HUD:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 14)
        self.title_font = pygame.font.SysFont("Consolas", 22, bold=True)
        self.h1_font = pygame.font.SysFont("Consolas", 28, bold=True)
        self.glow_color = (0, 255, 210)
        self.warn_color = (255, 210, 80)
        self.danger_color = (255, 80, 90)
        self.crt_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self._create_crt_grid()
        self.matrix_font = pygame.font.SysFont("Consolas", 14)
        self.matrix_chars = "01ABCDEF!@#$%^&*"

    def _create_crt_grid(self):
        for y in range(0, self.screen_height, 3):
            pygame.draw.line(self.crt_surface, (0, 0, 0, 60), (0, y), (self.screen_width, y))

    def _panel(self, w, h, alpha=200):
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((6, 14, 22, alpha))
        pygame.draw.rect(s, (0, 210, 255, 170), s.get_rect(), 2, border_radius=12)
        pygame.draw.rect(s, (0, 0, 0, 60), s.get_rect().inflate(-8, -8), 2, border_radius=10)
        return s

    def _draw_matrix(self, screen):
        # Majestic decryption matrix effect
        for _ in range(5):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            char = random.choice(self.matrix_chars)
            color = (0, 100, 50) if random.random() > 0.1 else (0, 255, 100)
            txt = self.matrix_font.render(char, True, color)
            screen.blit(txt, (x, y))

    def draw(self, screen, player, mission_text, scan_progress, level, shell_status=None, threat_level=None):
        # Matrix effect on Level 1
        if level == 1:
            self._draw_matrix(screen)
            
        # Left panel: DRONE status
        left = self._panel(310, 120, alpha=185)
        lx, ly = 18, 18
        screen.blit(left, (lx, ly))

        title = self.title_font.render("DRONE STATUS", True, self.glow_color)
        screen.blit(title, (lx + 16, ly + 12))

        # Health bar (with color ramp)
        hp_ratio = max(0.0, min(1.0, player.health / max(1, player.max_health)))
        bar_x, bar_y, bar_w, bar_h = lx + 16, ly + 50, 270, 14
        pygame.draw.rect(screen, (30, 35, 45), (bar_x, bar_y, bar_w, bar_h), border_radius=7)
        if hp_ratio > 0:
            if hp_ratio > 0.55:
                hp_color = (0, 255, 140)
            elif hp_ratio > 0.25:
                hp_color = self.warn_color
            else:
                hp_color = self.danger_color
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_w * hp_ratio), bar_h), border_radius=7)
        hp_txt = self.font.render(f"CORE INTEGRITY: {int(player.health)}%", True, (210, 230, 235))
        screen.blit(hp_txt, (lx + 16, ly + 74))

        # Signal / link status
        if shell_status:
            sig_color = self.glow_color if "CONNECTED" in shell_status else (150, 200, 210)
            if "RETRYING" in shell_status or "CONNECTING" in shell_status:
                sig_color = self.warn_color
            if "IDLE" in shell_status:
                sig_color = (150, 200, 210)
            sig = self.font_small.render(f"LINK: {shell_status}", True, sig_color)
            screen.blit(sig, (lx + 16, ly + 98))

        # Right panel: mission
        right_w = 420
        right = self._panel(right_w, 140, alpha=175)
        rx, ry = self.screen_width - right_w - 18, 18
        screen.blit(right, (rx, ry))
        mission_title = self.title_font.render("MISSION OBJECTIVE", True, self.glow_color)
        screen.blit(mission_title, (rx + 16, ry + 12))

        # Wrap mission text crudely to fit
        words = (mission_text or "").split()
        lines = []
        line = []
        for w in words:
            test = " ".join(line + [w])
            if self.font.size(test)[0] > (right_w - 32):
                if line:
                    lines.append(" ".join(line))
                line = [w]
            else:
                line.append(w)
        if line:
            lines.append(" ".join(line))
        for i, ln in enumerate(lines[:3]):
            mission_desc = self.font.render(ln, True, (170, 215, 220))
            screen.blit(mission_desc, (rx + 16, ry + 46 + i * 22))

        # Top center: title + level
        banner = self.h1_font.render("VIRUS HUNTER", True, (215, 245, 255))
        sub = self.font_small.render("CODE DEFENDER", True, (140, 200, 210))
        bx = (self.screen_width // 2) - (banner.get_width() // 2)
        screen.blit(banner, (bx, 18))
        screen.blit(sub, ((self.screen_width // 2) - (sub.get_width() // 2), 50))
        if threat_level is None:
            lvl_text = f"LEVEL {level}"
        else:
            lvl_text = f"LEVEL {level}  •  THREAT {int(threat_level)}"
        lvl = self.font_small.render(lvl_text, True, self.glow_color)
        screen.blit(lvl, ((self.screen_width // 2) - (lvl.get_width() // 2), 70))

        # Scan Progress Bar
        if scan_progress > 0:
            p_w = 420
            p_h = 12
            p_x = (self.screen_width // 2) - (p_w // 2)
            p_y = self.screen_height - 46
            pygame.draw.rect(screen, (30, 35, 45), (p_x, p_y, p_w, p_h), border_radius=7)
            fill_w = max(0, min(p_w, int((scan_progress / 100.0) * p_w)))
            if fill_w > 0:
                pygame.draw.rect(screen, self.glow_color, (p_x, p_y, fill_w, p_h), border_radius=7)
            scan_text = self.font.render(f"SYSTEM OPERATION... {scan_progress}%", True, self.glow_color)
            screen.blit(scan_text, (p_x + 8, p_y - 22))

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
