import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 1200, 1200
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vznik sluneční soustavy")

clock = pygame.time.Clock()
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

PLANET_COLORS = [
    (169, 169, 169),  # Merkur
    (218, 165, 32),   # Venuše
    (0, 191, 255),    # Země
    (255, 69, 0),     # Mars
    (255, 215, 0),    # Jupiter
    (210, 180, 140),  # Saturn
    (173, 216, 230),  # Uran
    (72, 61, 139),    # Neptun
]

planet_data = [
    {"name": "Merkur", "distance": 50,  "size": 3,  "color": PLANET_COLORS[0], "particles": 200},
    {"name": "Venuše", "distance": 80,  "size": 5,  "color": PLANET_COLORS[1], "particles": 400},
    {"name": "Země",   "distance": 110, "size": 5,  "color": PLANET_COLORS[2], "particles": 400},
    {"name": "Mars",   "distance": 140, "size": 4,  "color": PLANET_COLORS[3], "particles": 300},
    {"name": "Jupiter","distance": 200, "size": 10, "color": PLANET_COLORS[4], "particles": 1000},
    {"name": "Saturn", "distance": 260, "size": 9,  "color": PLANET_COLORS[5], "particles": 800},
    {"name": "Uran",   "distance": 320, "size": 7,  "color": PLANET_COLORS[6], "particles": 600},
    {"name": "Neptun", "distance": 370, "size": 7,  "color": PLANET_COLORS[7], "particles": 500},
]

G = 6.67430e-1  # zmenšená gravitační konstanta pro simulaci
SUN_MASS = 10000
MIN_DIST_FROM_SUN = 20  # minimální vzdálenost od středu Slunce

particles = []
planets = []

def generate_particles():
    for data in planet_data:
        count = data["particles"]
        dist_base = data["distance"]
        color = data["color"]
        name = data["name"]
        for i in range(count):
            angle = 2 * math.pi * i / count
            dist = dist_base + random.uniform(-5, 5)
            x = CENTER[0] + dist * math.cos(angle)
            y = CENTER[1] + dist * math.sin(angle)
            # Přesná tangenciální rychlost pro kruhovou orbitu
            speed = math.sqrt(G * SUN_MASS / dist)
            vx = -math.sin(angle) * speed
            vy = math.cos(angle) * speed
            particles.append({
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "mass": 1,
                "radius": 1,
                "color": color,
                "planet": name,
                "merged": False,
            })

def draw_sun():
    pygame.draw.circle(screen, YELLOW, CENTER, 15)

def apply_gravity(p):
    dx = CENTER[0] - p["x"]
    dy = CENTER[1] - p["y"]
    dist = math.hypot(dx, dy)
    if dist < MIN_DIST_FROM_SUN:
        dist = MIN_DIST_FROM_SUN  # nepujde blíže k Slunci, aby nespadl
    force = G * SUN_MASS / (dist ** 2)
    ax = force * dx / dist
    ay = force * dy / dist
    return ax, ay

def update_motion():
    damping = 0.995  # tlumení rychlosti
    for p in particles:
        ax, ay = apply_gravity(p)
        p["vx"] += ax
        p["vy"] += ay
        p["vx"] *= damping
        p["vy"] *= damping
        p["x"] += p["vx"]
        p["y"] += p["vy"]

    for p in planets:
        ax, ay = apply_gravity(p)
        p["vx"] += ax
        p["vy"] += ay
        p["vx"] *= damping
        p["vy"] *= damping
        p["x"] += p["vx"]
        p["y"] += p["vy"]

def merge_particles():
    global particles, planets
    new_particles = []
    used = set()
    for i, p in enumerate(particles):
        if i in used or p["merged"]:
            continue
        merged = False
        for j in range(i + 1, len(particles)):
            if j in used or particles[j]["merged"]:
                continue
            other = particles[j]
            if p["planet"] != other["planet"]:
                continue
            dx = other["x"] - p["x"]
            dy = other["y"] - p["y"]
            dist = math.hypot(dx, dy)
            if dist < 3:
                total_mass = p["mass"] + other["mass"]
                new_vx = ((p["vx"] * p["mass"] + other["vx"] * other["mass"]) / total_mass) * 0.7
                new_vy = ((p["vy"] * p["mass"] + other["vy"] * other["mass"]) / total_mass) * 0.7
                new_particle = {
                    "x": (p["x"] + other["x"]) / 2,
                    "y": (p["y"] + other["y"]) / 2,
                    "vx": new_vx,
                    "vy": new_vy,
                    "mass": total_mass,
                    "radius": min(25, 1 + total_mass ** 0.3),
                    "color": p["color"],
                    "planet": p["planet"],
                    "merged": False,
                }
                if total_mass > 20:
                    new_particle["merged"] = True
                    planets.append(new_particle)
                else:
                    new_particles.append(new_particle)
                used.add(j)
                merged = True
                break
        if not merged:
            new_particles.append(p)
    particles = new_particles

def draw_objects():
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), 1)
    for p in planets:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), int(p["radius"]))

generate_particles()

running = True
while running:
    screen.fill(BLACK)
    draw_sun()
    update_motion()
    merge_particles()
    draw_objects()
    pygame.display.flip()
    clock.tick(240)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
