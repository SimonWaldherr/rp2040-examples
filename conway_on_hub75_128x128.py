import hub75
import micropython
import random
import time

# Konstanten
HEIGHT = 128
WIDTH = 128
BORDER = 48  # Grenzen für lebende Zellen

# Anzeige initialisieren
xHEIGHT = HEIGHT // 4    # 32 Zeilen pro Modul
xWIDTH = WIDTH * 4       # 512 Spalten (4x128)
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Funktion für das X/Y-Remapping
@micropython.native
def newXY(x, y):
    x1 = x
    y1 = y
    if y < 64:
        yh = y
        if x < 32:
            xh = x
            x1 = 192 + yh
            y1 = 31 - xh
        elif x < 64:
            xh = x - 32
            x1 = 191 - yh
            y1 = xh
        elif x < 96:
            xh = x - 64
            x1 = 64 + yh
            y1 = 31 - xh
        elif x < 128:
            xh = x - 96
            x1 = 63 - yh
            y1 = xh
    elif y < 128:
        yh = y - 64
        if x < 32:
            xh = x
            x1 = 256 + yh
            y1 = 31 - xh
        elif x < 64:
            xh = x - 32
            x1 = 383 - yh
            y1 = xh
        elif x < 96:
            xh = x - 64
            x1 = 384 + yh
            y1 = 31 - xh
        elif x < 128:
            xh = x - 96
            x1 = 511 - yh
            y1 = xh
    return x1, y1

# Funktion zum Setzen eines Pixels mit Remapping
@micropython.native
def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

@micropython.native
def initialize_live_cells():
    live_cells = []
    for _ in range((HEIGHT-2*BORDER) * (WIDTH-2*BORDER) // 10):  # Initialisiere etwa 10% lebende Zellen
        x = random.randint(BORDER, WIDTH - BORDER - 1)
        y = random.randint(BORDER, HEIGHT - BORDER - 1)
        live_cells.append((x, y))
    return live_cells

@micropython.native
def count_neighbors(live_cells, x, y):
    count = 0
    for j in range(-1, 2):
        ny = (y + j) % HEIGHT
        for i in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx = (x + i) % WIDTH
            if (nx, ny) in live_cells:
                count += 1
    return count

@micropython.native
def update_live_cells(live_cells):
    new_live_cells = []
    cells_to_check = set()

    # Alle lebenden Zellen und ihre Nachbarn müssen überprüft werden
    for (x, y) in live_cells:
        cells_to_check.add((x, y))
        for j in range(-1, 2):
            for i in range(-1, 2):
                nx = (x + i) % WIDTH
                ny = (y + j) % HEIGHT
                cells_to_check.add((nx, ny))

    for (x, y) in cells_to_check:
        neighbors = count_neighbors(live_cells, x, y)
        if (x, y) in live_cells:
            if neighbors in (2, 3):
                new_live_cells.append((x, y))
        else:
            if neighbors == 3:
                new_live_cells.append((x, y))

    return new_live_cells

@micropython.native
def draw_changes(old_live, new_live):
    # Setze Zellen auf das neue Raster
    all_cells = set(old_live) | set(new_live)
    
    for (x, y) in all_cells:
        if (x, y) in new_live:
            set_pixel_mapped(x, y, 255, 255, 255)  # Lebende Zelle
        else:
            set_pixel_mapped(x, y, 0, 0, 0)        # Tote Zelle

def main():
    display.start()
    live_cells = initialize_live_cells()
    
    while True:
        draw_changes(live_cells, live_cells)  # Zeichne den aktuellen Zustand
        new_live = update_live_cells(live_cells)
        draw_changes(live_cells, new_live)  # Zeichne die neuen Änderungen
        live_cells = new_live

if __name__ == "__main__":
    main()
