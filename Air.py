import pygame
import sys
import random
import math

pygame.init()

# Fullscreen okno a získání správné velikosti obrazovky
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Barvy
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Poměr stran hřiště
TABLE_ASPECT_RATIO = 2.0  # šířka : výška
FPS = 60
FRICTION = 0.98
AI_DIFFICULTY = 0.7

# Výpočet velikosti stolu (bez okrajů)
table_height = SCREEN_HEIGHT
table_width = int(table_height * TABLE_ASPECT_RATIO)

# Pokud přesahuje obrazovku, přizpůsobíme výšku
if table_width > SCREEN_WIDTH:
    table_width = SCREEN_WIDTH
    table_height = int(table_width / TABLE_ASPECT_RATIO)

TABLE_WIDTH = table_width
TABLE_HEIGHT = table_height

# Umístění stolu
TABLE_X = (SCREEN_WIDTH - TABLE_WIDTH) // 2
TABLE_Y = (SCREEN_HEIGHT - TABLE_HEIGHT) // 2

# Herní prvky
PUCK_RADIUS = max(10, TABLE_HEIGHT // 30)
PADDLE_RADIUS = max(15, TABLE_HEIGHT // 25)
GOAL_WIDTH = TABLE_HEIGHT // 3
GOAL_DEPTH = TABLE_WIDTH // 20
PUCK_SPEED_LIMIT = TABLE_WIDTH // 30
PADDLE_SPEED = TABLE_WIDTH // 120

class Paddle:
    def __init__(self, x, y, color, is_ai=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = PADDLE_RADIUS
        self.speed = PADDLE_SPEED
        self.is_ai = is_ai
        self.target_x = x
        self.target_y = y

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 5)

    def move_to_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        if distance > 5:
            move_speed = min(distance, self.speed)
            self.x += dx / distance * move_speed
            self.y += dy / distance * move_speed

class Puck:
    def __init__(self):
        self.reset()
        self.radius = PUCK_RADIUS

    def reset(self):
        self.x = TABLE_X + TABLE_WIDTH // 2
        self.y = TABLE_Y + TABLE_HEIGHT // 2
        angle = random.uniform(0, 2 * math.pi)
        speed = PUCK_SPEED_LIMIT * 0.6
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= FRICTION
        self.dy *= FRICTION
        speed = math.hypot(self.dx, self.dy)
        if speed > PUCK_SPEED_LIMIT:
            scale = PUCK_SPEED_LIMIT / speed
            self.dx *= scale
            self.dy *= scale

    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 5)

class AirHockeyGame:
    def __init__(self):
        self.player = Paddle(TABLE_X + TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, BLUE)
        self.ai = Paddle(TABLE_X + 3 * TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, RED, is_ai=True)
        self.puck = Puck()
        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont('Arial', TABLE_HEIGHT // 15)
        self.small_font = pygame.font.SysFont('Arial', TABLE_HEIGHT // 30)
        self.center_line_width = max(2, TABLE_WIDTH // 300)
        self.border_width = max(5, TABLE_HEIGHT // 50)
        self.goal_color = (100, 100, 100)
        self.table_rect = pygame.Rect(TABLE_X, TABLE_Y, TABLE_WIDTH, TABLE_HEIGHT)
        self.inner_rect = pygame.Rect(TABLE_X + self.border_width, TABLE_Y + self.border_width,
                                      TABLE_WIDTH - 2 * self.border_width, TABLE_HEIGHT - 2 * self.border_width)

    def handle_collisions(self):
        for paddle in [self.player, self.ai]:
            distance = math.hypot(self.puck.x - paddle.x, self.puck.y - paddle.y)
            if distance < self.puck.radius + paddle.radius:
                angle = math.atan2(self.puck.y - paddle.y, self.puck.x - paddle.x)
                force = PUCK_SPEED_LIMIT * 0.8
                if paddle.is_ai:
                    target_angle = math.atan2(TABLE_Y + TABLE_HEIGHT // 2 - paddle.y, TABLE_X - paddle.x)
                    angle = angle * (1 - AI_DIFFICULTY * 0.3) + target_angle * (AI_DIFFICULTY * 0.3)
                self.puck.dx = math.cos(angle) * force
                self.puck.dy = math.sin(angle) * force
                overlap = (self.puck.radius + paddle.radius) - distance
                self.puck.x += math.cos(angle) * overlap * 0.5
                self.puck.y += math.sin(angle) * overlap * 0.5

        if self.puck.y - self.puck.radius <= self.inner_rect.top:
            self.puck.y = self.inner_rect.top + self.puck.radius
            self.puck.dy *= -0.9
        if self.puck.y + self.puck.radius >= self.inner_rect.bottom:
            self.puck.y = self.inner_rect.bottom - self.puck.radius
            self.puck.dy *= -0.9

        if self.puck.x - self.puck.radius <= self.table_rect.left:
            if self.inner_rect.centery - GOAL_WIDTH // 2 < self.puck.y < self.inner_rect.centery + GOAL_WIDTH // 2:
                self.ai_score += 1
                self.puck.reset()
            else:
                self.puck.x = self.table_rect.left + self.puck.radius
                self.puck.dx *= -0.8

        if self.puck.x + self.puck.radius >= self.table_rect.right:
            if self.inner_rect.centery - GOAL_WIDTH // 2 < self.puck.y < self.inner_rect.centery + GOAL_WIDTH // 2:
                self.player_score += 1
                self.puck.reset()
            else:
                self.puck.x = self.table_rect.right - self.puck.radius
                self.puck.dx *= -0.8

    def ai_move(self):
        if self.puck.dx > 0:
            predict_x = self.puck.x + self.puck.dx * 15
            predict_y = self.puck.y + self.puck.dy * 15
            error = (1 - AI_DIFFICULTY) * random.uniform(-100, 100)
            self.ai.target_x = max(TABLE_X + TABLE_WIDTH // 2,
                                   min(TABLE_X + TABLE_WIDTH - PADDLE_RADIUS, predict_x + error))
            self.ai.target_y = max(TABLE_Y + PADDLE_RADIUS,
                                   min(TABLE_Y + TABLE_HEIGHT - PADDLE_RADIUS, predict_y + error))
        else:
            self.ai.target_x = TABLE_X + 3 * TABLE_WIDTH // 4
            self.ai.target_y = TABLE_Y + TABLE_HEIGHT // 2
        self.ai.move_to_target()

    def draw(self):
        screen.fill(GRAY)
        pygame.draw.rect(screen, BLACK, self.table_rect)
        pygame.draw.rect(screen, WHITE, self.inner_rect)
        pygame.draw.line(screen, BLACK,
                         (TABLE_X + TABLE_WIDTH // 2, TABLE_Y),
                         (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT),
                         self.center_line_width)
        pygame.draw.circle(screen, BLACK,
                           (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT // 2),
                           TABLE_HEIGHT // 6, self.center_line_width)
        pygame.draw.rect(screen, self.goal_color,
                         (TABLE_X - GOAL_DEPTH, TABLE_Y + TABLE_HEIGHT // 2 - GOAL_WIDTH // 2,
                          GOAL_DEPTH, GOAL_WIDTH))
        pygame.draw.rect(screen, self.goal_color,
                         (TABLE_X + TABLE_WIDTH, TABLE_Y + TABLE_HEIGHT // 2 - GOAL_WIDTH // 2,
                          GOAL_DEPTH, GOAL_WIDTH))

        player_text = self.font.render(str(self.player_score), True, BLUE)
        ai_text = self.font.render(str(self.ai_score), True, RED)
        screen.blit(player_text, (TABLE_X + TABLE_WIDTH // 4 - player_text.get_width() // 2, TABLE_Y + 10))
        screen.blit(ai_text, (TABLE_X + 3 * TABLE_WIDTH // 4 - ai_text.get_width() // 2, TABLE_Y + 10))

        exit_text = self.small_font.render("ESC - Ukončit hru", True, BLACK)
        screen.blit(exit_text, (SCREEN_WIDTH - exit_text.get_width() - 20, 20))

        self.player.draw()
        self.ai.draw()
        self.puck.draw()

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.player.target_x = max(TABLE_X + self.player.radius,
                                       min(TABLE_X + TABLE_WIDTH - self.player.radius, mouse_x))
            self.player.target_y = max(TABLE_Y + self.player.radius,
                                       min(TABLE_Y + TABLE_HEIGHT - self.player.radius, mouse_y))
            self.player.move_to_target()

            self.ai_move()
            self.puck.move()
            self.handle_collisions()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = AirHockeyGame()
    game.run()
