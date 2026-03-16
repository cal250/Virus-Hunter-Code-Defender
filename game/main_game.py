import sys
import os
import pygame
import argparse

# Add parent directory to path to import modules properly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cyber_modules.dependency_checker import ensure_dependencies
from game.player import Player
from game.ui import HUD, TerminalUI
from game.terminals import Terminal, Enemy
from game.bullet import Bullet
from cyber_modules.network_shell import ReverseShell
from cyber_modules.persistence import create_persistence, remove_persistence

def show_consent_screen(screen, width, height):
    font = pygame.font.SysFont("Consolas", 24)
    small_font = pygame.font.SysFont("Consolas", 18)
    
    messages = [
        "VIRUS HUNTER: CODE DEFENDER",
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
        
        # Subtle grid
        for x in range(0, width, 50):
            pygame.draw.line(screen, (10, 20, 30), (x, 0), (x, height))
        for y in range(0, height, 50):
            pygame.draw.line(screen, (10, 20, 30), (0, y), (width, y))

        for i, msg in enumerate(messages):
            color = (0, 255, 200) if i == 0 else (200, 220, 220)
            if "ACCEPT" in msg: color = (0, 255, 100)
            if "CANCEL" in msg: color = (255, 100, 100)
            
            text = font.render(msg, True, color)
            rect = text.get_rect(center=(width // 2, 100 + i * 35))
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
    scan_terminal = Terminal(width // 4, height // 4, "scan", "SYSTEM SCANNER")
    network_terminal = Terminal(3 * width // 4, height // 4, "network", "NETWORK NODE")
    quarantine_terminal = Terminal(width // 2, 3 * height // 4, "quarantine", "QUARANTINE TERMINAL")
    terminals.add(scan_terminal)
    
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    
    mission_text = "Level 1: Interact with System Scanner"
    scan_progress = 0
    is_scanning = False
    level = 1
    persistence_created = False
    
    shell = ReverseShell()
    
    running = True
    win = False
    while running:
        delta_time = clock.tick(60) / 1000.0
        
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
                    bullets.add(Bullet(player.pos.x, player.pos.y, pygame.Vector2(1, 0)))
                if event.key == pygame.K_e:
                    if level == 1 and scan_terminal.is_near(player):
                        is_scanning = True
                        mission_text = "Level 1: System Scanning..."
                    elif level == 2 and network_terminal.is_near(player):
                        shell.start()
                        mission_text = "Level 2: SHELL ACTIVE - Check Listener! (Find Quarantine)"
                        level = 3
                        terminals.add(quarantine_terminal)
                    elif level == 3 and quarantine_terminal.is_near(player):
                        persistence_created, path = create_persistence()
                        mission_text = "Level 3: Malware persistence detected. Clean the system!"
                        level = 4
                        mission_text = "Level 4: Eliminate all viruses to SECURE system!"

        # Logic
        if win:
            continue

        if level == 1 and is_scanning:
            if scan_progress < 100:
                scan_progress += 0.5
            else:
                is_scanning = False
                level = 2
                terminals.add(network_terminal)
                mission_text = "Level 1 Complete! Find Network Node."
        
        if level == 4:
            if len(enemies) == 0 and not is_scanning: # Final cleanup condition
                # Wait for some enemies to spawn and then be killed
                if scan_progress > 100: # Reuse scan_progress as a counter or similar
                    win = True
                    mission_text = "SYSTEM SECURED. Press any key to exit."
            
            # Spawn some final enemies if level 4
            if len(enemies) < 5:
                import random
                if random.random() < 0.01:
                    enemies.add(Enemy(random.randint(0, width), random.randint(0, height)))
            
            # Use scan_progress to track "Cleanup" in level 4
            if scan_progress < 200:
                scan_progress += 0.2

        player.update(width, height)
        bullets.update()
        
        # Simple bullet removal
        for bullet in list(bullets):
            if bullet.pos.x < 0 or bullet.pos.x > width or bullet.pos.y < 0 or bullet.pos.y > height:
                bullets.remove(bullet)

        terminals.update(player)
        
        # Spawn logic (simple placeholder)
        if len(enemies) < 3 and is_scanning:
             import random
             if random.random() < 0.02:
                 enemies.add(Enemy(random.randint(0, width), random.randint(0, height)))

        enemies.update(player.pos)
        
        # Collisions
        pygame.sprite.groupcollide(bullets, enemies, True, True)
        if pygame.sprite.spritecollide(player, enemies, True):
            player.health -= 10

        # Render
        screen.fill((5, 10, 20))
        
        # Grid
        for x in range(0, width, 60):
            pygame.draw.line(screen, (15, 25, 40), (x, 0), (x, height))
        for y in range(0, height, 60):
            pygame.draw.line(screen, (15, 25, 40), (0, y), (width, y))

        terminals.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        player.draw(screen)
        hud.draw(screen, player, mission_text, min(100, int(scan_progress)))
        
        if win:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            big_font = pygame.font.SysFont("Consolas", 72, bold=True)
            win_text = big_font.render("SYSTEM SECURED", True, (0, 255, 100))
            rect = win_text.get_rect(center=(width // 2, height // 2 - 50))
            screen.blit(win_text, rect)
            
            sub_font = pygame.font.SysFont("Consolas", 24)
            sub_text = sub_font.render("All malware removed. Malware persistence identified and neutralized.", True, (200, 255, 200))
            rect2 = sub_text.get_rect(center=(width // 2, height // 2 + 50))
            screen.blit(sub_text, rect2)
            
            exit_text = sub_font.render("Press any key to escape...", True, (255, 255, 255))
            rect3 = exit_text.get_rect(center=(width // 2, height // 2 + 100))
            screen.blit(exit_text, rect3)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
