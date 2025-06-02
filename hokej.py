import pygame
import sys
import random
import math

pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Fullscreen window and get correct screen size
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Air Hockey")

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (200, 200, 255)
LIGHT_RED = (255, 200, 200)

# Game constants
TABLE_ASPECT_RATIO = 2.0  # width : height
FPS = 60
FRICTION = 0.98
AI_DIFFICULTY = 0.7  # 0-1 (easy-hard)
MAX_SCORE = 7  # Score needed to win

# Calculate table size (without margins)
table_height = SCREEN_HEIGHT * 0.9  # Use 90% of screen height
table_width = int(table_height * TABLE_ASPECT_RATIO)

# Adjust if exceeds screen width
if table_width > SCREEN_WIDTH * 0.9:
    table_width = int(SCREEN_WIDTH * 0.9)
    table_height = int(table_width / TABLE_ASPECT_RATIO)

TABLE_WIDTH = table_width
TABLE_HEIGHT = table_height

# Table position (centered)
TABLE_X = (SCREEN_WIDTH - TABLE_WIDTH) // 2
TABLE_Y = (SCREEN_HEIGHT - TABLE_HEIGHT) // 2

# Game elements
PUCK_RADIUS = max(10, TABLE_HEIGHT // 30)
PADDLE_RADIUS = max(15, TABLE_HEIGHT // 25)
GOAL_WIDTH = TABLE_HEIGHT // 3
GOAL_DEPTH = TABLE_WIDTH // 20
PUCK_SPEED_LIMIT = TABLE_WIDTH // 40
PADDLE_SPEED = TABLE_WIDTH // 200

# Load sounds
try:
    HIT_SOUND = pygame.mixer.Sound("hit.wav")
    GOAL_SOUND = pygame.mixer.Sound("goal.wav")
    WIN_SOUND = pygame.mixer.Sound("win.wav")
except:
    # Create dummy sound objects if files not found
    class DummySound:
        def play(self): pass
    HIT_SOUND = GOAL_SOUND = WIN_SOUND = DummySound()

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
        self.highlight = False
        self.highlight_time = 0

    def draw(self):
        # Draw outer circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw inner circle with highlight effect if needed
        inner_color = WHITE
        if self.highlight:
            # Create a pulsing effect when highlighted
            pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
            if self.color == BLUE:
                inner_color = (255, 255, 255 - int(100 * pulse))
            else:
                inner_color = (255, 255 - int(100 * pulse), 255 - int(100 * pulse))
        
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), self.radius - 5)
        
        # Draw center dot
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius // 3)

    def move_to_target(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)
        if distance > 5:
            move_speed = min(distance, self.speed)
            self.x += dx / distance * move_speed
            self.y += dy / distance * move_speed

    def set_highlight(self, duration=500):
        self.highlight = True
        self.highlight_time = pygame.time.get_ticks() + duration

    def update_highlight(self):
        if self.highlight and pygame.time.get_ticks() > self.highlight_time:
            self.highlight = False

class Puck:
    def __init__(self):
        self.reset()
        self.radius = PUCK_RADIUS
        self.trail = []  # For storing previous positions
        self.max_trail = 10  # Number of trail segments

    def reset(self):
        self.x = TABLE_X + TABLE_WIDTH // 2
        self.y = TABLE_Y + TABLE_HEIGHT // 2
        angle = random.uniform(0, 2 * math.pi)
        speed = PUCK_SPEED_LIMIT * 0.6
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.trail = []  # Clear trail on reset

    def move(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        self.x += self.dx
        self.y += self.dy
        self.dx *= FRICTION
        self.dy *= FRICTION
        
        # Limit speed
        speed = math.hypot(self.dx, self.dy)
        if speed > PUCK_SPEED_LIMIT:
            scale = PUCK_SPEED_LIMIT / speed
            self.dx *= scale
            self.dy *= scale

    def draw(self):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            radius = int(self.radius * (0.3 + 0.7 * (i / len(self.trail))))
            trail_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (255, 100, 100, alpha), (radius, radius), radius)
            screen.blit(trail_surface, (tx - radius, ty - radius))
        
        # Draw puck
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 5)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius // 3)

