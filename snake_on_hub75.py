import hub75
import random
import time

# Constants
HEIGHT = 64
WIDTH = 64

# Initialize the display
display = hub75.Hub75(WIDTH, HEIGHT)

# HSB to RGB Conversion
def hsb_to_rgb(h, s, b):
    if s == 0:
        return int(b * 255), int(b * 255), int(b * 255)
    h = h % 360
    h /= 60
    i = int(h)
    f = h - i
    p = b * (1 - s)
    q = b * (1 - s * f)
    t = b * (1 - s * (1 - f))
    p, q, t, b = int(p * 255), int(q * 255), int(t * 255), int(b * 255)
    if i == 0:
        return b, t, p
    elif i == 1:
        return q, b, p
    elif i == 2:
        return p, b, t
    elif i == 3:
        return p, q, b
    elif i == 4:
        return t, p, b
    elif i == 5:
        return b, p, q

# Initial snake settings
snake = [(32, 32)]
snake_length = 3
snake_direction = 'UP'
target = (random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2))

def restart_game():
    global snake, snake_length, snake_direction, target
    snake = [(32, 32)]
    snake_length = 3
    snake_direction = 'UP'
    target = (random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2))
    display.clear()  # Lösche das gesamte Display
    place_target()  # Platziere ein neues Ziel
    print("Game restarted")


def place_target():
    global target
    target = (random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2))
    display.set_pixel(target[0], target[1], 255, 0, 0)

def update_direction():
    global snake_direction
    head_x, head_y = snake[0]
    target_x, target_y = target

    # Priorisiere die Achse, auf der sich das Ziel nicht auf der gleichen Linie befindet
    if head_x == target_x:
        # Vertikale Bewegung ist erforderlich, da x bereits gleich ist
        if head_y < target_y and snake_direction != 'UP':
            snake_direction = 'DOWN'
        elif head_y > target_y and snake_direction != 'DOWN':
            snake_direction = 'UP'
    elif head_y == target_y:
        # Horizontale Bewegung ist erforderlich, da y bereits gleich ist
        if head_x < target_x and snake_direction != 'LEFT':
            snake_direction = 'RIGHT'
        elif head_x > target_x and snake_direction != 'RIGHT':
            snake_direction = 'LEFT'
    else:
        # Wenn sich das Ziel nicht auf der gleichen Linie befindet, entscheide basierend auf der kleineren Distanz
        if abs(head_x - target_x) < abs(head_y - target_y):
            # Horizontale Annäherung
            if head_x < target_x and snake_direction != 'LEFT':
                snake_direction = 'RIGHT'
            elif head_x > target_x and snake_direction != 'RIGHT':
                snake_direction = 'LEFT'
        else:
            # Vertikale Annäherung
            if head_y < target_y and snake_direction != 'UP':
                snake_direction = 'DOWN'
            elif head_y > target_y and snake_direction != 'DOWN':
                snake_direction = 'UP'


def check_self_collision():
    global snake, snake_direction, snake_length
    head_x, head_y = snake[0]
    body = snake[1:]  # Der Rest des Körpers ohne den Kopf

    # Potenzielle neue Kopfpositionen basierend auf möglichen Richtungen
    potential_moves = {
        'UP': (head_x, head_y - 1),
        'DOWN': (head_x, head_y + 1),
        'LEFT': (head_x - 1, head_y),
        'RIGHT': (head_x + 1, head_y)
    }

    # Filtere mögliche Bewegungen, die nicht zu einer Kollision führen würden
    safe_moves = {dir: pos for dir, pos in potential_moves.items() if pos not in body}

    # Wenn der aktuelle Bewegungspfad nicht sicher ist, wähle eine neue Richtung aus den sicheren Bewegungen
    if potential_moves[snake_direction] not in safe_moves.values():
        if safe_moves:
            snake_direction = random.choice(list(safe_moves.keys()))  # Zufällige sichere Bewegung
        else:
            # Keine sichere Bewegung möglich, starte das Spiel neu
            restart_game()



step_counter = 0

# Main game loop
display.start()
place_target()
while True:
    step_counter += 1
    
    # Prüfe und aktualisiere die Richtung alle 16 Schritte oder wenn auf gleicher Linie
    if step_counter % 8 == 0 or snake[0][0] == target[0] or snake[0][1] == target[1]:
        update_direction()
    
    # Prüfe auf Selbstkollision und verhindere diese oder starte neu
    check_self_collision()
    
    # Calculate new head position
    head_x, head_y = snake[0]
    if snake_direction == 'UP':
        head_y -= 1
    elif snake_direction == 'DOWN':
        head_y += 1
    elif snake_direction == 'LEFT':
        head_x -= 1
    elif snake_direction == 'RIGHT':
        head_x += 1
    
    # Wrap around
    head_x %= WIDTH
    head_y %= HEIGHT
    
    # Insert new head
    snake.insert(0, (head_x, head_y))
    if len(snake) > snake_length:
        tail = snake.pop()
        display.set_pixel(tail[0], tail[1], 0, 0, 0)  # Clear the tail from the display
    
    # Check for collision with target
    if (head_x, head_y) == target or (head_x, head_y) == (target[0]+1, target[1]) or \
       (head_x, head_y) == (target[0], target[1]+1) or (head_x, head_y) == (target[0]+1, target[1]+1):
        snake_length += 4  # Increase snake length
        place_target()     # Place a new target
    
    # Update snake on display
    hue = 0
    for idx, (x, y) in enumerate(snake):
        hue = (hue + 5) % 360  # Update hue for rainbow effect
        r, g, b = hsb_to_rgb(hue, 1, 1)
        display.set_pixel(x, y, r, g, b)
    
    time.sleep(0.04)
