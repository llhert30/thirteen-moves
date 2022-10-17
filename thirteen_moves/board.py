BLUE = "B"
RED = "R"


class Board:
    WIDTH = 5
    HEIGHT = 6

    def __init__(self, tiles):
        self.tiles = tiles

    def __str__(self):
        tiles = self.to_array()
        string = "------------------\n"
        for y in range(Board.HEIGHT):
            string += "| "
            for x in range(Board.WIDTH):
                tile = tiles[x][y]
                if tile != 0:
                    string += tile
                    string += "  "
                else:
                    string += ".. "
            string += "| \n"
        string += "------------------"
        return string + "\n"

    def to_array(self):
        height = Board.HEIGHT
        width = Board.WIDTH

        tiles = [[0 for _ in range(height)] for _ in range(width)]

        blue_tiles = self.tiles[0]
        red_tiles = self.tiles[1]

        for tile in blue_tiles:
            x = tile % width
            y = tile // width
            tiles[x][y] = BLUE

        for tile in red_tiles:
            x = tile % width
            y = tile // width
            tiles[x][y] = RED

        return tiles

    @classmethod
    def new(cls):
        """
        `tiles` is a tuple consisting of 2 arrays, with the first
        one representing the positions of the blue tiles, and
        the second one representing the positions of the red tiles.
        Each position is an integer, calculated by width*y+x. For
        example, (1, 3) with width 5 => 16. Tiles are stored this way
        so cloning and other operations are faster.
        """

        tiles = ([], [])

        height = Board.HEIGHT
        width = Board.WIDTH

        end_row = height-1
        for i in range(Board.WIDTH):
            tiles[0].append(end_row*width+i)

        for i in range(Board.WIDTH):
            tiles[1].append(i)

        return cls(tiles)

    def clone(self):
        tiles = (self.tiles[0].copy(), self.tiles[1].copy())
        return Board(tiles)

    @staticmethod
    def in_bounds(x, y):
        return 0 <= x < Board.WIDTH and 0 <= y < Board.HEIGHT

    def get_valid_moves(self, color):
        width = Board.WIDTH

        if color == BLUE:
            dirs = ((-1, -width-1), (0, -width), (1, -width+1))
            player_tiles = self.tiles[0]
        else:
            dirs = ((-1, width-1), (0, width), (1, width+1))
            player_tiles = self.tiles[1]

        valid_moves = []
        player_tile_set = set(player_tiles)
        for from_tile in player_tiles:
            tile_x = from_tile % width
            for j, direction in dirs:
                x = tile_x + j
                if 0 <= x < width:
                    to_tile = from_tile + direction
                    # Tiles cannot be moved to other tiles of the same color
                    if to_tile not in player_tile_set:
                        valid_moves.append([from_tile, to_tile])
        return valid_moves

    def perform_move(self, color, move):
        from_tile, to_tile = move
        tiles = self.tiles

        if color == BLUE:
            player_tiles = tiles[0]
            enemy_tiles = tiles[1]
        else:
            player_tiles = tiles[1]
            enemy_tiles = tiles[0]

        player_tiles[player_tiles.index(from_tile)] = to_tile
        if to_tile in enemy_tiles:
            enemy_tiles.remove(to_tile)

    def is_winning(self):
        blue_tiles = self.tiles[0]
        red_tiles = self.tiles[1]

        if len(blue_tiles) == 0:
            return RED
        if len(red_tiles) == 0:
            return BLUE

        width = Board.WIDTH
        for tile in blue_tiles:
            if tile // width == 0:
                return BLUE

        height_1 = Board.HEIGHT - 1
        for tile in red_tiles:
            if tile // width == height_1:
                return RED

        return False
