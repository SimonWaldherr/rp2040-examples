import hub75
import random
import time
import machine
from machine import Pin

# Constants for the physical display
HEIGHT = 128
WIDTH = 128

xHEIGHT = 32    # 32 Zeilen pro Modul
xWIDTH = 512    # 8 Module in Reihe à 64 Spalten = 512 Spalten

# Initialize the display with real hardware resolution
display = hub75.Hub75(xWIDTH, xHEIGHT)

# Zeichen-Dictionary für die Anzeige von Text
char_dict = {
    '0': ["01110", "10001", "10001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "01110"],
    '2': ["11110", "00001", "01110", "10000", "11111"],
    '3': ["11110", "00001", "00110", "00001", "11110"],
    '4': ["10000", "10010", "10010", "11111", "00010"],
    '5': ["11111", "10000", "11110", "00001", "11110"],
    '6': ["01110", "10000", "11110", "10001", "01110"],
    '7': ["11111", "00010", "00100", "01000", "10000"],
    '8': ["01110", "10001", "01110", "10001", "01110"],
    '9': ["01110", "10001", "01111", "00001", "01110"],
    ' ': ["00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00001"],
    ':': ["00000", "00100", "00000", "00100", "00000"]
}

# Pixel Remapping
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

# Wrapper für set_pixel mit Remapping
def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

# Funktion zum Zeichnen eines Rechtecks
def rect(x1, y1, x2, y2, r, g, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            set_pixel_mapped(x, y, r, g, b)

# Funktion zum Zeichnen eines einzelnen Zeichens
def draw_char(x, y, char, r, g, b):
    if char in char_dict:
        matrix = char_dict[char]
        for row in range(5):
            for col in range(5):
                if matrix[row][col] == '1':
                    set_pixel_mapped(x + col, y + row, r, g, b)

# Funktion zum Zeichnen von Text
def draw_text(x, y, text, r, g, b):
    offset_x = x
    for char in text:
        draw_char(offset_x, y, char, r, g, b)
        offset_x += 6  # Abstand zwischen den Zeichen

# Funktion zur Umwandlung von HSB (Farbton, Sättigung, Helligkeit) zu RGB
def hsb_to_rgb(hue, saturation, brightness):
    hue_normalized = (hue % 360) / 60
    hue_index = int(hue_normalized)
    hue_fraction = hue_normalized - hue_index

    value1 = brightness * (1 - saturation)
    value2 = brightness * (1 - saturation * hue_fraction)
    value3 = brightness * (1 - saturation * (1 - hue_fraction))

    colors = [
        (brightness, value3, value1),
        (value2, brightness, value1),
        (value1, brightness, value3),
        (value1, value2, brightness),
        (value3, value1, brightness),
        (brightness, value1, value2)
    ]

    if hue_index >= len(colors):
        hue_index = len(colors) - 1

    red, green, blue = colors[hue_index]
    return int(red * 255), int(green * 255), int(blue * 255)

# Spielvariablen
score = 0
snake = [(WIDTH // 2, HEIGHT // 2)]  # Startposition in der Mitte des Displays
snake_length = 3
snake_direction = 'UP'
text = ""

# Echtzeituhr initialisieren
rtc = machine.RTC()

# Restart-Funktion für das Spiel
def restart_game():
    global snake, snake_length, snake_direction, score, green_targets, target
    score = 0
    snake = [(WIDTH // 2, HEIGHT // 2)]
    snake_length = 3
    snake_direction = 'UP'
    green_targets = []
    display.clear()
    place_target()
    print("Spiel neu gestartet")

# Funktion zur Generierung eines zufälligen Ziels
def random_target():
    return (random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2))

# Initialisierung des Ziels und der grünen Ziele
target = random_target()
green_targets = []

# Funktion zum Platzieren des roten Ziels mit Löschen des alten
def place_target():
    global target
    # Löschen des alten Ziels
    set_pixel_mapped(target[0], target[1], 0, 0, 0)
    # Generieren eines neuen Ziels
    target = random_target()
    set_pixel_mapped(target[0], target[1], 255, 0, 0)  # Rotes Ziel

# Funktion zum Platzieren eines grünen Ziels
def place_green_target():
    x, y = random_target()
    green_targets.append((x, y, 256))  # 256 als Lebensdauer
    set_pixel_mapped(x, y, 0, 255, 0)  # Grünes Ziel

# Aktualisieren der grünen Ziele (Lebensdauer reduzieren und entfernen)
def update_green_targets():
    global green_targets
    new_green_targets = []
    for x, y, lifespan in green_targets:
        if lifespan > 1:
            new_green_targets.append((x, y, lifespan - 1))
        else:
            set_pixel_mapped(x, y, 0, 0, 0)  # Grünes Ziel löschen
    green_targets = new_green_targets

# Funktion zur Suche des nächsten Ziels basierend auf Manhattan-Distanz
def find_nearest_target(head_x, head_y, green_targets, red_target):
    def manhattan_distance(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    min_distance_green = float('inf')
    nearest_green_target = None

    for x, y, _ in green_targets:
        distance = manhattan_distance(head_x, head_y, x, y)
        if distance < min_distance_green:
            min_distance_green = distance
            nearest_green_target = (x, y)

    distance_red = manhattan_distance(head_x, head_y, red_target[0], red_target[1])

    if nearest_green_target and min_distance_green <= distance_red * 1.5:
        return nearest_green_target
    else:
        return red_target

# **Automatische Richtungsaktualisierung**
def update_direction(snake, snake_direction, green_targets, target):
    head_x, head_y = snake[0]
    target_x, target_y = find_nearest_target(head_x, head_y, green_targets, target)
    
    opposite_directions = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}

    new_direction = snake_direction  # Default to current direction

    if head_x == target_x:
        if head_y < target_y and snake_direction != 'UP':
            new_direction = 'DOWN'
        elif head_y > target_y and snake_direction != 'DOWN':
            new_direction = 'UP'
    elif head_y == target_y:
        if head_x < target_x and snake_direction != 'LEFT':
            new_direction = 'RIGHT'
        elif head_x > target_x and snake_direction != 'RIGHT':
            new_direction = 'LEFT'
    else:
        if abs(head_x - target_x) < abs(head_y - target_y):
            if head_x < target_x and snake_direction != 'LEFT':
                new_direction = 'RIGHT'
            elif head_x > target_x and snake_direction != 'RIGHT':
                new_direction = 'LEFT'
        else:
            if head_y < target_y and snake_direction != 'UP':
                new_direction = 'DOWN'
            elif head_y > target_y and snake_direction != 'DOWN':
                new_direction = 'UP'

    if new_direction == opposite_directions[snake_direction]:
        new_direction = snake_direction
    
    return new_direction

# Überprüfen auf Kollision der Schlange mit sich selbst
def check_self_collision():
    global snake, snake_direction
    head_x, head_y = snake[0]
    body = snake[1:]
    if (head_x, head_y) in body:
        restart_game()

# Aktualisieren der Schlange-Position
def update_snake_position():
    global snake, snake_length, snake_direction
    head_x, head_y = snake[0]
    if snake_direction == 'UP':
        head_y -= 1
    elif snake_direction == 'DOWN':
        head_y += 1
    elif snake_direction == 'LEFT':
        head_x -= 1
    elif snake_direction == 'RIGHT':
        head_x += 1

    # Bildschirmgrenzen behandeln (Schlange läuft am anderen Ende wieder herein)
    head_x %= WIDTH
    head_y %= HEIGHT

    snake.insert(0, (head_x, head_y))
    if len(snake) > snake_length:
        tail = snake.pop()
        set_pixel_mapped(tail[0], tail[1], 0, 0, 0)  # Letztes Segment löschen

# Überprüfen auf Kollision mit dem roten Ziel
def check_target_collision():
    global snake, snake_length, target, score
    head_x, head_y = snake[0]
    if (head_x, head_y) == target:
        snake_length += 2
        place_target()
        score += 1

# Überprüfen auf Kollision mit grünen Zielen
def check_green_target_collision():
    global snake, snake_length, green_targets
    head_x, head_y = snake[0]
    for target in green_targets:
        x, y, lifespan = target
        if (head_x, head_y) == (x, y):
            snake_length = max(snake_length // 2, 2)
            green_targets.remove(target)
            set_pixel_mapped(x, y, 0, 0, 0)
            break  # Nur eine Kollision pro Schritt berücksichtigen

# Zeichnen der Schlange auf der Matrix
def draw_snake():
    hue = 0
    for idx, (x, y) in enumerate(snake[:snake_length]):
        hue = (hue + 5) % 360
        r, g, b = hsb_to_rgb(hue, 1, 1)
        set_pixel_mapped(x, y, r, g, b)
    # Entfernen von überschüssigen Segmenten
    for idx in range(snake_length, len(snake)):
        x, y = snake[idx]
        set_pixel_mapped(x, y, 0, 0, 0)

# Anzeigen von Punktzahl und Zeit
def display_score_and_time(score):
    global text
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    time_str = "{:02}:{:02}".format(hour, minute)
    score_str = str(score)
    # Positionierung der Zeit und Punktzahl
    time_x = WIDTH - (len(time_str) * 6) - 1  # Rechtsbündig
    time_y = 1  # Oben
    score_x = 1  # Links
    score_y = 1  # Oben

    # Hintergrund für die Anzeige löschen (kleines Rechteck)
    rect(score_x, score_y, score_x + len(score_str) * 6, score_y + 5, 0, 0, 0)
    rect(time_x, time_y, time_x + len(time_str) * 6, time_y + 5, 0, 0, 0)

    # Zeichnen der Punktzahl und der Zeit
    draw_text(score_x, score_y, score_str, 255, 255, 255)
    draw_text(time_x, time_y, time_str, 255, 255, 255)

# **Automatische Richtungsaktualisierung entfernen und durch automatische Logik ersetzen**
# Entfernen der Funktion zur manuellen Richtungsaktualisierung

# Hauptschleife
def main():
    step_counter = 0
    step_counter2 = 0

    display.start()
    place_target()

    while True:
        step_counter += 1
        step_counter2 += 1

        # Alle 1024 Schritte ein grünes Ziel platzieren
        if step_counter2 % 1024 == 0:
            place_green_target()

        # Lebensdauer der grünen Ziele aktualisieren
        update_green_targets()
            
        global snake_direction
            
        if step_counter % 6 == 0:
            snake_direction = update_direction(snake, snake_direction, green_targets, target)
        elif len(green_targets) > 0:
            if snake[0][0] == green_targets[0][0] or snake[0][1] == green_targets[0][1]:
                snake_direction = update_direction(snake, snake_direction, green_targets, target)
        elif snake[0][0] == target[0] or snake[0][1] == target[1] or snake[0][0] < 4 or snake[0][0] > WIDTH-4 or snake[0][1] < 4 or snake[0][1] > HEIGHT-4:
            snake_direction = update_direction(snake, snake_direction, green_targets, target)


        # Schlange-Position aktualisieren
        update_snake_position()

        # Kollision mit roten Ziel prüfen
        check_target_collision()

        # Kollision mit grünen Zielen prüfen
        check_green_target_collision()

        # Schlange zeichnen
        draw_snake()

        # Punktzahl und Zeit anzeigen
        display_score_and_time(score)

        # Kurze Pause basierend auf der Schlangenlänge
        #time.sleep(max(0.03, (0.09 - max(0.01, snake_length / 300))))

if __name__ == "__main__":
    main()
