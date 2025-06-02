import pygame
import math
import random
from pygame import gfxdraw

# Inicializace
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulace sluneční soustavy")

# Barvy
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
COLORS = [
    (100, 100, 255), (200, 150, 100),
    (255, 200, 150), (150, 200, 255),
    (200, 255, 200), (255, 150, 150)
]

# Fyzikální parametry
NUM_PARTICLES = 2000  # Sníženo pro stabilitu
STAR_MASS = 20000     # Velká hmotnost hvězdy
G = 1.5               # Gravitační konstanta
MIN_DISTANCE = 60
MAX_DISTANCE = 350
DAMPING = 0.999       # Mírné tlumení

class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'mass', 'radius', 'color', 'fixed', 'age']
    
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.vx = 0
        self.vy = 0
        self.radius = max(1, int(math.log(mass + 1) * 1.3)
        self.color = random.choice(COLORS)
        self.fixed = False
        self.age = 0

    def update(self, particles, star):
        if self.fixed:
            return

        self.age += 1

        # Vektor ke hvězdě
        dx = star.x - self.x
        dy = star.y - self.y
        dist_sq = dx*dx + dy*dy
        dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.1

        # Silná gravitační síla
        force = G * star.mass * self.mass / dist_sq
        
        # Orbitální rychlost (Keplerův zákon)
        orbital_speed = math.sqrt(G * star.mass / dist)
        
        # Automatické nastavení orbitální rychlosti
        if self.age < 30:  # Prvních 30 snímků - stabilizace
            tangent_x = -dy/dist
            tangent_y = dx/dist
            self.vx = tangent_x * orbital_speed * random.uniform(0.97, 1.03)
            self.vy = tangent_y * orbital_speed * random.uniform(0.97, 1.03)
        
        # Aplikace gravitace
        self.vx += force * dx/dist * 0.00005
        self.vy += force * dy/dist * 0.00005
        
        # Tlumení
        self.vx *= DAMPING
        self.vy *= DAMPING

        # Kolize a shlukování
        if self.age > 60:  # Až po stabilizaci
            for p in particles[:]:
                if p is self or p.fixed or p.age <= 60:
                    continue
                    
                dx = p.x - self.x
                dy = p.y - self.y
                dist = math.hypot(dx, dy)
                min_dist = self.radius + p.radius

                if dist < min_dist:
                    # Spojení částic
                    total_mass = self.mass + p.mass
                    self.x = (self.x*self.mass + p.x*p.mass)/total_mass
                    self.y = (self.y*self.mass + p.y*p.mass)/total_mass
                    self.vx = (self.vx*self.mass + p.vx*p.mass)/total_mass
                    self.vy = (self.vy*self.mass + p.vy*p.mass)/total_mass
                    self.mass = total_mass
                    self.radius = max(2, int(math.log(total_mass + 1) * 1.3)
                    particles.remove(p)
                    break

        # Pohyb
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            if self.radius < 2:
                screen.set_at((x, y), self.color)
            else:
                gfxdraw.filled_circle(screen, x, y, self.radius, self.color)
                if self.radius > 2:
                    gfxdraw.aacircle(screen, x, y, self.radius, WHITE)

# Vytvoření hvězdy
star = Particle(WIDTH/2, HEIGHT/2, STAR_MASS)
star.color = YELLOW
star.fixed = True
star.radius = 20

def create_particles():
    particles = [star]
    for _ in range(NUM_PARTICLES):
        # Rozložení v disku s vyšší hustotou blíže středu
        r = (MIN_DISTANCE**2 + (MAX_DISTANCE**2 - MIN_DISTANCE**2) * random.random())**0.5
        angle = random.uniform(0, 2*math.pi)
        x = star.x + r * math.cos(angle)
        y = star.y + r * math.sin(angle)
        
        mass = random.uniform(0.8, 1.2)
        p = Particle(x, y, mass)
        
        # Přesná orbitální rychlost
        orbital_speed = math.sqrt(G * STAR_MASS / r)
        p.vx = -math.sin(angle) * orbital_speed
        p.vy = math.cos(angle) * orbital_speed
        
        particles.append(p)
    return particles

# Hlavní smyčka
def main():
    particles = create_particles()
    clock = pygame.time.Clock()
    running = True
    paused = False
    font = pygame.font.SysFont('Arial', 16)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    particles = create_particles()
        
        if not paused:
            # Aktualizace v náhodném pořadí
            for p in random.sample(particles, len(particles)):
                p.update(particles, star)
        
        # Vykreslení
        screen.fill(BLACK)
        
        # Nejprve hvězda
        star.draw(screen)
        
        # Pak částice seřazené podle vzdálenosti
        for p in sorted(particles, key=lambda p: -((p.x-star.x)**2 + (p.y-star.y)**2)):
            if not p.fixed:
                p.draw(screen)
        
        # Informace
        info = f"Částic: {len(particles)-1} | SPACE: pauza | R: reset"
        screen.blit(font.render(info, True, WHITE), (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()