deltas = ({'name': 'L', 'dx': -1, 'dy': 0, 'dist': 2, 'rot': 0, },
          {'name': 'R', 'dx': 1, 'dy': 0, 'dist': 2, 'rot': 180, },
          {'name': 'U', 'dx': 0, 'dy': -1, 'dist': 2, 'rot': 90, },
          {'name': 'D', 'dx': 0, 'dy': 1, 'dist': 2, 'rot': 270, },
          {'name': 'UL', 'dx': -1, 'dy': -1, 'dist': 3, 'rot': 315, },
          {'name': 'DR', 'dx': 1, 'dy': 1, 'dist': 3, 'rot': 135, },
          {'name': 'UR', 'dx': 1, 'dy': -1, 'dist': 3, 'rot': 45, },
          {'name': 'DL', 'dx': -1, 'dy': 1, 'dist': 3, 'rot': 225, })


def get_neighbors(tile_pos):
    to_return = []  # [((new_x, new_y), delta_index),]
    x, y = tile_pos
    for i in range(8):
        to_return.append((
            (x + deltas[i]['dx'], y + deltas[i]['dy']), i
        ))
    if x + y % 2:
        return to_return
    else:
        return flip_order(to_return)


def flip_order(list):
    temp = list[:4]
    temp.reverse()
    flip_list = temp

    temp = list[4:]
    temp.reverse()
    return flip_list + temp


print(get_neighbors((2, 2)))
