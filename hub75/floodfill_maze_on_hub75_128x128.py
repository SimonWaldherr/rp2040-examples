import hub75
import micropython
import random
import time
import gc

# Konstanten
HEIGHT = 128
WIDTH = 128
BORDER = 48  # Grenzen für lebende Zellen

# Farben für mehr Abwechslung
COLOR_PALETTE = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

# Anzeige initialisieren
xHEIGHT = HEIGHT // 4    # 32 Zeilen pro Modul
xWIDTH = WIDTH * 4       # 512 Spalten (4x128)
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Funktion für das X/Y-Remapping
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
        return x, y  # Identity transformation for values >= 128


# Funktion zum Setzen eines Pixels mit Remapping
@micropython.native
def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

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
    
MazeWaySize = 8
    
def draw_maze_on_grid():
    # Labyrinth-Generierungsfunktion mit Depth-First Search (Recursive Backtracker)
    stack = []
    visited = set()

    # Startpunkt in der Mitte
    start_x = random.randint(BORDER // 2, WIDTH - BORDER // 2)
    start_y = random.randint(BORDER // 2, HEIGHT - BORDER // 2)

    stack.append((start_x, start_y))
    visited.add((start_x, start_y))

    # Bewegungen (rechts, links, oben, unten) um 4 Zellen für breite Korridore
    directions = [(0, MazeWaySize), (0, -MazeWaySize), (MazeWaySize, 0), (-MazeWaySize, 0)]

    while stack:
        x, y = stack[-1]

        # Mischen der Richtungen
        mixed_directions = directions[:]  # Kopie der Richtungen
        for i in range(len(mixed_directions) - 1, 0, -1):
            j = random.randint(0, i)
            mixed_directions[i], mixed_directions[j] = mixed_directions[j], mixed_directions[i]

        found_unvisited_neighbor = False

        for dx, dy in mixed_directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < WIDTH and 0 < ny < HEIGHT and (nx, ny) not in visited:
                # Füge Verbindung zwischen den Zellen (Mauer entfernen) und breite den Weg aus
                for i in range(1, MazeWaySize):  # Zellen dazwischen freiräumen, um 3-Zellen breite Gänge zu schaffen
                    set_grid_value(x + (dx // MazeWaySize) * i, y + (dy // MazeWaySize) * i, 1)
                    set_pixel_mapped(x + (dx // MazeWaySize) * i, y + (dy // MazeWaySize) * i, 255, 255, 255)

                # Füge die neue Zelle zum Stack hinzu und markiere sie als besucht
                stack.append((nx, ny))
                visited.add((nx, ny))

                # Zeichne den aktuellen Pfad (Endpunkt des Sprungs)
                set_grid_value(nx, ny, 5)
                set_pixel_mapped(nx, ny, 255, 255, 255)

                found_unvisited_neighbor = True
                break

        if not found_unvisited_neighbor:
            # Rückwärts, wenn keine unbesuchten Nachbarn vorhanden sind
            stack.pop()

    # Wähle zufällig einen Gegner in einer leeren Zelle
    while True:
        enemy_x = random.randint(BORDER, WIDTH - BORDER - 1)
        enemy_y = random.randint(BORDER, HEIGHT - BORDER - 1)
        if get_grid_value(enemy_x, enemy_y) == 0:
            break

    return enemy_x, enemy_y


@micropython.native
def floodfill(x, y, r, g, b, max_steps=16000):
    stack = [(x, y)]
    steps = 0
    hue_start = 0  # Startwert für den Farbverlauf
    hue_end = 360  # Endwert für den Farbverlauf

    while stack and steps < max_steps:
        x, y = stack.pop(0)
        grid_value = get_grid_value(x, y)

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue
        if grid_value != 0 and grid_value != 3:
            continue

        set_grid_value(x, y, 2)

        if grid_value != 3:
            # Berechne den Farbverlauf basierend auf der Anzahl der Schritte
            hue = hue_start + (hue_end - hue_start) * (steps / max_steps)
            rgb_color = hsb_to_rgb(hue, 1.0, 1.0)  # Volle Sättigung und Helligkeit
            set_pixel_mapped(x, y, *rgb_color)

        steps += 1

        # Nachbarpixel zur Liste hinzufügen
        if x + 1 < WIDTH:
            stack.append((x + 1, y))
        if x - 1 >= 0:
            stack.append((x - 1, y))
        if y + 1 < HEIGHT:
            stack.append((x, y + 1))
        if y - 1 >= 0:
            stack.append((x, y - 1))

    return len(stack) > 0  # Gibt zurück, ob noch Arbeit übrig ist


display.start()

while True:
    display.clear()
    initialize_grid()
    
    enemy_x, enemy_y = draw_maze_on_grid()
    
    set_grid_value(enemy_x, enemy_y, 3)

    # Speicherbereinigung und Stats ausgeben
    gc.collect()
    print("Memory before floodfill:", gc.mem_free())
    
    floodfill(enemy_x, enemy_y, 140, 100, 5)

    gc.collect()
    print("Memory after floodfill:", gc.mem_free())

    time.sleep(1)
    display.clear()

