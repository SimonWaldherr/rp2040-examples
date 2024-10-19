import hub75
import random
import time

# Display dimensions
xHEIGHT = 32
xWIDTH = 512

# Fire simulation grid dimensions
GRID_HEIGHT = 32
GRID_WIDTH = 128

# Initialize display
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Fire simulation constants
MAX_ROUNDS = 200
NR_OF_COLS = 10

# Brighter fire pixel colors
rgbs = [
    (0, 0, 0),
    (32, 0, 0),
    (64, 0, 0),
    (128, 32, 0),
    (192, 64, 32),
    (255, 64, 0),
    (255, 160, 0),
    (255, 255, 0),
    (255, 255, 128),
    (192, 192, 255),
]

@micropython.native
class Fire:
    def __init__(self):
        # Initialize the fire pixel grid
        self._fire_pixels = [0] * (GRID_HEIGHT * GRID_WIDTH)
        self._rounds = 0
        self.set_bottom_row(NR_OF_COLS - 1)
    
    def set_bottom_row(self, col):
        # Set the bottom row of the grid to the maximum color intensity
        for i in range(GRID_WIDTH):
            index = (GRID_HEIGHT - 1) * GRID_WIDTH + i
            self._fire_pixels[index] = col
    
    def simulate(self):
        # Create a list of all indices in the grid except the bottom row
        indices = [(y, x) for y in range(1, GRID_HEIGHT) for x in range(GRID_WIDTH)]
        # Shuffle the indices using a custom shuffle function
        self.custom_shuffle(indices)
        
        # Process each pixel in random order
        for y, x in indices:
            self.spread_fire(y * GRID_WIDTH + x)
        
        # Increment the round counter
        self._rounds += 1
        
        # If the fire is going out, set the bottom row to black
        if self.is_going_out():
            self.set_bottom_row(0)
    
    def spread_fire(self, src):
        # Randomly determine the direction of the fire spread (left, right, or center)
        rand = random.randint(0, 3)
        dst = src - GRID_WIDTH + rand - 1
        
        # Ensure the destination is within bounds
        if 0 <= dst < len(self._fire_pixels):
            # Calculate the new fire intensity value
            new_value = max(0, self._fire_pixels[src] - (rand & 1))
            
            # Only update if the new value is different
            if self._fire_pixels[dst] != new_value:
                self._fire_pixels[dst] = new_value
                # Map the grid coordinates to display coordinates
                x, y = dst % GRID_WIDTH, dst // GRID_WIDTH
                r, g, b = rgbs[new_value]
                set_pixel_mapped(x, y + (GRID_WIDTH - GRID_HEIGHT), r, g, b)

    def is_going_out(self):
        # Check if the fire is close to ending
        return self._rounds >= MAX_ROUNDS - 45

    def custom_shuffle(self, lst):
        # Custom shuffle function for the list
        n = len(lst)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            lst[i], lst[j] = lst[j], lst[i]

@micropython.native
def set_pixel_mapped(x, y, r, g, b):
    # Convert the grid coordinates to physical display coordinates
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

@micropython.native
def newXY(x, y):
    yh = y % 64
    if y < 64:
        if x < 32:
            return 192 + yh, 31 - x
        elif x < 64:
            return 191 - yh, x - 32
        elif x < 96:
            return 64 + yh, 31 - (x - 64)
        elif x < 128:
            return 63 - yh, x - 96
    elif y < 128:
        if x < 32:
            return 256 + yh, 31 - x
        elif x < 64:
            return 383 - yh, x - 32
        elif x < 96:
            return 384 + yh, 31 - (x - 64)
        elif x < 128:
            return 511 - yh, x - 96
    else:
        return x, y

def main():
    fire = Fire()
    display.start()
    i = 100
    while i > 1:
        fire.simulate()
        i -= 1
    display.stop()

if __name__ == "__main__":
    main()
