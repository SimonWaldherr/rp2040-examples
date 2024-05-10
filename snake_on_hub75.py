import hub75
import random
import time
import machine

rtc = machine.RTC()

# Constants
HEIGHT = 64
WIDTH = 64

# Initialize the display
display = hub75.Hub75(WIDTH, HEIGHT)

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

def rect(x1, y1, x2, y2, r, g, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            display.set_pixel(x, y, r, g, b)

def draw_char(x, y, char, r, g, b):
    if char in char_dict:
        matrix = char_dict[char]
        for row in range(5):
            for col in range(5):
                if matrix[row][col] == '1':
                    display.set_pixel(x + col, y + row, r, g, b)

def draw_text(x, y, text, r, g, b):
    offset_x = x
    for char in text:
        draw_char(offset_x, y, char, r, g, b)
        offset_x += 6

def hsb_to_rgb(hue, saturation, brightness):
    # Normalisiere den Farbton auf einen Bereich von 0 bis 6
    hue_normalized = (hue % 360) / 60
    hue_index = int(hue_normalized)
    hue_fraction = hue_normalized - hue_index

    # Berechne die RGB-Intermediärwerte auf Basis der Sättigung und Helligkeit
    value1 = brightness * (1 - saturation)
    value2 = brightness * (1 - saturation * hue_fraction)
    value3 = brightness * (1 - saturation * (1 - hue_fraction))

    # Zuweisung der RGB-Werte basierend auf dem Bereich, in dem der Farbton liegt
    red, green, blue = [
        (brightness, value3, value1),
        (value2, brightness, value1),
        (value1, brightness, value3),
        (value1, value2, brightness),
        (value3, value1, brightness),
        (brightness, value1, value2)
    ][hue_index]

    # Umwandlung von RGB-Werten von 0-1 Skala zu 0-255 Skala und Rückgabe als Ganzzahlen
    return int(red * 255), int(green * 255), int(blue * 255)


score = 0
snake = [(32, 32)]
snake_length = 3
snake_direction = 'UP'
text = ""

def restart_game():
    global snake, snake_length, snake_direction, score, green_targets
    score = 0
    snake = [(32, 32)]
    snake_length = 3
    snake_direction = 'UP'
    target = random_target()
    green_targets = []
    display.clear()
    place_target()
    print("Game restarted")

def random_target():
    global target
    target = (random.randint(1, WIDTH-2), random.randint(1, HEIGHT-8))
    return target

target = random_target()
green_targets = []

def place_target():
    global target
    target = random_target()
    display.set_pixel(target[0], target[1], 255, 0, 0)  # Red target

def place_green_target():
    x, y = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-8)
    green_targets.append((x, y, 256)) 
    display.set_pixel(x, y, 0, 255, 0)  # Green target

def update_green_targets():
    global green_targets, snake_length
    new_green_targets = []
    for x, y, lifespan in green_targets:
        if lifespan > 1:
            new_green_targets.append((x, y, lifespan - 1))
        else:
            display.set_pixel(x, y, 0, 0, 0)  # Clear green target from display
    green_targets = new_green_targets

def find_nearest_target(head_x, head_y, green_targets, fallback_target):
    min_distance = float('inf')
    nearest_target = fallback_target
    for x, y, _ in green_targets:
        distance = abs(head_x - x) + abs(head_y - y)
        if distance < min_distance:
            nearest_target = (x, y)
            min_distance = distance
    return nearest_target

def update_direction(snake, snake_direction, green_targets, target):
    head_x, head_y = snake[0]
    target_x, target_y = find_nearest_target(head_x, head_y, green_targets, target)

    # Priorisiere die Achse für die Bewegung
    if head_x == target_x:
        if head_y < target_y and snake_direction != 'UP':
            snake_direction = 'DOWN'
        elif head_y > target_y and snake_direction != 'DOWN':
            snake_direction = 'UP'
    elif head_y == target_y:
        if head_x < target_x and snake_direction != 'LEFT':
            snake_direction = 'RIGHT'
        elif head_x > target_x and snake_direction != 'RIGHT':
            snake_direction = 'LEFT'
    else:
        if abs(head_x - target_x) < abs(head_y - target_y):
            if head_x < target_x and snake_direction != 'LEFT':
                snake_direction = 'RIGHT'
            elif head_x > target_x and snake_direction != 'RIGHT':
                snake_direction = 'LEFT'
        else:
            if head_y < target_y and snake_direction != 'UP':
                snake_direction = 'DOWN'
            elif head_y > target_y and snake_direction != 'DOWN':
                snake_direction = 'UP'

    return snake_direction


