import hub75
import random
import time
import machine
from machine import ADC

# Initialize ADC for joystick
adc0 = ADC(0)
adc1 = ADC(1)
adc2 = ADC(2)

# Constants
HEIGHT = 64
WIDTH = 64

# Initialize the display
display = hub75.Hub75(WIDTH, HEIGHT)

# Color definitions
colors_bright = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255),   # Blue
    (255, 255, 0)  # Yellow
]

colors = [(int(r * 0.5), int(g * 0.5), int(b * 0.5)) for r, g, b in colors_bright]
inactive_colors = [(int(r * 0.2), int(g * 0.2), int(b * 0.2)) for r, g, b in colors_bright]

# Game states
simon_sequence = []
user_sequence = []

def rect(x1, y1, x2, y2, r, g, b):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            display.set_pixel(x, y, r, g, b)

def draw_quad_screen():
    rect(0, 0, WIDTH // 2 - 1, HEIGHT // 2 - 1, *inactive_colors[0])
    rect(WIDTH // 2, 0, WIDTH - 1, HEIGHT // 2 - 1, *inactive_colors[1])
    rect(0, HEIGHT // 2, WIDTH // 2 - 1, HEIGHT - 1, *inactive_colors[2])
    rect(WIDTH // 2, HEIGHT // 2, WIDTH - 1, HEIGHT - 1, *inactive_colors[3])

def flash_color(index, duration=0.5):
    x, y = index % 2, index // 2
    rect(x * WIDTH // 2, y * HEIGHT // 2, (x + 1) * WIDTH // 2 - 1, (y + 1) * HEIGHT // 2 - 1, *colors[index])
    time.sleep(duration)
    rect(x * WIDTH // 2, y * HEIGHT // 2, (x + 1) * WIDTH // 2 - 1, (y + 1) * HEIGHT // 2 - 1, *inactive_colors[index])

def play_sequence():
    for color in simon_sequence:
        flash_color(color)
        time.sleep(0.5)

def get_joystick_direction():
    read0 = adc0.read_u16()
    read1 = adc1.read_u16()
    read2 = adc2.read_u16()

    valueX = read0 - 32768  # Adjusted to be centered at 0
    valueY = read1 - 32768  # Adjusted to be centered at 0

    if abs(valueX) > abs(valueY):
        if valueX > 10000:
            return 'RIGHT'
        elif valueX < -10000:
            return 'LEFT'
    else:
        if valueY > 10000:
            return 'DOWN'
        elif valueY < -10000:
            return 'UP'

    return None

def get_user_input():
    while True:
        joystick_dir = get_joystick_direction()
        if joystick_dir:
            return joystick_dir
        time.sleep(0.1)

def translate_joystick_to_color(joystick_dir):
    if joystick_dir == 'UP':
        return 0
    elif joystick_dir == 'RIGHT':
        return 1
    elif joystick_dir == 'LEFT':
        return 2
    elif joystick_dir == 'DOWN':
        return 3
    return None

def check_user_sequence():
    for i in range(len(user_sequence)):
        if user_sequence[i] != simon_sequence[i]:
            return False
    return True

def start_game():
    global simon_sequence, user_sequence
    simon_sequence = []
    user_sequence = []
    draw_quad_screen()

def joystick_test():
    start_time = time.time()
    while time.time() - start_time < 10:
        joystick_dir = get_joystick_direction()
        if joystick_dir:
            print(f"Joystick moved: {joystick_dir}")
            color_index = translate_joystick_to_color(joystick_dir)
            if color_index is not None:
                flash_color(color_index, 0.5)
        time.sleep(0.1)
    print("Joystick test completed")

def main_game_loop():
    global simon_sequence, user_sequence

    start_game()
    #joystick_test()
    while True:
        simon_sequence.append(random.randint(0, 3))
        play_sequence()
        user_sequence = []

        for _ in range(len(simon_sequence)):
            joystick_dir = get_user_input()
            selected_color = translate_joystick_to_color(joystick_dir)
            if selected_color is not None:
                flash_color(selected_color, 0.2)
                user_sequence.append(selected_color)
            else:
                print("Invalid input")
                break

        if not check_user_sequence():
            print("Game Over")
            start_game()

        time.sleep(1)

display.start()

main_game_loop()

