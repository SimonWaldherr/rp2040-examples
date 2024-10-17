import hub75
import random
import time
import machine
from machine import Pin

# Constants for the physical display
HEIGHT = 128
WIDTH = 128

xHEIGHT = 32    # 32 rows per module
xWIDTH = 512    # 8 modules in a row with 64 columns each = 512 columns

# Initialize the display with the actual hardware resolution
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Grid size
grid_size = 128

# Optimized pixel remapping function without storing in RAM
def remap_pixel(x, y):
    x1, y1 = x, y
    if y < 64:
        if x < 32:
            x1 = 192 + y
            y1 = 31 - x
        elif x < 64:
            x1 = 191 - y
            y1 = x - 32
        elif x < 96:
            x1 = 64 + y
            y1 = 31 - (x - 64)
        elif x < 128:
            x1 = 63 - y
            y1 = x - 96
    else:
        if x < 32:
            x1 = 256 + (y - 64)
            y1 = 31 - x
        elif x < 64:
            x1 = 383 - (y - 64)
            y1 = x - 32
        elif x < 96:
            x1 = 384 + (y - 64)
            y1 = 31 - (x - 64)
        elif x < 128:
            x1 = 511 - (y - 64)
            y1 = x - 96
    return x1, y1

# Wrapper for set_pixel with optimized calculation
def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = remap_pixel(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

# Initialize grid as a bytearray (128x128 cells)
grid = bytearray(random.choice([0]*7 + [1]) for _ in range(grid_size * grid_size))

# Access functions for the grid
def get_grid_value(grid, x, y):
    return grid[y * grid_size + x]

def set_grid_value(grid, x, y, value):
    grid[y * grid_size + x] = value

# Directions (0: North, 1: East, 2: South, 3: West)
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# Initialize ants
def initialize_ants(num_ants):
    return [{'pos': [random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)],
             'dir': random.randint(0, 3)} for _ in range(num_ants)]

num_ants = 8
ants = initialize_ants(num_ants)

# Update only the affected cells of the grid
def update_game_of_life_locally(grid, x, y, changed_cells):
    live_neighbors = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % grid_size
            ny = (y + dy) % grid_size
            live_neighbors += get_grid_value(grid, nx, ny)
    
    current_state = get_grid_value(grid, x, y)
    
    # Apply Game of Life rules
    if current_state == 1 and (live_neighbors < 2 or live_neighbors > 3):
        set_grid_value(grid, x, y, 0)  # Cell dies
        changed_cells.append((x, y, 0))
    elif current_state == 0 and live_neighbors == 3:
        set_grid_value(grid, x, y, 1)  # Cell becomes alive
        changed_cells.append((x, y, 1))

# Update ants and their surroundings in the grid
def update_ants(grid, ants):
    changed_cells = []
    ant_previous_positions = []

    for ant in ants:
        x, y = ant['pos']
        current_dir = ant['dir']

        # Record the previous position to erase the ant later
        ant_previous_positions.append((x, y))

        # Langton's Ant rules
        current_state = get_grid_value(grid, x, y)
        if current_state == 0:
            if random.randint(0, 3) == 0:
                ant['dir'] = random.randint(0, 3)
            else:
                # Turn left and set cell to alive
                ant['dir'] = (current_dir - 1) % 4
            
            set_grid_value(grid, x, y, 1)
            changed_cells.append((x, y, 1))
        else:
            # Turn right and set cell to dead
            ant['dir'] = (current_dir + 1) % 4
            set_grid_value(grid, x, y, 0)
            changed_cells.append((x, y, 0))
        
        # Move the ant
        dx, dy = DIRECTIONS[ant['dir']]
        new_x = (x + dx) % grid_size
        new_y = (y + dy) % grid_size

        # Apply Game of Life rules in the 3x3 area around the new position
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                nx = (new_x + offset_x) % grid_size
                ny = (new_y + offset_y) % grid_size
                update_game_of_life_locally(grid, nx, ny, changed_cells)
        
        # Update the ant's position
        ant['pos'] = [new_x, new_y]

    return changed_cells, ant_previous_positions

# Main loop
def main():
    display.start()

    # Initial drawing of the grid
    for index in range(grid_size * grid_size):
        x = index % grid_size
        y = index // grid_size
        if grid[index]:
            set_pixel_mapped(x, y, 155, 155, 155)  # Alive = White
        else:
            set_pixel_mapped(x, y, 0, 0, 0)        # Dead = Black

    # Draw the initial positions of the ants
    for ant in ants:
        x, y = ant['pos']
        set_pixel_mapped(x, y, 255, 0, 0)  # Ants = Red

    #display.update()  # Ensure initial state is rendered

    while True:
        # Update ants and get the list of changed cells
        changed_cells, ant_prev_positions = update_ants(grid, ants)

        # Erase ants from their previous positions
        for x, y in ant_prev_positions:
            cell_state = get_grid_value(grid, x, y)
            if cell_state:
                set_pixel_mapped(x, y, 155, 155, 155)  # Alive = White
            else:
                set_pixel_mapped(x, y, 0, 0, 0)        # Dead = Black

        # Update only the changed cells on the display
        for x, y, state in changed_cells:
            if state:
                set_pixel_mapped(x, y, 155, 155, 155)  # Alive = White
            else:
                set_pixel_mapped(x, y, 0, 0, 0)        # Dead = Black

        # Draw the ants in their new positions
        for ant in ants:
            x, y = ant['pos']
            set_pixel_mapped(x, y, 255, 0, 0)  # Ants = Red

# Start the program
if __name__ == "__main__":
    main()
