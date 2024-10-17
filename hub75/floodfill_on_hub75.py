import hub75
import micropython
import random
import time
import gc

# Constants
HEIGHT = 64
WIDTH = 64
BORDER = 0

# Initialize the display
display = hub75.Hub75(WIDTH, HEIGHT)

# Global variable for the grid
grid = bytearray(WIDTH * HEIGHT)

# grid values:
# 0 = empty
# 1 = line
# 2 = floodfill
# 3 = enemy


def initialize_grid():
    global grid
    grid = bytearray(WIDTH * HEIGHT)

def get_grid_value(x, y):
    return grid[y * WIDTH + x]

def set_grid_value(x, y, value):
    grid[y * WIDTH + x] = value

def draw_line_on_grid():
    startpoint_x = random.randint(BORDER+1, WIDTH - BORDER - 1)
    startpoint_y = 0

    down_for = random.randint(1, HEIGHT - 15)
    for i in range(down_for):
        set_grid_value(startpoint_x, startpoint_y + i, 1)
        display.set_pixel(startpoint_x, startpoint_y + i, 255, 255, 255)

    left_for = random.randint(1, startpoint_x - BORDER)
    for i in range(left_for):
        set_grid_value(startpoint_x - i, startpoint_y + down_for, 1)
        display.set_pixel(startpoint_x - i, startpoint_y + down_for, 255, 255, 255)

    # Draw line down to bottom
    down_for_2 = HEIGHT - (startpoint_y + down_for)
    for i in range(down_for_2):
        set_grid_value(startpoint_x - left_for, startpoint_y + down_for + i, 1)
        display.set_pixel(startpoint_x - left_for, startpoint_y + down_for + i, 255, 255, 255)

    # Define random point x/y for enemy and check if it is on the line
    for _ in range(10):
        enemy_x = random.randint(BORDER, WIDTH - BORDER - 1)
        enemy_y = random.randint(BORDER, HEIGHT - BORDER - 1)
        if get_grid_value(enemy_x, enemy_y) == 1:
            continue
        else:
            break

    display.set_pixel(enemy_x, enemy_y, 255, 0, 0)
    return enemy_x, enemy_y

@micropython.native
def floodfill(x, y, r, g, b, max_steps=8000):
    stack = [(x, y)]
    steps = 0

    while stack and steps < max_steps:
        x, y = stack.pop(0)
        grid_value = get_grid_value(x, y)
        
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue
        if grid_value != 0 and grid_value != 3:
            continue

        set_grid_value(x, y, 2)

        if grid_value != 3:
            display.set_pixel(x, y, r, g, b)

        steps += 1

        # Add neighboring pixels to the stack
        if x + 1 < WIDTH:
            stack.append((x + 1, y))
        if x - 1 >= 0:
            stack.append((x - 1, y))
        if y + 1 < HEIGHT:
            stack.append((x, y + 1))
        if y - 1 >= 0:
            stack.append((x, y - 1))

    return len(stack) > 0  # Indicates if there's still work left

display.start()

while True:
    display.clear()
    initialize_grid()
    enemy_x, enemy_y = draw_line_on_grid()
    set_grid_value(enemy_x, enemy_y, 3)

    # Collect garbage and print memory stats before and after floodfill
    gc.collect()
    print("Memory before floodfill:", gc.mem_free())
    
    floodfill(enemy_x, enemy_y, 140, 100, 5)

    gc.collect()
    print("Memory after floodfill:", gc.mem_free())

    time.sleep(1)
    display.clear()

