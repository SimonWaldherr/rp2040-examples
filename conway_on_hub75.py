import hub75
import micropython
import random

# Konstanten
HEIGHT = 64
WIDTH = 64
BORDER = 16

# Anzeige initialisieren
display = hub75.Hub75(WIDTH, HEIGHT)

@micropython.native
def initialize_grid():
    grid = bytearray(WIDTH * HEIGHT)
    for y in range(BORDER, HEIGHT - BORDER):
        for x in range(BORDER, WIDTH - BORDER):
            grid[y * WIDTH + x] = random.getrandbits(1)
    return grid

@micropython.native
def count_neighbors(grid, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not (i == 0 and j == 0):
                nx, ny = (x + i) % WIDTH, (y + j) % HEIGHT
                if grid[ny * WIDTH + nx] == 1:
                    count += 1
    return count

@micropython.native
def update_grid(grid):
    new_grid = bytearray(WIDTH * HEIGHT)
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            neighbors = count_neighbors(grid, x, y)
            idx = y * WIDTH + x
            if grid[idx] == 1 and neighbors in (2, 3):
                new_grid[idx] = 1
            elif grid[idx] == 0 and neighbors == 3:
                new_grid[idx] = 1
    return new_grid

@micropython.native
def draw_grid(grid):
    display.clear()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y * WIDTH + x] == 1:
                display.set_pixel(x, y, 255, 255, 255)

grid = initialize_grid()
display.start()

while True:
    draw_grid(grid)
    grid = update_grid(grid)

