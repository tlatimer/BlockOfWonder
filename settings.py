screen_w = 1366
screen_h = 768

grid_w = 13
grid_h = 11

assert grid_w >= grid_h

tile_size = int(min(screen_h, screen_w) / grid_h)
border_size = 2
default_border_color = 'gray20'

unit_radius = int(tile_size / 6)
unit_speed = 1.5  # tiles per second

deltas_cardinal = [
    [-1, 0], [1, 0], [0, -1], [0, 1]
]
deltas_diagonal = [
    [-1, -1], [1, 1], [-1, 1], [1, -1]
]

# tasks are done in priorities from first to last
unit_task_types = ['input', 'output']