import math
import random
from board import Board

LOWERBOUND, EXACT, UPPERBOUND = -1, 0, 1
tile_row_vals_red = [1.0, 1.1, 1.05, 1.1, 1.0]
tile_row_vals_blue = [1.0, 1.1, 1.05, 1.1, 1.0]


def position_id(tiles):
    stiles = sorted(tiles)
    if not stiles:
        return 0
    s = stiles[0]
    n = s+0
    for tile in stiles[1:]:
        s *= 16
        s += (tile-n)
    return s


def position_id_both(tiles):
    id1 = position_id(tiles[0])
    id2 = position_id(tiles[1])
    return id1*1048576+id2


def clone_tiles(tiles):
    return tiles[0].copy(), tiles[1].copy()


# kind of unelegant but its fast
def get_valid_moves(tiles, maximizing_player):
    width = Board.WIDTH

    if maximizing_player:
        dirs = ((-1, width - 1), (0, width), (1, width + 1))
        player_tiles = tiles[1]
    else:
        dirs = ((-1, -width - 1), (0, -width), (1, -width + 1))
        player_tiles = tiles[0]

    valid_moves = []
    player_tile_set = set(player_tiles)
    for i, from_tile in enumerate(player_tiles):
        tile_x = from_tile % width
        for j, direction in dirs:
            x = tile_x + j
            if 0 <= x < width:
                to_tile = from_tile + direction
                # Tiles cannot be moved to other tiles of the same color
                if to_tile not in player_tile_set:
                    valid_moves.append([i, to_tile])
    return valid_moves


def random_move(tiles, maximizing_player):
    return random.choice(get_valid_moves(tiles, maximizing_player))


def perform_move(tiles, maximizing_player, move):
    from_i, to_tile = move

    if maximizing_player:
        tiles[1][from_i] = to_tile
        enemy_tiles = tiles[0]
    else:
        tiles[0][from_i] = to_tile
        enemy_tiles = tiles[1]

    if to_tile in enemy_tiles:
        enemy_tiles.remove(to_tile)


def is_winning(tiles):
    blue_tiles = tiles[0]
    red_tiles = tiles[1]

    if len(blue_tiles) == 0:
        return 2
    if len(red_tiles) == 0:
        return 1

    width = Board.WIDTH
    for tile in blue_tiles:
        if tile // width == 0:
            return 1

    height_1 = Board.HEIGHT - 1
    for tile in red_tiles:
        if tile // width == height_1:
            return 2

    return False


def evaluate_simple(tiles):
    return len(tiles[1])-len(tiles[0])


def evaluate(tiles):
    # higher score is better for red
    return sum(tile_row_vals_blue[t % 5] for t in tiles[1])-sum(tile_row_vals_red[t % 5] for t in tiles[0])


# TODO: refactor minimax function so it doesn't repeat everything twice
def minimax(tiles, depth, origDepth, alpha, beta, maximizing_player, moves, eval_func, tt):
    pos_id = position_id_both(tiles)
    lookup = tt.get(pos_id, None)
    if lookup is not None:
        flag, move, value, d = lookup
        if d == depth:
            if flag == EXACT:
                return move, value
            elif flag == LOWERBOUND:
                alpha = max(alpha, value)
            elif flag == UPPERBOUND:
                beta = min(beta, value)
            if alpha >= beta:
                return move, value

    winning = is_winning(tiles)
    if winning:
        if winning == 1:
            return None, -(27-moves)*10
        else:
            return None, (27-moves)*10

    if moves > 24:
        return None, (27-moves)*10

    if depth == 0:
        return None, eval_func(tiles)

    if moves >= 17 and depth != origDepth:
        for t in tiles[0]:
            if t // 5 > 12 - moves // 2:
                break
        else:
            if len(tiles[1]) > (26-moves) // 2:
                # blue can never reach the other side or take all enemy pieces in the moves left
                return None, 10

    if maximizing_player:
        valid_moves = get_valid_moves(tiles, True)
        random.shuffle(valid_moves)

        if depth > 1:
            moves_ = []
            for move in valid_moves:
                clone = clone_tiles(tiles)
                perform_move(clone, True, move)
                moves_.append([clone, move, eval_func(clone)])
            moves_.sort(key=lambda x: x[2], reverse=True)
        else:
            moves_ = valid_moves

        a = alpha
        best_move = valid_moves[0]
        max_eval = -math.inf
        for move_ in moves_:
            if depth > 1:
                clone, move, _ = move_
            else:
                move = move_
                clone = clone_tiles(tiles)
                perform_move(clone, True, move)

            current_eval = minimax(clone, depth - 1, origDepth, a, beta, False, moves+1, eval_func, tt)[1]
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            a = max(a, current_eval)
            if beta <= a:
                break

        tt[pos_id] = (UPPERBOUND if (max_eval <= alpha) else (LOWERBOUND if (max_eval >= beta) else EXACT), best_move, max_eval, depth)
        return best_move, max_eval

    else:
        valid_moves = get_valid_moves(tiles, False)
        if not moves:
            valid_moves = valid_moves[:7]
        random.shuffle(valid_moves)

        if depth > 1:
            moves_ = []
            for move in valid_moves:
                clone = clone_tiles(tiles)
                perform_move(clone, False, move)
                moves_.append([clone, move, eval_func(clone)])
            moves_.sort(key=lambda x: x[2], reverse=False)
        else:
            moves_ = valid_moves

        b = beta
        best_move = valid_moves[0]
        min_eval = math.inf
        for move_ in moves_:
            if depth > 1:
                clone, move, _ = move_
            else:
                move = move_
                clone = clone_tiles(tiles)
                perform_move(clone, False, move)

            current_eval = minimax(clone, depth - 1, origDepth, alpha, b, True, moves+1, eval_func, tt)[1]
            if current_eval < min_eval:
                min_eval = current_eval
                best_move = move
            b = min(b, current_eval)
            if b <= alpha:
                break
        tt[pos_id] = (UPPERBOUND if (min_eval <= alpha) else (LOWERBOUND if (min_eval >= beta) else EXACT), best_move, min_eval, depth)
        return best_move, min_eval


def play(board, maximizing_player, moves, depth):
    return minimax(board.tiles, depth, depth, -math.inf, math.inf, maximizing_player, moves, evaluate, {})