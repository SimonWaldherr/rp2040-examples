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

def hsb_to_rgb(hue, saturation, brightness):
    hue_normalized = (hue % 360) / 60
    hue_index = int(hue_normalized)
    hue_fraction = hue_normalized - hue_index

    value1 = brightness * (1 - saturation)
    value2 = brightness * (1 - saturation * hue_fraction)
    value3 = brightness * (1 - saturation * (1 - hue_fraction))

    red, green, blue = [
        (brightness, value3, value1),
        (value2, brightness, value1),
        (value1, brightness, value3),
        (value1, value2, brightness),
        (value3, value1, brightness),
        (brightness, value1, value2)
    ][hue_index]

    return int(red * 255), int(green * 255), int(blue * 255)

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

# Initialize ants with unique colors
def initialize_ants(num_ants):
    ants = []
    for _ in range(num_ants):
        ant = {
            'pos': [random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)],
            'dir': random.randint(0, 3),
            'color': hsb_to_rgb(random.randint(0, 360), 1, 1)  # Bright random color
        }
        ants.append(ant)
    return ants

num_ants = 8
ants = initialize_ants(num_ants)

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
            changed_cells.append((x, y, 1, ant['color']))
        else:
            # Turn right and set cell to dead
            ant['dir'] = (current_dir + 1) % 4
            set_grid_value(grid, x, y, 0)
            changed_cells.append((x, y, 0, (0, 0, 0)))
        
        # Move the ant
        dx, dy = DIRECTIONS[ant['dir']]
        new_x = (x + dx) % grid_size
        new_y = (y + dy) % grid_size

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
        r, g, b = ant['color']
        set_pixel_mapped(x, y, r, g, b)

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
        for x, y, state, color in changed_cells:
            if state:
                # Slightly dimmer color for cells the ant has passed over
                r, g, b = [int(c * 0.5) for c in color]
                set_pixel_mapped(x, y, r, g, b)
            else:
                set_pixel_mapped(x, y, 0, 0, 0)        # Dead = Black

        # Draw the ants in their new positions
        for ant in ants:
            x, y = ant['pos']
            r, g, b = ant['color']
            set_pixel_mapped(x, y, r, g, b)

# Start the program
if __name__ == "__main__":
    main()
