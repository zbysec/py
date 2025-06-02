import pygame
import random
import math
from pygame.locals import *

# Inicializace
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Particles Simulator")

# Barvy
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)

# Nastavení
MAX_PARTICLES = 20000
MIN_PARTICLES = 100
DEFAULT_PARTICLES = 5000
ATTRACTION_RADIUS = 300
MAX_SPEED = 6
DAMPING = 0.96
MIN_FORCE = 0.1
MAX_FORCE = 10
DEFAULT_FORCE = 2.0

# Třída pro částice
class Particle:
    def __init__(self, x=None, y=None):
        self.x = random.randint(0, WIDTH) if x is None else x
        self.y = random.randint(0, HEIGHT) if y is None else y
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
        self.size = 1
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
    
    def update(self, target_x, target_y, attraction_mode, attraction_force):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < ATTRACTION_RADIUS and distance > 5:
            force = (ATTRACTION_RADIUS - distance) / ATTRACTION_RADIUS
            
            if attraction_mode:
                self.vx += dx/distance * force * attraction_force * 0.2
                self.vy += dy/distance * force * attraction_force * 0.2
            else:
                self.vx -= dx/distance * force * attraction_force * 0.2
                self.vy -= dy/distance * force * attraction_force * 0.2
        
        speed = math.sqrt(self.vx**2 + self.vy**2)
        if speed > MAX_SPEED:
            self.vx = (self.vx/speed) * MAX_SPEED
            self.vy = (self.vy/speed) * MAX_SPEED
        
        self.x += self.vx
        self.y += self.vy
        self.vx *= DAMPING
        self.vy *= DAMPING
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))
    
    def draw(self, surface):
        if 0 <= int(self.x) < WIDTH and 0 <= int(self.y) < HEIGHT:
            surface.set_at((int(self.x), int(self.y)), self.color)

# Třída pro křížek
class ExitButton:
    def __init__(self):
        self.size = 30
        self.rect = pygame.Rect(WIDTH - self.size - 20, 20, self.size, self.size)
    
    def draw(self, surface):
        pygame.draw.line(surface, RED, (self.rect.left, self.rect.top), 
                        (self.rect.right, self.rect.bottom), 3)
        pygame.draw.line(surface, RED, (self.rect.left, self.rect.bottom), 
                        (self.rect.right, self.rect.top), 3)
    
    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# Vytvoření ovládacích prvků
exit_button = ExitButton()

# Globální nastavení
particles = [Particle() for _ in range(DEFAULT_PARTICLES)]
attraction_mode = True
attraction_force = DEFAULT_FORCE

# Funkce pro změnu počtu částic
def adjust_particles(amount):
    global particles
    new_count = len(particles) + amount
    new_count = max(MIN_PARTICLES, min(MAX_PARTICLES, new_count))
    
    if new_count > len(particles):
        particles.extend([Particle() for _ in range(new_count - len(particles))])
    elif new_count < len(particles):
        particles = particles[:new_count]

# Funkce pro změnu síly interakce
def adjust_force(amount):
    global attraction_force
    attraction_force += amount
    attraction_force = max(MIN_FORCE, min(MAX_FORCE, attraction_force))

# Hlavní smyčka
running = True
clock = pygame.time.Clock()

while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    events = pygame.event.get()
    
    for event in events:
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Levé tlačítko
                if exit_button.check_click((mouse_x, mouse_y)):
                    running = False
                else:
                    # Reset s aktuálním počtem částic
                    particles = [Particle() for _ in range(len(particles))]
            elif event.button == 3:  # Pravé tlačítko
                attraction_mode = not attraction_mode
        elif event.type == MOUSEWHEEL:
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Shift + kolečko = změna síly
                adjust_force(event.y * 0.2)
            else:  # Pouze kolečko = změna počtu částic
                adjust_particles(event.y * 50)
    
    # Aktualizace částic
    for p in particles:
        p.update(mouse_x, mouse_y, attraction_mode, attraction_force)
    
    # Vykreslení
    screen.fill(BLACK)
    
    # Částice
    for p in particles:
        p.draw(screen)
    
    # Křížek pro ukončení
    exit_button.draw(screen)
    
    # Zobrazení aktuálních hodnot
    font = pygame.font.SysFont('Arial', 24)
    particles_text = font.render(f"Částic: {len(particles)}", True, WHITE)
    force_text = font.render(f"Síla: {attraction_force:.1f}", True, WHITE)
    mode_text = font.render(f"Režim: {'Přitahování' if attraction_mode else 'Odpuzování'}", 
                          True, WHITE if attraction_mode else RED)
    
    screen.blit(particles_text, (20, 20))
    screen.blit(force_text, (20, 50))
    screen.blit(mode_text, (20, 80))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()