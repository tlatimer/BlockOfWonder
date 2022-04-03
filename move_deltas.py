deltas = ({'name': 'L', 'dx': -1, 'dy': 0, 'dist': 2, 'rot': 0, },
          {'name': 'R', 'dx': 1, 'dy': 0, 'dist': 2, 'rot': 180, },
          {'name': 'U', 'dx': 0, 'dy': -1, 'dist': 2, 'rot': 90, },
          {'name': 'D', 'dx': 0, 'dy': 1, 'dist': 2, 'rot': 270, },
          {'name': 'UL', 'dx': -1, 'dy': -1, 'dist': 3, 'rot': 315, },
          {'name': 'DR', 'dx': 1, 'dy': 1, 'dist': 3, 'rot': 135, },
          {'name': 'UR', 'dx': 1, 'dy': -1, 'dist': 3, 'rot': 45, },
          {'name': 'DL', 'dx': -1, 'dy': 1, 'dist': 3, 'rot': 225, })

# deltas itself needs to be ordered, but we also want to retrieve by key. I can spare the RAM.
delta_map = {}
for delta in deltas:
    delta_map[delta['name']] = delta


def get_neighbors(tile_pos):
    to_return = []  # [((new_x, new_y), delta_index),]
    x, y = tile_pos
    for d in deltas:
        to_return.append((
            (x + d['dx'], y + d['dy']), d['name']
        ))
    if x + y % 2:
        return to_return
    else:
        return flip_order(to_return)


def flip_order(this_list):
    # https://www.redblobgames.com/pathfinding/a-star/implementation.html#troubleshooting-ugly-path
    temp = this_list[:4]
    temp.reverse()
    flip_list = temp

    temp = this_list[4:]
    temp.reverse()
    return flip_list + temp
