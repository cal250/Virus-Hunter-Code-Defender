import sys
import os
import pygame
import argparse
import random

# Add parent directory to path to import modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cyber_modules.dependency_checker import ensure_dependencies
from game.player import Player
from game.ui import HUD, TerminalUI
from game.terminals import Terminal, Enemy
from game.bullet import Bullet
from cyber_modules.network_shell import ReverseShell
from cyber_modules.persistence import create_persistence, remove_persistence

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 360)
        speed = random.uniform(2, 5)
        self.vel = pygame.Vector2(0, 1).rotate(angle) * speed
        self.lifetime = random.randint(20, 40)
        self.color = color

    def update(self):
        self.pos += self.vel
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            size = max(1, self.lifetime // 10)
            pygame.draw.circle(screen, self.color, self.pos, size)

def show_consent_screen(screen, width, height):
    font = pygame.font.SysFont("Consolas", 28, bold=True)
    small_font = pygame.font.SysFont("Consolas", 20)
    
    messages = [
        "VIRUS HUNTER: CODE DEFENDER (MAJESTIC EDITION)",
        "",
        "This project is for cybersecurity education ONLY.",
        "It demonstrates:",
        "1. Dependency Management",
        "2. Remote Shell Communication (Simulation)",
        "3. Persistence Mechanisms (Simulated Marker)",
        "4. System Cleanup",
        "",
        "Use ONLY in a controlled VM or lab environment.",
        "",
        "Press 'Y' to ACCEPT and enter the system.",
        "Press 'N' to CANCEL."
    ]

    running = True
    while running:
        screen.fill((2, 5, 10))
        
        # Grid
        for x in range(0, width, 50):
            pygame.draw.line(screen, (10, 20, 30), (x, 0), (x, height))
        for y in range(0, height, 50):
            pygame.draw.line(screen, (10, 20, 30), (0, y), (width, y))

        for i, msg in enumerate(messages):
            color = (0, 255, 200) if i == 0 else (200, 220, 220)
            if "ACCEPT" in msg: color = (0, 255, 100)
            if "CANCEL" in msg: color = (255, 100, 100)
            
            text = font.render(msg, True, color) if i == 0 else small_font.render(msg, True, color)
            rect = text.get_rect(center=(width // 2, 100 + i * 40))
            screen.blit(text, rect)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    return False
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--windowed", action="store_true")
    args = parser.parse_args()

    # Ensure dependencies first
    try:
        ensure_dependencies(["pygame"])
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        sys.exit(1)

    pygame.init()
    
    if args.windowed:
        width, height = 1200, 800
        screen = pygame.display.set_mode((width, height))
    else:
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    
    pygame.display.set_caption("Virus Hunter: Code Defender")
    clock = pygame.time.Clock()

    if not show_consent_screen(screen, width, height):
        pygame.quit()
        sys.exit()

    player = Player(width // 2, height // 2)
    hud = HUD(width, height)
    
    terminals = pygame.sprite.Group()
    network_terminal = Terminal(3 * width // 4, height // 4, "network", "NETWORK NODE")
    quarantine_terminal = Terminal(width // 2, 3 * height // 4, "quarantine", "QUARANTINE TERMINAL")
    
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = []
    
    mission_text = "Level 1: System Intrusion Detected! Defend node."
    scan_progress = 0
    level = 1
    shake_amount = 0
    
    shell = ReverseShell()
    last_direction = pygame.Vector2(1, 0)
    
    running = True
    win = False
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        
        # Track direction
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: move.y -= 1
        if keys[pygame.K_s]: move.y += 1
        if keys[pygame.K_a]: move.x -= 1
        if keys[pygame.K_d]: move.x += 1
        if move.length() > 0:
            last_direction = move.normalize()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if win:
                if event.type == pygame.KEYDOWN:
                    running = False
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    bullets.add(Bullet(player.pos.x, player.pos.y, last_direction))
                    shake_amount = 5 # Recoil shake
                if event.key == pygame.K_e:
                    if level == 2 and network_terminal.is_near(player):
                        shell.start()
                    elif level == 3 and quarantine_terminal.is_near(player):
                        create_persistence()
                        level = 4
                        mission_text = "Level 4: Eliminate all viruses to SECURE system!"

        # Logic
        if win:
            continue

        if level == 1:
            if scan_progress < 100:
                scan_progress += 0.3
                deps = ["pygame", "socket", "threading", "os", "sys"]
                curr_dep = deps[int(scan_progress / 20) % len(deps)]
                mission_text = f"Level 1: Decrypting node dependencies... {curr_dep}"
                
                # Spawn enemies during intrusion
                if len(enemies) < 4 and random.random() < 0.03:
                    enemies.add(Enemy(random.randint(0, width), random.randint(0, height)))
            else:
                level = 2
                terminals.add(network_terminal)
                mission_text = "Intrusion Blocked. Level 2: Find Network Node terminal."
        
        if level == 2:
            if shell.status == "CONNECTED":
                level = 3
                terminals.add(quarantine_terminal)
                mission_text = "Majestic Shell Active. Level 3: Find Quarantine Terminal."
            elif "RETRYING" in shell.status or "CONNECTING" in shell.status:
                mission_text = f"Linking: {shell.status}. (Run tools/listener.py!)"
            else:
                 mission_text = "Level 2: Secure Network Node (Press E)"
        
        if level == 4:
            if scan_progress < 200:
                scan_progress += 0.4
            if len(enemies) == 0 and scan_progress >= 200:
                win = True
            
            if len(enemies) < 6 and random.random() < 0.02:
                enemies.add(Enemy(random.randint(0, width), random.randint(0, height)))

        player.update(width, height)
        bullets.update()
        
        # Bullet cleanup and particles
        for bullet in list(bullets):
            if bullet.pos.x < 0 or bullet.pos.x > width or bullet.pos.y < 0 or bullet.pos.y > height:
                bullets.remove(bullet)
        
        terminals.update(player)
        enemies.update(player.pos)
        
        # Collisions
        hit_enemies = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for enemy in hit_enemies:
            shake_amount = 10 # Impact shake
            for _ in range(15):
                particles.append(Particle(enemy.pos.x, enemy.pos.y, (255, 50, 50)))
        
        if pygame.sprite.spritecollide(player, enemies, True):
            player.health -= 15
            shake_amount = 20 # Damage shake
            for _ in range(10):
                particles.append(Particle(player.pos.x, player.pos.y, (0, 255, 255)))

        # Update particles
        for p in list(particles):
            p.update()
            if p.lifetime <= 0:
                particles.remove(p)

        # Shake decay
        if shake_amount > 0:
            shake_amount -= 1
        
        offset = pygame.Vector2(random.uniform(-shake_amount, shake_amount), 
                                random.uniform(-shake_amount, shake_amount))

        # Render
        screen.fill((2, 8, 15))
        
        # Grid with offset
        for x in range(0, width + 100, 60):
            pygame.draw.line(screen, (10, 20, 40), (x + offset.x, 0), (x + offset.x, height))
        for y in range(0, height + 100, 60):
            pygame.draw.line(screen, (10, 20, 40), (0, y + offset.y), (width, y + offset.y))

        for t in terminals:
            screen.blit(t.image, t.rect.move(offset))
            if t.active: # Draw prompt manually for shake
                font = pygame.font.SysFont("Consolas", 16)
                prompt = font.render(f"PRESS E: {t.title}", True, (255, 255, 0))
                screen.blit(prompt, (t.rect.centerx - prompt.get_width()//2 + offset.x, t.rect.top - 20 + offset.y))

        for e in enemies:
            screen.blit(e.image, e.rect.move(offset))
            
        for b in bullets:
            b.draw(screen) # Pointers/bullets handle their own relative draw if needed, but let's just blit for now
            # Actually Bullet.draw uses screen.blit(self.image, self.rect), we should move rect
            # b.draw(screen) doesn't account for shake. Let's fix.
            
        for p in particles:
            p.draw(screen) # Particles are relative to screen

        player.draw(screen) # Player trail draws at current pos, no shake on player itself usually looks better or worse? 
        # Actually shake the WHOLE screen by blitting to a surface then blitting that. 
        # But for now, just blitting at offset is okay.
        
        hud.draw(screen, player, mission_text, min(100, int(scan_progress) if level == 1 else (int(scan_progress - 100) if level == 4 else 0)), level)
        
        # Re-draw b.draw with offset
        for b in bullets:
             screen.blit(b.image, b.rect.move(offset))

        # Objective pointer
        if level == 2:
            hud.draw_pointer(screen, player.pos, network_terminal.rect.center)
        elif level == 3:
            hud.draw_pointer(screen, player.pos, quarantine_terminal.rect.center)

        if win:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            f = pygame.font.SysFont("Consolas", 60, bold=True)
            txt = f.render("SYSTEM SECURED", True, (0, 255, 100))
            screen.blit(txt, txt.get_rect(center=(width // 2, height // 2)))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