class AirHockeyGame:
    def __init__(self):
        self.player = Paddle(TABLE_X + TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, BLUE)
        self.ai = Paddle(TABLE_X + 3 * TABLE_WIDTH // 4, TABLE_Y + TABLE_HEIGHT // 2, RED, is_ai=True)
        self.puck = Puck()
        self.player_score = 0
        self.ai_score = 0
        self.game_state = "playing"  # "playing", "game_over"
        self.winner = None
        self.font = pygame.font.SysFont('Arial', TABLE_HEIGHT // 10, bold=True)
        self.small_font = pygame.font.SysFont('Arial', TABLE_HEIGHT // 20)
        self.center_line_width = max(2, TABLE_WIDTH // 300)
        self.border_width = max(5, TABLE_HEIGHT // 50)
        self.goal_color = (100, 100, 100)
        self.table_rect = pygame.Rect(TABLE_X, TABLE_Y, TABLE_WIDTH, TABLE_HEIGHT)
        self.inner_rect = pygame.Rect(TABLE_X + self.border_width, TABLE_Y + self.border_width,
                                    TABLE_WIDTH - 2 * self.border_width, TABLE_HEIGHT - 2 * self.border_width)
        self.last_collision_time = 0
        self.countdown = 0  # Countdown timer after goal
        self.goal_scored = False

    def handle_collisions(self):
        current_time = pygame.time.get_ticks()
        
        for paddle in [self.player, self.ai]:
            distance = math.hypot(self.puck.x - paddle.x, self.puck.y - paddle.y)
            if distance < self.puck.radius + paddle.radius:
                # Only play sound if enough time has passed since last collision
                if current_time - self.last_collision_time > 100:
                    HIT_SOUND.play()
                    self.last_collision_time = current_time
                    paddle.set_highlight()
                
                angle = math.atan2(self.puck.y - paddle.y, self.puck.x - paddle.x)
                force = PUCK_SPEED_LIMIT * 0.8
                
                # AI gets better aim at higher difficulty
                if paddle.is_ai:
                    target_angle = math.atan2(TABLE_Y + TABLE_HEIGHT // 2 - paddle.y, TABLE_X - paddle.x)
                    angle = angle * (1 - AI_DIFFICULTY * 0.3) + target_angle * (AI_DIFFICULTY * 0.3)
                
                self.puck.dx = math.cos(angle) * force
                self.puck.dy = math.sin(angle) * force
                
                # Push puck out of paddle to prevent sticking
                overlap = (self.puck.radius + paddle.radius) - distance
                self.puck.x += math.cos(angle) * overlap * 0.5
                self.puck.y += math.sin(angle) * overlap * 0.5

        # Wall collisions
        if self.puck.y - self.puck.radius <= self.inner_rect.top:
            self.puck.y = self.inner_rect.top + self.puck.radius
            self.puck.dy *= -0.9
        if self.puck.y + self.puck.radius >= self.inner_rect.bottom:
            self.puck.y = self.inner_rect.bottom - self.puck.radius
            self.puck.dy *= -0.9

        # Left goal check
        if self.puck.x - self.puck.radius <= self.table_rect.left:
            if self.inner_rect.centery - GOAL_WIDTH // 2 < self.puck.y < self.inner_rect.centery + GOAL_WIDTH // 2:
                self.ai_score += 1
                self.goal_scored = True
                GOAL_SOUND.play()
                self.countdown = pygame.time.get_ticks() + 1000  # 1 second delay
            else:
                self.puck.x = self.table_rect.left + self.puck.radius
                self.puck.dx *= -0.8

        # Right goal check
        if self.puck.x + self.puck.radius >= self.table_rect.right:
            if self.inner_rect.centery - GOAL_WIDTH // 2 < self.puck.y < self.inner_rect.centery + GOAL_WIDTH // 2:
                self.player_score += 1
                self.goal_scored = True
                GOAL_SOUND.play()
                self.countdown = pygame.time.get_ticks() + 1000  # 1 second delay
            else:
                self.puck.x = self.table_rect.right - self.puck.radius
                self.puck.dx *= -0.8

        # Check for winner
        if self.player_score >= MAX_SCORE or self.ai_score >= MAX_SCORE:
            self.game_state = "game_over"
            self.winner = "player" if self.player_score > self.ai_score else "ai"
            WIN_SOUND.play()

    def ai_move(self):
        if self.puck.dx > 0:  # Only move when puck is coming toward AI
            # Predict puck position with some randomness based on difficulty
            predict_frames = 10 + int(10 * (1 - AI_DIFFICULTY))
            predict_x = self.puck.x + self.puck.dx * predict_frames
            predict_y = self.puck.y + self.puck.dy * predict_frames
            
            # Add some error based on difficulty
            error_x = (1 - AI_DIFFICULTY) * random.uniform(-TABLE_WIDTH/4, TABLE_WIDTH/4)
            error_y = (1 - AI_DIFFICULTY) * random.uniform(-TABLE_HEIGHT/4, TABLE_HEIGHT/4)
            
            self.ai.target_x = max(TABLE_X + TABLE_WIDTH // 2,
                                min(TABLE_X + TABLE_WIDTH - PADDLE_RADIUS, predict_x + error_x))
            self.ai.target_y = max(TABLE_Y + PADDLE_RADIUS,
                                min(TABLE_Y + TABLE_HEIGHT - PADDLE_RADIUS, predict_y + error_y))
        else:
            # Return to defensive position
            self.ai.target_x = TABLE_X + 3 * TABLE_WIDTH // 4
            self.ai.target_y = TABLE_Y + TABLE_HEIGHT // 2
            
        self.ai.move_to_target()

    def draw(self):
        # Draw background
        screen.fill(GRAY)
        
        # Draw table
        pygame.draw.rect(screen, BLACK, self.table_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.inner_rect, border_radius=5)
        
        # Draw center line and circle
        pygame.draw.line(screen, BLACK,
                       (TABLE_X + TABLE_WIDTH // 2, TABLE_Y),
                       (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT),
                       self.center_line_width)
        pygame.draw.circle(screen, BLACK,
                          (TABLE_X + TABLE_WIDTH // 2, TABLE_Y + TABLE_HEIGHT // 2),
                          TABLE_HEIGHT // 6, self.center_line_width)
        
        # Draw goals
        pygame.draw.rect(screen, self.goal_color,
                       (TABLE_X - GOAL_DEPTH, TABLE_Y + TABLE_HEIGHT // 2 - GOAL_WIDTH // 2,
                        GOAL_DEPTH, GOAL_WIDTH), border_radius=5)
        pygame.draw.rect(screen, self.goal_color,
                       (TABLE_X + TABLE_WIDTH, TABLE_Y + TABLE_HEIGHT // 2 - GOAL_WIDTH // 2,
                        GOAL_DEPTH, GOAL_WIDTH), border_radius=5)
        
        # Draw scores with colored backgrounds
        player_score_bg = pygame.Surface((TABLE_WIDTH//6, TABLE_HEIGHT//10), pygame.SRCALPHA)
        player_score_bg.fill((*BLUE, 150))
        screen.blit(player_score_bg, (TABLE_X + TABLE_WIDTH//4 - TABLE_WIDTH//12, TABLE_Y + 10))
        
        ai_score_bg = pygame.Surface((TABLE_WIDTH//6, TABLE_HEIGHT//10), pygame.SRCALPHA)
        ai_score_bg.fill((*RED, 150))
        screen.blit(ai_score_bg, (TABLE_X + 3*TABLE_WIDTH//4 - TABLE_WIDTH//12, TABLE_Y + 10))
        
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (TABLE_X + TABLE_WIDTH // 4 - player_text.get_width() // 2, TABLE_Y + 10))
        screen.blit(ai_text, (TABLE_X + 3 * TABLE_WIDTH // 4 - ai_text.get_width() // 2, TABLE_Y + 10))
        
        # Draw controls info
        exit_text = self.small_font.render("ESC - Quit", True, BLACK)
        screen.blit(exit_text, (SCREEN_WIDTH - exit_text.get_width() - 20, 20))
        
        # Draw game elements
        self.player.draw()
        self.ai.draw()
        self.puck.draw()
        
        # Update paddle highlights
        self.player.update_highlight()
        self.ai.update_highlight()
        
        # Draw countdown after goal
        if self.goal_scored and pygame.time.get_ticks() < self.countdown:
            time_left = (self.countdown - pygame.time.get_ticks()) / 1000
            countdown_text = self.font.render(str(int(time_left + 1)), True, BLACK)
            screen.blit(countdown_text, (SCREEN_WIDTH//2 - countdown_text.get_width()//2, 
                                      SCREEN_HEIGHT//2 - countdown_text.get_height()//2))
        
        # Draw game over screen
        if self.game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            winner_text = self.font.render(f"{'Player' if self.winner == 'player' else 'AI'} Wins!", True, 
                                        BLUE if self.winner == "player" else RED)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
            
            screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 
                                   SCREEN_HEIGHT//2 - winner_text.get_height()))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                                     SCREEN_HEIGHT//2 + 50))

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.game_state = "playing"
        self.winner = None
        self.player.x = TABLE_X + TABLE_WIDTH // 4
        self.player.y = TABLE_Y + TABLE_HEIGHT // 2
        self.ai.x = TABLE_X + 3 * TABLE_WIDTH // 4
        self.ai.y = TABLE_Y + TABLE_HEIGHT // 2
        self.puck.reset()
        self.goal_scored = False

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
                    elif event.key == pygame.K_r and self.game_state == "game_over":
                        self.reset_game()
            
            if self.game_state == "playing":
                # Handle mouse input for player paddle
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.player.target_x = max(TABLE_X + self.player.radius,
                                         min(TABLE_X + TABLE_WIDTH - self.player.radius, mouse_x))
                self.player.target_y = max(TABLE_Y + self.player.radius,
                                         min(TABLE_Y + TABLE_HEIGHT - self.player.radius, mouse_y))
                self.player.move_to_target()

                # AI movement
                self.ai_move()
                
                # Puck movement (only if not in goal celebration)
                if not self.goal_scored or pygame.time.get_ticks() >= self.countdown:
                    self.puck.move()
                    self.handle_collisions()
                    if self.goal_scored and pygame.time.get_ticks() >= self.countdown:
                        self.puck.reset()
                        self.goal_scored = False
            
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    game = AirHockeyGame()
    game.run()