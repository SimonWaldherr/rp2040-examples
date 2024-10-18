import hub75
import random
import time
from machine import Pin

# Display dimensions
xHEIGHT = 32
xWIDTH = 512

# Initialize display
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Constants for Tic Tac Toe
VOID = 0
GRID = 1
CIRCLE = 2
CIRCLE_WIN = 12
CROSS = 3
CROSS_WIN = 13

# Game states
STATE_PLAYING = 1
STATE_WINNER = 2
STATE_OVER = 3

DIM = 3  # 3x3 Tic Tac Toe

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

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
        return x, y  # Identity transformation for values >= 128

def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

class TicTacToe:
    def __init__(self):
        self.rounds_to_play = 42  # Total number of moves (adjust as needed)
        self.state = STATE_PLAYING
        self.play_smart = random.choice([True, False])
        self.player_one = random.choice([True, False])
        self.copy_world = [[VOID for _ in range(DIM)] for _ in range(DIM)]
        self.world = [[VOID for _ in range(128)] for _ in range(128)]
        self.changes = []  # List to track changed pixels
        self.cell_size = 40  # Size of each Tic Tac Toe cell in pixels
        self.reset()
    
    def reset(self):
        self.state = STATE_PLAYING
        self.play_smart = random.choice([True, False])
        self.player_one = random.choice([True, False])
        self.changes = []
        
        for i in range(DIM):
            for j in range(DIM):
                self.copy_world[i][j] = VOID
        
        # Initialize grid lines
        for i in range(128):
            for j in range(128):
                if (i == self.cell_size or i == 2 * self.cell_size) or (j == self.cell_size or j == 2 * self.cell_size):
                    if self.world[i][j] != GRID:
                        self.world[i][j] = GRID
                        self.changes.append((i, j, GRID))
                else:
                    if self.world[i][j] != VOID:
                        self.world[i][j] = VOID
                        self.changes.append((i, j, VOID))
    
    def get_next_pos(self, what):
        candidates = [Point(x, y) for y in range(DIM) for x in range(DIM) if self.copy_world[x][y] == VOID]
        
        if not candidates:
            return None  # No available moves
        
        if self.play_smart:
            high_score = -1
            best_candidate = candidates[0]
            for c in candidates:
                score = 0
                # Evaluate rows, columns, and diagonals
                score += self.evaluate_line(what, self.prepare_line(0, c.y, 1, c.y, 2, c.y))
                score += self.evaluate_line(what, self.prepare_line(c.x, 0, c.x, 1, c.x, 2))
                if c.x == c.y:
                    score += self.evaluate_line(what, self.prepare_line(0, 0, 1, 1, 2, 2))
                if c.x + c.y == 2:
                    score += self.evaluate_line(what, self.prepare_line(2, 0, 1, 1, 0, 2))
                if score > high_score:
                    high_score = score
                    best_candidate = c
            return best_candidate
        return random.choice(candidates)
    
    def prepare_line(self, x1, y1, x2, y2, x3, y3):
        return [Point(x1, y1), Point(x2, y2), Point(x3, y3)]
    
    def evaluate_line(self, what, line):
        score = 1
        x_count = sum(1 for p in line if self.copy_world[p.x][p.y] == CROSS)
        o_count = sum(1 for p in line if self.copy_world[p.x][p.y] == CIRCLE)
        if (what == CROSS and x_count == 2) or (what == CIRCLE and o_count == 2):
            score += 2
        return score
    
    def simulate(self):
        if self.state == STATE_PLAYING:
            self.check_if_over()
        
        if self.state == STATE_OVER:
            self.reset()
            self.rounds_to_play -= 1
            if self.rounds_to_play == 0:
                return  # Game over
        elif self.state == STATE_WINNER:
            self.state = STATE_OVER
        else:
            what = CIRCLE if self.player_one else CROSS
            pos = self.get_next_pos(what)
            if pos:
                self.draw(pos.x, pos.y, what)
                self.copy_world[pos.x][pos.y] = what
                self.player_one = not self.player_one
    
    def draw(self, col, row, what):
        start_x = col * self.cell_size
        start_y = row * self.cell_size
        padding = 5  # Padding inside each cell
        
        if what in (CIRCLE, CIRCLE_WIN):
            # Draw unfilled circle
            radius = self.cell_size // 2 - padding
            thickness = 1  # Thickness of the circle border
            for i in range(padding, self.cell_size - padding):
                for j in range(padding, self.cell_size - padding):
                    dx = i - self.cell_size // 2
                    dy = j - self.cell_size // 2
                    dist_sq = dx * dx + dy * dy
                    if (radius - thickness) ** 2 < dist_sq <= radius ** 2:
                        x = start_x + i
                        y = start_y + j
                        if self.world[x][y] != what:
                            self.world[x][y] = what
                            self.changes.append((x, y, what))
        else:
            # Draw cross
            for i in range(padding, self.cell_size - padding):
                x1 = start_x + i
                y1 = start_y + i
                y2 = start_y + (self.cell_size - i - 1)
                if self.world[x1][y1] != what:
                    self.world[x1][y1] = what
                    self.changes.append((x1, y1, what))
                if self.world[x1][y2] != what:
                    self.world[x1][y2] = what
                    self.changes.append((x1, y2, what))
    
    def map_color(self, x, y):
        value = self.world[x][y]
        if value == GRID:
            return (255, 255, 255)  # White
        elif value == CIRCLE:
            return (0, 255, 0) if self.play_smart else (0, 255, 255)  # Green or Cyan
        elif value == CROSS:
            return (0, 0, 255) if self.play_smart else (255, 0, 170)  # Blue or Magenta
        elif value in (CIRCLE_WIN, CROSS_WIN):
            return (255, 255, 0)  # Yellow
        else:
            return (0, 0, 0)  # Black
    
    def check_if_over(self):
        # Define all winning lines
        winning_lines = [
            self.prepare_line(0, 0, 1, 1, 2, 2),
            self.prepare_line(2, 0, 1, 1, 0, 2)
        ]
        for i in range(DIM):
            winning_lines.append(self.prepare_line(i, 0, i, 1, i, 2))  # Rows
            winning_lines.append(self.prepare_line(0, i, 1, i, 2, i))  # Columns
        
        for line in winning_lines:
            x_count = sum(1 for p in line if self.copy_world[p.x][p.y] == CROSS)
            o_count = sum(1 for p in line if self.copy_world[p.x][p.y] == CIRCLE)
            if x_count == 3 or o_count == 3:
                self.state = STATE_WINNER
                win_value = CROSS_WIN if x_count == 3 else CIRCLE_WIN
                for p in line:
                    self.draw(p.x, p.y, win_value)
                return
        
        if all(cell != VOID for row in self.copy_world for cell in row):
            self.state = STATE_OVER

def render_tic_tac_toe(tic_tac_toe):
    for x, y, value in tic_tac_toe.changes:
        r, g, b = tic_tac_toe.map_color(x, y)
        set_pixel_mapped(x, y, r, g, b)
    tic_tac_toe.changes = []

def main():
    tic_tac_toe = TicTacToe()
    display.start()
    
    while tic_tac_toe.rounds_to_play > 0:
        tic_tac_toe.simulate()
        render_tic_tac_toe(tic_tac_toe)
        time.sleep(0.05)
    
    display.stop()

if __name__ == "__main__":
    main()
