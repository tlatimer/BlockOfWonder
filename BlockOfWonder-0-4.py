from queue import Queue
from random import choice

import pygame as pg
from pygame.sprite import Sprite, Group

import settings as s


class BlockOfWonder:
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(
            (s.screen_w, s.screen_h),
            # pg.FULLSCREEN
        )

        self.grid = Grid()  # debating on whether to make this global

        self.buildings = Group()
        self.units = Group()

    def main_loop(self, fps=3):
        self.grid.tiles.draw(self.screen)
        self.buildings.draw(self.screen)
        self.units.draw(self.screen)

        self.units.update()

        self.check_for_quit()
        pg.display.flip()
        self.clock.tick(fps)

    def check_for_quit(self):
        if pg.event.get(pg.QUIT):
            pg.quit()
            exit()

        for event in pg.event.get(pg.KEYDOWN):
            if event.key == pg.K_ESCAPE:
                pg.quit()
                exit()

            # did not exit, put the event back in the queue
            pg.event.post(event)


class Grid:
    def __init__(self):
        self.tiles = Group()

        # populate the tiles
        for x in range(s.grid_w):
            for y in range(s.grid_h):
                pos = (x, y)
                self.tiles.add(Tile(pos))

        # to lookup by coords
        self.tile_dict = {}
        for t in self.tiles:
            self.tile_dict[t.pos] = t

        self.tiles_walkable = Group()
        self.set_walkable_tiles()

    def set_walkable_tiles(self):
        self.tiles_walkable.empty()

        for t in self.tiles:
            if t.is_walkable:
                self.tiles_walkable.add(t)

    def path_bfs(self, src_tile, dest_tile):
        visited = set()
        to_visit = Queue()
        to_visit.put(src_tile)
        for t in self.tiles:
            t.pf_parent = None

        while to_visit:
            cur_tile = to_visit.get()
            to_visit.task_done()  # needed for queue stuff
            visited.add(cur_tile)
            if cur_tile == dest_tile:
                break

            for delta in self._get_deltas(cur_tile.pos):
                new_pos = self._add_pos(cur_tile.pos, delta)
                if new_pos in self.tile_dict:
                    new_tile = self.tile_dict[new_pos]
                    if not new_tile.pf_parent and new_tile.is_walkable and new_tile not in visited:
                        new_tile.pf_parent = cur_tile
                        to_visit.put(new_tile)

        path = []
        while cur_tile.pf_parent:
            cur_tile = cur_tile.pf_parent
            path.append(cur_tile)

        path.reverse()
        return path

    def _add_pos(self, pos, delta):
        x1, y1 = pos
        x2, y2 = delta
        return x1 + x2, y1 + y2

    def _get_deltas(self, pos):
        if sum(pos) % 2:
            return s.deltas_cardinal + s.deltas_diagonal
        else:
            return s.deltas_cardinal[::-1] + s.deltas_diagonal[::-1]

    def get_random_tile(self):
        return choice(self.tiles_walkable.sprites())


class Tile(Sprite):
    def __init__(self, pos):
        super().__init__()

        self.pos = pos  # (x, y)

        self.color_border = s.default_border_color
        self.color_inner = 'black'
        self._redraw()

        # pathfinding variables
        self.pf_parent = None
        self.is_walkable = True

        self.parent_building = None

    def __repr__(self):
        if self.pf_parent:
            repr_parent = self.pf_parent.pos
        else:
            repr_parent = 'None'
        return f'Tile: {self.pos} -> {repr_parent}'

    def _redraw(self, size=1):  # size isn't technically used for Tile, but for subclass Building
        x, y = self.pos
        self.rect = pg.Rect(x * s.tile_size,  # relative to screen
                            y * s.tile_size,
                            s.tile_size * size,
                            s.tile_size * size)

        inner_rect = pg.Rect(s.border_size,  # relative to tile
                             s.border_size,
                             s.tile_size * size - 2 * s.border_size,
                             s.tile_size * size - 2 * s.border_size)

        self.image = pg.Surface((s.tile_size * size, s.tile_size * size))
        self.image.fill(self.color_border)
        pg.draw.rect(self.image, self.color_inner, inner_rect, border_radius=10 * size)

    def set_border_color(self, color):
        self.color_border = color
        self._redraw()

    def set_parent(self, parent):
        self.parent_building = parent


class Building(Tile):
    def __init__(self, pos, size, grid):
        super().__init__(pos)

        self.pos = pos
        self.size = size

        self.sub_tiles = pg.sprite.Group()
        self.set_sub_tiles(grid)
        grid.set_walkable_tiles()

        self.entrance_tile = None

        self.items_storage = ItemList()
        self.items_crafting = ItemList()
        self.items_output = ItemList()

        self.color_inner = 'blue4'
        self._redraw(size)

        self.drawn_this_frame = False

    def set_sub_tiles(self, grid):
        grid_x, grid_y = self.pos
        for x in range(grid_x, grid_x + self.size):
            for y in range(grid_y, grid_y + self.size):
                t = grid.tile_dict[(x, y)]
                t.set_parent(self)
                t.is_walkable = False
                self.sub_tiles.add(t)


def can_place_building(grid, grid_x, grid_y, size):
    for x in range(grid_x, grid_x + size):
        for y in range(grid_y, grid_y + size):
            t = grid.tile_dict[(x, y)]
            if t.parent_building:
                return False
    return True


class Unit(Sprite):
    def __init__(self, cur_tile):
        super().__init__()

        self.cur_tile = cur_tile

        self.color = 'white'
        
        self._redraw()

        self.path = None
        self.ticks_passed = 0

    def set_path(self, path):
        self.path = path

    def _redraw(self):
        ur = s.unit_radius

        self.rect = pg.Rect(self.cur_tile.rect.centerx - ur,
                            self.cur_tile.rect.centery - ur,
                            ur * 2,
                            ur * 2)

        self.image = pg.Surface((ur * 2, ur * 2))
        pg.draw.circle(self.image, self.color, (ur, ur), ur)

    def update(self, tick_ms):
        if self.path:
            self.ticks_passed += tick_ms
            self.cur_tile = self.path.pop(0)
            self._redraw()


class ItemList:
    def __init__(self):
        self.items = {}  # {Item: qty}

    def check_if_contains(self, item_list):
        pass

    def multiply(self, num):
        """note that this returns multiplied, but doesn't affect the itemlist itself"""
        pass


def main():
    bow = BlockOfWonder()

    nexus_pos = ((int(s.grid_w / 2) - 1), (int(s.grid_h / 2) - 1))
    nexus = Building(nexus_pos, 3, bow.grid)
    bow.buildings.add(nexus)

    for _ in range(30):
        nexus = Building(bow.grid.get_random_tile().pos, 1, bow.grid)
        bow.buildings.add(nexus)

    for _ in range(10):
        my_unit = Unit(bow.grid.get_random_tile())
        bow.units.add(my_unit)

    while True:
        for u in bow.units.sprites():
            if not u.path:
                u.path = bow.grid.path_bfs(u.cur_tile, bow.grid.get_random_tile())

        bow.main_loop()


if __name__ == '__main__':
    main()

