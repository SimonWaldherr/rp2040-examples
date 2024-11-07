import hub75
import math
import time
import machine
from machine import Pin
import micropython

# Constants for the physical display
HEIGHT = 128
WIDTH = 128

xHEIGHT = 32    # 32 rows per module
xWIDTH = 512    # 8 modules in a row of 64 columns each = 512 columns

# Initialize the display with real hardware resolution
display = hub75.Hub75(xWIDTH, xHEIGHT)

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

# Wrapper for set_pixel with remapping
def set_pixel_mapped(x, y, r, g, b):
    x1, y1 = newXY(x, y)
    if 0 <= x1 < xWIDTH and 0 <= y1 < xHEIGHT:
        display.set_pixel(x1, y1, r, g, b)

# 3D Cube Rotation Parameters
cube_size = 30
angle_x = 0
angle_y = 0
angle_z = 0
rotation_speed = 0.05

# Define cube vertices
vertices = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1)
]

# Define cube edges
edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

def rotate_vertex(x, y, z, angle_x, angle_y, angle_z):
    # Rotation around X-axis
    cos_x = math.cos(angle_x)
    sin_x = math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    # Rotation around Y-axis
    cos_y = math.cos(angle_y)
    sin_y = math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    # Rotation around Z-axis
    cos_z = math.cos(angle_z)
    sin_z = math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

    return x, y, z

def draw_line(x1, y1, x2, y2, r, g, b):
    # Bresenham's Line Algorithm
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        set_pixel_mapped(x1, y1, r, g, b)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy

def rotate_and_project(vertices, angle_x, angle_y, angle_z):
    projected = []
    for v in vertices:
        rotated = rotate_vertex(v[0], v[1], v[2], angle_x, angle_y, angle_z)
        # Simple orthographic projection
        x = int(rotated[0] * cube_size) + WIDTH // 2
        y = int(rotated[1] * cube_size) + HEIGHT // 2
        projected.append((x, y))
    return projected

def rotating_cube():
    global angle_x, angle_y, angle_z
    display.start()
    
    while True:
        display.clear()
        projected_vertices = rotate_and_project(vertices, angle_x, angle_y, angle_z)
        
        # Draw edges
        for edge in edges:

            start = projected_vertices[edge[0]]
            end = projected_vertices[edge[1]]
            # Color based on edge index
            color = (
                (edge[0] * 20) % 256,
                (edge[1] * 40) % 256,
                (edge[0] * edge[1] * 15) % 256
            )

            

            # Draw line between vertices
            draw_line(start[0], start[1], end[0], end[1], *color)
        
        #display.update()
        angle_x += rotation_speed
        angle_y += rotation_speed
        angle_z += rotation_speed
        #time.sleep(0.03)

# Run the rotating cube animation
if __name__ == "__main__":
    try:
        rotating_cube()
    except KeyboardInterrupt:
        display.clear()
        display.update()

