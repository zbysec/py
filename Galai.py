# gravitace.py
# GPU-akcelerovaný gravitační simulátor pixelů pomocí pygame + numba

import pygame
import numpy as np
from numba import njit, prange
import ctypes
import random
import sys

pygame.init()

# Zjisti rozlišení obrazovky a nastav formát 16:9
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = int(screen_width * 9 / 16)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tvorba Galaxie")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SUN_X, SUN_Y = screen_width / 2, screen_height / 2
SUN_MASS = 200.0
G = 1.0

num_particles = 1000
speed_multiplier = 1.0

positions = np.random.rand(num_particles, 2).astype(np.float32)
positions[:, 0] *= screen_width
positions[:, 1] *= screen_height

masses = np.ones(num_particles, dtype=np.float32)

velocities = np.zeros((num_particles, 2), dtype=np.float32)
dx = positions[:, 0] - SUN_X
dy = positions[:, 1] - SUN_Y
dist = np.sqrt(dx**2 + dy**2)
speed = np.sqrt(G * SUN_MASS / (dist + 1e-5))
velocities[:, 0] = -dy / dist * speed
velocities[:, 1] = dx / dist * speed

@njit(parallel=True)
def apply_gravity_and_update(positions, velocities, masses, sun_x, sun_y, sun_mass, g, speed_multiplier):
    for i in prange(positions.shape[0]):
        dx = sun_x - positions[i, 0]
        dy = sun_y - positions[i, 1]
        dist_sq = dx*dx + dy*dy
        dist = np.sqrt(dist_sq)
        if dist < 1:
            continue
        force = g * masses[i] * sun_mass / dist_sq
        ax = force * dx / dist / masses[i]
        ay = force * dy / dist / masses[i]

        # Víření - slabé zakřivení pohybu
        perp = 0.05
        ax += perp * -dy / (dist + 1e-5)
        ay += perp * dx / (dist + 1e-5)

        velocities[i, 0] += ax
        velocities[i, 1] += ay

        positions[i, 0] += velocities[i, 0] * speed_multiplier
        positions[i, 1] += velocities[i, 1] * speed_multiplier

def get_color(distance):
    if distance < 100:
        return (255, 255, 255)  # bílá
    elif distance < 200:
        return (255, 255, 0)    # žlutá
    elif distance < 300:
        return (255, 165, 0)    # oranžová
    elif distance < 400:
        return (255, 0, 0)      # červená
    else:
        return (128, 0, 255)    # fialová

font = pygame.font.SysFont(None, 24)
def draw_info():
    np_text = font.render(f"Počet částic: {positions.shape[0]}", True, (200, 200, 200))
    sp_text = font.render(f"Rychlost: {speed_multiplier:.1f}x", True, (200, 200, 200))
    screen.blit(np_text, (20, screen_height - 40))
    screen.blit(sp_text, (20, screen_height - 20))

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                speed_multiplier = min(speed_multiplier + 0.2, 10.0)
            elif event.button == 3:
                new_count = 100
                new_pos = np.random.rand(new_count, 2).astype(np.float32)
                new_pos[:, 0] *= screen_width
                new_pos[:, 1] *= screen_height
                new_mass = np.ones(new_count, dtype=np.float32)
                new_vel = np.zeros((new_count, 2), dtype=np.float32)
                dx = new_pos[:, 0] - SUN_X
                dy = new_pos[:, 1] - SUN_Y
                dist = np.sqrt(dx**2 + dy**2)
                spd = np.sqrt(G * SUN_MASS / (dist + 1e-5))
                new_vel[:, 0] = -dy / dist * spd
                new_vel[:, 1] = dx / dist * spd
                positions = np.vstack((positions, new_pos))
                masses = np.hstack((masses, new_mass))
                velocities = np.vstack((velocities, new_vel))
            elif event.button == 4:
                speed_multiplier = min(speed_multiplier + 0.1, 10.0)
            elif event.button == 5:
                speed_multiplier = max(speed_multiplier - 0.1, 0.1)

    apply_gravity_and_update(positions, velocities, masses, SUN_X, SUN_Y, SUN_MASS, G, speed_multiplier)

    # Černá díra s bílým okrajem
    pygame.draw.circle(screen, WHITE, (int(SUN_X), int(SUN_Y)), 6)
    pygame.draw.circle(screen, BLACK, (int(SUN_X), int(SUN_Y)), 4)

    for i in range(positions.shape[0]):
        dist = np.sqrt((positions[i, 0] - SUN_X) ** 2 + (positions[i, 1] - SUN_Y) ** 2)
        color = get_color(dist)
        pygame.draw.circle(screen, color, (int(positions[i, 0]), int(positions[i, 1])), 2)

    draw_info()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
