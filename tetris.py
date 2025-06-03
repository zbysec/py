import pygame
import random

# Nastavení okna
WIDTH, HEIGHT = 300, 600
TILE_SIZE = 30
COLUMNS, ROWS = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE

# Barvy
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
COLORS = [(0, 255, 255), (0, 0, 255), (255, 165, 0),
          (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)]

# Tvar bloků (Tetrominoes)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 0],
     [0, 1, 1]],     # Z
    [[0, 1, 1],
     [1, 1, 0]],     # S
    [[1, 1, 1],
     [0, 1, 0]],     # T
    [[1, 1],
     [1, 1]],        # O
    [[1, 1, 1],
     [1, 0, 0]],     # L
    [[1, 1, 1],
     [0, 0, 1]]      # J
]

class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate_left(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def rotate_right(self):
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]

    def get_cells(self):
        return [(self.x + j, self.y + i)
                for i, row in enumerate(self.shape)
                for j, val in enumerate(row) if val]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def valid_space(piece, grid):
    for x, y in piece.get_cells():
        if x < 0 or x >= COLUMNS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True

def clear_rows(grid, locked):
    cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(COLUMNS):
                del locked[(j, i)]
            for y in sorted(locked, key=lambda x: x[1], reverse=True):
                x, y_ = y
                if y_ < i:
                    locked[(x, y_ + 1)] = locked.pop((x, y_))
    return cleared

def get_new_piece():
    shape = random.choice(SHAPES)
    color = random.choice(COLORS)
    return Piece(shape, color)

def draw_grid(win, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(win, grid[y][x],
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for y in range(ROWS):
        pygame.draw.line(win, GRAY, (0, y * TILE_SIZE), (WIDTH, y * TILE_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(win, GRAY, (x * TILE_SIZE, 0), (x * TILE_SIZE, HEIGHT))

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris s ovládáním myší")
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_new_piece()
    fall_time = 0
    fall_speed = 0.5

    running = True
    while running:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                for x, y in current_piece.get_cells():
                    locked_positions[(x, y)] = current_piece.color
                current_piece = get_new_piece()
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Levé tlačítko → posun doleva
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.button == 3:  # Pravé tlačítko → posun doprava
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.button == 4:  # Scroll nahoru → otočení doprava
                    current_piece.rotate_right()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate_left()
                elif event.button == 5:  # Scroll dolů → otočení doleva
                    current_piece.rotate_left()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate_right()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1

        draw_grid(win, grid)
        for x, y in current_piece.get_cells():
            if y >= 0:
                pygame.draw.rect(win, current_piece.color,
                                 (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        pygame.display.update()

        clear_rows(grid, locked_positions)

    pygame.quit()

if __name__ == "__main__":
    main()
