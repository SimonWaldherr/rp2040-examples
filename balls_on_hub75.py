import time
import random
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X64

i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X64)
graphics = i75.display

width = i75.width
height = i75.height

class Ball:
    def __init__(self, x, y, r, dx, dy, hue, saturation, brightness):
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness
        self.pen = None
        self.update_pen()

    def update_pen(self):
        r, g, b = hsb_to_rgb(self.hue, self.saturation, self.brightness)
        self.pen = graphics.create_pen(r, g, b)

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

balls = []
for i in range(0, 10):
    r = random.randint(0, 3) + 3
    hue = random.randint(0, 359)
    saturation = 1.0
    brightness = 1.0
    balls.append(
        Ball(
            random.randint(r, r + (width - 2 * r)),
            random.randint(r, r + (height - 2 * r)),
            r,
            (7 - r) / 4,
            (7 - r) / 4,
            hue,
            saturation,
            brightness
        )
    )

BG = graphics.create_pen(0, 0, 0)

while True:
    graphics.set_pen(BG)
    graphics.clear()

    for ball in balls:
        ball.x += ball.dx
        ball.y += ball.dy

        xmax = width - ball.r
        xmin = ball.r
        ymax = height - ball.r
        ymin = ball.r

        if ball.x < xmin or ball.x > xmax:
            ball.dx *= -1

        if ball.y < ymin or ball.y > ymax:
            ball.dy *= -1

        ball.hue = (ball.hue + 1) % 360
        ball.update_pen()

        graphics.set_pen(ball.pen)
        graphics.circle(int(ball.x), int(ball.y), int(ball.r))

    i75.update()
