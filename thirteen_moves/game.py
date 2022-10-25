from board import Board
import pygame
from visual_utils import alpha_rect, centered_text, set_cursor_to_default, Text
from ai import play
import time
import random


END = (32, 32, 32)
GRAY = (160, 160, 160)
WHITE = (255, 255, 255)

TILE_BLUE = "B"
TILE_RED = "R"

# List of AI players, if both are included AI plays against itself
# Possible options: `TILE_BLUE`, `TILE_RED`
AI_PLAYER = [TILE_RED]

# Depth of each AI player
DEPTHS = {TILE_BLUE: 10, TILE_RED: 10}

# Min time for an AI move so it feels natural
wait = 0.5

# Only winning first moves (depth 26)
first_blue_move = [[1, 20], [3, 24]]

YELLOW = (246, 190, 0)
RED = (135, 34, 34)
BLUE = (34, 34, 135)
LIGHT_RED = (255, 102, 102)
LIGHT_BLUE = (102, 102, 255)


class Game:
    def __init__(self, board, x, y, width, height, tile_padding, x_center):
        self.board = board
        self.tiles = self.board.to_array()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tile_padding = tile_padding
        self.x_center = x_center

        self.tile_width = self.width / Board.WIDTH
        self.tile_height = self.height / Board.HEIGHT
        self.tile_filled_width = self.tile_width * (1 - self.tile_padding)
        self.tile_filled_height = self.tile_height * (1 - self.tile_padding)

        self.held_tile = None
        self.winning = None
        self.player = TILE_BLUE
        self.moves = 0

        self.new_game_text = Text("New Game", self.x_center, y + self.height * 15/24, GRAY, WHITE, font_size=40)

    @classmethod
    def new(cls, x=0, y=0, width=None, height=None, tile_padding=0.07, x_center=250):
        board = Board.new()
        if width is None:
            width = board.WIDTH * 100
        if height is None:
            height = board.HEIGHT * 100
        return cls(board, x, y, width, height, tile_padding, x_center)

    @staticmethod
    def display_end_screen(surface):
        alpha_rect(surface, color=END, alpha=0.85)

    def new_game(self):
        set_cursor_to_default()

        self.board = Board.new()
        self.winning = None
        self.held_tile = None
        self.player = TILE_BLUE
        self.moves = 0

    def mouse_pos_to_tile(self, mouse_pos):
        x, y = mouse_pos
        x = (x - self.x) / self.tile_width
        y = (y - self.y) / self.tile_height

        return round(x-0.5), round(y-0.5)

    def tile_pos_to_rect(self, tile_pos):
        x, y = tile_pos

        game_x = self.tile_width * x + self.tile_width * self.tile_padding / 2 + self.x
        game_y = self.tile_height * y + self.tile_height * self.tile_padding / 2 + self.y

        rect = (game_x, game_y, self.tile_filled_width, self.tile_filled_height)
        return rect

    def switch_player(self):
        self.moves += 1
        if self.player == TILE_BLUE:
            self.player = TILE_RED
        else:
            self.player = TILE_BLUE

    def display(self, surface, events):
        self.display_move_counter(surface)

        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                self.display_tile(surface, (x, y))

        if not (self.held_tile is None):
            self.highlight_valid_moves(surface, self.held_tile)
            self.display_tile_on_mouse(surface, self.held_tile, events.mouse_pos)

        if not (self.winning is None):
            self.display_end_screen(surface)
            self.display_player_wins(surface)
            self.new_game_text.display(surface)

    def display_tile(self, surface, tile_pos):
        x, y = tile_pos

        if self.held_tile is None:
            held = None
        else:
            held = self.held_tile[1:]

        tile = self.tiles[x][y]
        rect = self.tile_pos_to_rect((x, y))

        if tile == 0 or (x, y) == held:
            pygame.draw.rect(surface, GRAY, rect)
        elif tile == TILE_BLUE:
            pygame.draw.rect(surface, BLUE, rect)
        else:
            pygame.draw.rect(surface, RED, rect)

    def highlight_valid_moves(self, surface, tile):
        for move in self.board.get_valid_moves(TILE_BLUE):
            if move[0] == tile:
                self.highlight_move(surface, move)

    def highlight_move(self, surface, move):
        tile_pos = move.xto, move.yto
        self.highlight_tile(surface, tile_pos)

    def highlight_tile(self, surface, tile_pos):
        rect = self.tile_pos_to_rect(tile_pos)
        alpha_rect(surface, rect, color=YELLOW, alpha=0.5)

    def display_player_wins(self, surface, x=None, y=None, font_size=55):
        if x is None:
            x = self.x_center
        if y is None:
            y = self.y + self.height / 2

        if self.winning == TILE_BLUE:
            text = "Blue wins!"
            color = LIGHT_BLUE
        else:
            text = "Red wins!"
            color = LIGHT_RED
        centered_text(surface, text, x, y, color, font_size=font_size)

    def display_move_counter(self, surface, x=None, y=None, font_size=45):
        if x is None:
            x = self.x_center
        if y is None:
            y = self.y / 2
        moves_left = 13 - (self.moves+1) // 2
        add_s = "" if moves_left == 1 else "s"
        text = f"{moves_left} Move{add_s} Left"
        centered_text(surface, text, x, y, font_size=font_size)

    def update(self, events, surface):
        self.tiles = self.board.to_array()
        self.new_game_text.update(events)

        mouse_down, mouse_up = events.mouse_down, events.mouse_up
        mouse_pos = events.mouse_pos
        x, y = self.mouse_pos_to_tile(mouse_pos)

        if mouse_down and Board.in_bounds(x, y) and (self.winning is None):
            self.select_tile(x, y)
        elif mouse_up and not (self.held_tile is None):
            self.release_tile(x, y)

        winning = self.board.is_winning()
        if winning == TILE_BLUE:
            self.winning = TILE_BLUE
        elif winning == TILE_RED:
            self.winning = TILE_RED
        elif 13-(self.moves+1)//2 <= 0:
            self.winning = TILE_RED

        if self.player in AI_PLAYER and self.winning is None:
            self.tiles = self.board.to_array()
            self.display(surface, events)
            pygame.display.flip()
            start = time.time()
            # Random first moves since they don't rly matter
            if self.moves == 0:
                move, score = random.choice(first_blue_move), 0
            elif self.moves == 1:
                if self.board.tiles[0][1] == 20:
                    move, score = [0, 6], 0
                else:
                    move, score = [4, 8], 0
            else:
                move, score = play(self.board, self.player == TILE_RED, self.moves, depth=DEPTHS[self.player])
            end = time.time()
            if self.player == TILE_BLUE:
                move[0] = self.board.tiles[0][move[0]]
            else:
                move[0] = self.board.tiles[1][move[0]]
            if wait-(end-start) > 0:
                time.sleep(wait-(end-start))
            if end-start < wait:
                time.sleep(wait-(end-start))
            print("depth:", DEPTHS[self.player], "time:", end-start, "eval:", round(score, 2))
            self.board.perform_move(self.player, move)
            self.tiles = self.board.to_array()
            self.switch_player()

        if not (self.winning is None):
            if mouse_down and self.new_game_text.is_hovered(events):
                self.new_game()

    def display_tile_on_mouse(self, surface, tile, mouse_pos):
        x, y = mouse_pos
        w, h = self.tile_filled_width, self.tile_filled_height
        rect = (x - w/2, y - h/2, w, h)

        if tile[0] == TILE_BLUE:
            pygame.draw.rect(surface, BLUE, rect)
        else:
            pygame.draw.rect(surface, RED, rect)

    def select_tile(self, x, y):
        tile = self.tiles[x][y]
        if tile == 0:
            return
        if tile != self.player:
            return
        self.held_tile = (tile, x, y)

    def release_tile(self, x, y):
        move = [self.held_tile[2]*Board.WIDTH+self.held_tile[1], y*Board.WIDTH+x]
        if move in self.board.get_valid_moves(TILE_BLUE) or move in self.board.get_valid_moves(TILE_RED):
            self.board.perform_move(self.player, move)
            self.switch_player()
        self.held_tile = None