def check_self_collision():
    global snake, snake_direction, snake_length
    head_x, head_y = snake[0]
    body = snake[1:]
    potential_moves = {
        'UP': (head_x, head_y - 1),
        'DOWN': (head_x, head_y + 1),
        'LEFT': (head_x - 1, head_y),
        'RIGHT': (head_x + 1, head_y)
    }
    safe_moves = {dir: pos for dir, pos in potential_moves.items() if pos not in body}
    if potential_moves[snake_direction] not in safe_moves.values():
        if safe_moves:
            snake_direction = random.choice(list(safe_moves.keys()))
        else:
            restart_game()

def display_score_and_time(score):
    global text
    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    time_str = "{:02}:{:02}".format(hour, minute)
    score_str = str(score)
    time_x = WIDTH - (len(time_str) * 6)
    time_y = HEIGHT - 6
    score_x = 1
    score_y = HEIGHT - 6
    if text != score_str + " " + time_str:
        text = score_str + " " + time_str
        rect(score_x, score_y, WIDTH, score_y+5, 0, 0, 0)
    draw_text(score_x, score_y, score_str, 255, 255, 255)
    draw_text(time_x, time_y, time_str, 255, 255, 255)

step_counter = 0
step_counter2 = 0

display.start()
place_target()
while True:
    step_counter += 1
    step_counter2 += 1
    
    if step_counter2 % 1024 == 0:
        place_green_target()
    update_green_targets()

    if step_counter % 8 == 0:
        snake_direction = update_direction(snake, snake_direction, green_targets, target)
    elif len(green_targets) > 0:
        if snake[0][0] == green_targets[0][0] or snake[0][1] == green_targets[0][1]:
            snake_direction = update_direction(snake, snake_direction, green_targets, target)
    elif snake[0][0] == target[0] or snake[0][1] == target[1] or snake[0][0] < 4 or snake[0][0] > WIDTH-4 or snake[0][1] < 4 or snake[0][1] > HEIGHT-4:
        snake_direction = update_direction(snake, snake_direction, green_targets, target)


    check_self_collision()

    head_x, head_y = snake[0]
    if snake_direction == 'UP':
        head_y -= 1
    elif snake_direction == 'DOWN':
        head_y += 1
    elif snake_direction == 'LEFT':
        head_x -= 1
    elif snake_direction == 'RIGHT':
        head_x += 1

    head_x %= WIDTH
    head_y %= HEIGHT

    snake.insert(0, (head_x, head_y))
    if len(snake) > snake_length:
        tail = snake.pop()
        display.set_pixel(tail[0], tail[1], 0, 0, 0)

    if (head_x, head_y) == target:
        snake_length += 2
        place_target()
        score += 1
        step_counter = 4

    for x, y, lifespan in green_targets:
        if (head_x, head_y) == (x, y):
            snake_length = max(snake_length // 2, 2)  # Halve the snake length, minimum length 2
            green_targets.remove((x, y, lifespan))
            display.set_pixel(x, y, 0, 0, 0)  # Clear the green target

    hue = 0
    
    for idx, (x, y) in enumerate(snake[:snake_length]):
        hue = (hue + 5) % 360  # Update hue for rainbow effect
        r, g, b = hsb_to_rgb(hue, 1, 1)
        display.set_pixel(x, y, r, g, b)

    for idx in range(snake_length, len(snake)):
        x, y = snake[idx]
        display.set_pixel(x, y, 0, 0, 0) 

    display_score_and_time(score)

    time.sleep(max(0.03, (0.09-max(0.01, snake_length/300))))
