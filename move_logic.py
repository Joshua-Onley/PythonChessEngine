import time
import bit_manipulation
import globals
import precomputed_tables
from precomputed_tables import *
from bit_manipulation import *
from gui import display_draw, display_winner
from globals import save_global_state, restore_global_state
from utils import determine_what_piece_has_been_selected
from debugging_functions import print_binary_as_chessboard

COLOR_TO_INDEX = {'black': 0, 'white': 1}
empty_bitboard = np.uint64(0)


def generate_knight_moves(index):
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return precomputed_tables.KNIGHT_MOVES[index] & ~pieces_bitboard


def find_diagonal_moves(i, occupancy):
    col = i & 7
    masked_occupancy = precomputed_tables.DIAGONAL_MASKS[i] & occupancy
    shift_val = (precomputed_tables.COLUMNS[0] * masked_occupancy) >> 56
    occupancy = precomputed_tables.COLUMNS[0] * precomputed_tables.FIRST_ROW_MOVES[col][shift_val]
    return precomputed_tables.DIAGONAL_MASKS[i] & occupancy

def find_antidiagonal_moves(i, occupancy):
    col = i & 7
    masked_occupancy = precomputed_tables.ANTIDIAGONAL_MASKS[i] & occupancy
    shift_val = (precomputed_tables.COLUMNS[0] * masked_occupancy) >> 56
    occupancy = precomputed_tables.COLUMNS[0] * precomputed_tables.FIRST_ROW_MOVES[col][shift_val]
    return precomputed_tables.ANTIDIAGONAL_MASKS[i] & occupancy

def get_row_moves_bitboard(i, occupancy):
    col = i & 7
    masked_occupancy = precomputed_tables.ROW_MASKS[i] & occupancy
    shift_val = (precomputed_tables.COLUMNS[0] * masked_occupancy) >> 56
    occupancy = precomputed_tables.COLUMNS[0] * precomputed_tables.FIRST_ROW_MOVES[col][shift_val]
    return precomputed_tables.ROW_MASKS[i] & occupancy

def get_column_moves_bitboard(i, occupancy):
    col_index = i & 7
    masked_occupancy = precomputed_tables.COLUMNS[0] & (occupancy >> col_index)
    shift_val = (precomputed_tables.A1_to_H8_DIAGONAL_MASK * masked_occupancy) >> 56
    first_rank_index = (i ^ 56) >> 3
    occupancy = precomputed_tables.A1_to_H8_DIAGONAL_MASK * precomputed_tables.FIRST_ROW_MOVES[first_rank_index][shift_val]
    return (precomputed_tables.COLUMNS[7] & occupancy) >> (col_index ^ 7)

def generate_bishop_moves(index):
    diag_moves = find_diagonal_moves(index, globals.all_pieces_bitboard)
    antidiag_moves = find_antidiagonal_moves(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (diag_moves | antidiag_moves) & ~pieces_bitboard



def generate_rook_moves(index):
    row_moves = get_row_moves_bitboard(index, globals.all_pieces_bitboard)
    col_moves = get_column_moves_bitboard(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (row_moves ^ col_moves) & ~pieces_bitboard



def compute_pawn_quiet_moves(index):
    bb = 1 << index
    white_starting_rank = 0x000000000000FF00
    black_starting_rank = 0x00FF000000000000
    starting_rank = white_starting_rank if globals.player_turn == 'white' else black_starting_rank
    single_move = bb << 8 if globals.player_turn == 'white' else bb >> 8
    double_move = (bb & starting_rank) << 16 if globals.player_turn == 'white' else (bb & starting_rank) >> 16
    return single_move | double_move

def generate_pawn_moves(index):
    quiet_moves = compute_pawn_quiet_moves(index)
    attacking_moves = compute_pawn_attack_moves(index)
    if globals.player_turn == 'white':
        valid_captures = attacking_moves & globals.black_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.black_pieces_bitboard
    else:
        valid_captures = attacking_moves & globals.white_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.white_pieces_bitboard
    return valid_quiets | valid_captures

def generate_king_moves_bitboard(index):
    castling_moves = get_castling_options()
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (precomputed_tables.KING_MOVES[index] & ~pieces_bitboard) | castling_moves




def compute_pawn_attack_moves(index):
    bb = np.uint64(1 << index)
    file_a_mask = np.uint64(0x7F7F7F7F7F7F7F7F)
    file_h_mask = np.uint64(0xFEFEFEFEFEFEFEFE)
    if globals.player_turn == 'white':
        left_attack = (bb & file_h_mask) << np.uint8(7)
        right_attack = (bb & file_a_mask) << np.uint8(9)
    else:
        left_attack = (bb & file_h_mask) >> np.uint8(9)
        right_attack = (bb & file_a_mask) >> np.uint8(7)

    return left_attack | right_attack


def calculate_king_moves(index):
    if globals.player_turn == 'white':
        return precomputed_tables.KING_MOVES[index] & ~(globals.white_pieces_bitboard)
    elif globals.player_turn == 'black':
        return precomputed_tables.KING_MOVES[index] & ~(globals.black_pieces_bitboard)


def generate_pawn_moves_bitboard(index):
    player_index = COLOR_TO_INDEX[globals.player_turn]
    opponent_colour = 'white' if globals.player_turn == 'black' else 'black'
    if globals.player_turn == 'white':
        attacks = precomputed_tables.PAWN_ATTACKS[1][index] & globals.black_pieces_bitboard
        en_passants = is_en_passant_legal() if len(globals.game_states) >= 4 else np.uint64(0)
        white_free = to_bitboard(index + 8) & globals.all_pieces_bitboard == empty_bitboard
        quiets = precomputed_tables.PAWN_QUIETS[0][index] & ~globals.all_pieces_bitboard if white_free else empty_bitboard
    else:
        attacks = precomputed_tables.PAWN_ATTACKS[0][index] & globals.white_pieces_bitboard
        en_passants = is_en_passant_legal() if len(globals.game_states) > 3 else np.uint64(0)
        black_free = to_bitboard(index - 8) & globals.all_pieces_bitboard == empty_bitboard
        quiets = precomputed_tables.PAWN_QUIETS[1][index] & ~globals.all_pieces_bitboard if black_free else empty_bitboard
    return attacks | quiets | en_passants

import numpy as np


def is_en_passant_legal():
    COL_A_MASK = 0xFEFEFEFEFEFEFEFE
    COL_H_MASK = 0x7F7F7F7F7F7F7F7F

    if globals.player_turn == 'white':
        current_black_pawn_state = globals.game_states[-1]['black_pawn']
        previous_black_pawn_state = globals.game_states[-2]['black_pawn']

        if current_black_pawn_state != previous_black_pawn_state:
            start_square = previous_black_pawn_state & ~current_black_pawn_state
            end_square = ~previous_black_pawn_state & current_black_pawn_state

            if (start_square >> 16) & end_square:
                # Apply column masks before checking for adjacent white pawns
                masked_end_square_left = (end_square & COL_A_MASK) >> 1
                masked_end_square_right = (end_square & COL_H_MASK) << 1

                if (masked_end_square_left & globals.piece_bitboards['white_pawn']) or (
                        masked_end_square_right & globals.piece_bitboards['white_pawn']):

                    return end_square << 8

    elif globals.player_turn == 'black':
        current_white_pawn_state = globals.game_states[-1]['white_pawn']
        previous_white_pawn_state = globals.game_states[-2]['white_pawn']

        if current_white_pawn_state != previous_white_pawn_state:
            start_square = previous_white_pawn_state & ~current_white_pawn_state
            end_square = ~previous_white_pawn_state & current_white_pawn_state

            if (start_square << 16) & end_square:
                masked_end_square_left = (end_square & COL_A_MASK) >> 1
                masked_end_square_right = (end_square & COL_H_MASK) << 1

                if (masked_end_square_left & globals.piece_bitboards['black_pawn']) or (
                        masked_end_square_right & globals.piece_bitboards['black_pawn']):

                    return end_square >> 8

    return np.uint64(0)


def get_castling_options():
    castling_options = np.uint64(0)
    if globals.player_turn == 'white':
        # White Kingside Castling
        if not (np.uint64(1) << 5 & globals.all_pieces_bitboard) and not (np.uint64(1) << 6 & globals.all_pieces_bitboard):
            if not is_square_attacked(4, globals.piece_bitboards, 'white') and not is_square_attacked(5, globals.piece_bitboards,
                                                                                     'white') and not is_square_attacked(
                    6, globals.piece_bitboards, 'white') and not globals.white_king_has_moved and not globals.white_kingside_rook_has_moved:
                castling_options |= np.uint64(1) << 6
        # White Queenside Castling
        if not (np.uint64(1) << 1 & globals.all_pieces_bitboard) and not (np.uint64(1) << 2 & globals.all_pieces_bitboard) and not (
                np.uint64(1) << 3 & globals.all_pieces_bitboard):
            if not is_square_attacked(2, globals.piece_bitboards, 'white') and not is_square_attacked(3, globals.piece_bitboards,
                                                                                     'white') and not is_square_attacked(
                    4, globals.piece_bitboards, 'white') and not globals.white_king_has_moved and not globals.white_queenside_rook_has_moved:
                castling_options |= np.uint64(1) << 2

    elif globals.player_turn == 'black':
        # Black Kingside Castling
        if not (np.uint64(1) << 62 & globals.all_pieces_bitboard) and not (np.uint64(1) << 61 & globals.all_pieces_bitboard):
            if not is_square_attacked(60, globals.piece_bitboards, 'black') and not is_square_attacked(61, globals.piece_bitboards,
                                                                                    'black') and not is_square_attacked(
                    62, globals.piece_bitboards, 'black') and not globals.black_king_has_moved and not globals.black_kingside_rook_has_moved:
                castling_options |= np.uint64(1) << 62
        # Black Queenside Castling
        if not (np.uint64(1) << 57 & globals.all_pieces_bitboard) and not (np.uint64(1) << 58 & globals.all_pieces_bitboard) and not (
                np.uint64(1) << 59 & globals.all_pieces_bitboard):
            if not is_square_attacked(60, globals.piece_bitboards, 'black') and not is_square_attacked(59, globals.piece_bitboards,
                                                                                    'black') and not is_square_attacked(
                    58, globals.piece_bitboards, 'black') and not globals.black_king_has_moved and not globals.black_queenside_rook_has_moved:
                castling_options |= np.uint64(1) << 58

    return castling_options


def make_move(piece, start_index, end_index):

    target_piece = determine_what_piece_has_been_selected(end_index, globals.piece_bitboards)

    if piece == 'white_pawn' and (start_index == end_index - 9 or start_index == end_index - 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], start_index)
        globals.piece_bitboards['white_pawn'] = set_square(globals.piece_bitboards['white_pawn'], end_index)
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], end_index - 8)

    elif piece == 'white_pawn' and 56 <= end_index <= 63:
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], start_index)
        globals.piece_bitboards['white_queen'] = set_square(globals.piece_bitboards['white_queen'], end_index)

    elif piece == 'black_pawn' and (start_index == end_index + 9 or start_index == end_index + 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], start_index)
        globals.piece_bitboards['black_pawn'] = set_square(globals.piece_bitboards['black_pawn'], end_index)
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], end_index + 8)

    elif piece == 'black_pawn' and 0 <= end_index <= 7:
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], start_index)
        globals.piece_bitboards['black_queen'] = set_square(globals.piece_bitboards['black_queen'], end_index)

    elif piece == 'white_king' and start_index == 4 and end_index == 6:
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 7)
        globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 5)
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 7)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 5)
        globals.white_king_has_moved = True

    elif piece == 'white_king' and start_index == 4 and end_index == 2:
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 0)
        globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 3)
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 0)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 3)
        globals.white_king_has_moved = True

    elif piece == 'black_king' and start_index == 60 and end_index == 62:
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 63)
        globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 61)
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 63)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 61)
        globals.black_king_has_moved = True

    elif piece == 'black_king' and start_index == 60 and end_index == 58:
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 56)
        globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 59)
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 56)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 59)
        globals.black_king_has_moved = True

    elif piece == 'white_king':
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.white_king_has_moved = True

    elif piece == 'black_king':
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.black_king_has_moved = True

    elif piece == 'white_rook' and start_index == 0:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.white_queenside_rook_has_moved = True

    elif piece == 'white_rook' and start_index == 7:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.white_kingside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 63:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.black_kingside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 56:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.black_queenside_rook_has_moved = True


    else:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)

    globals.all_pieces_bitboard = clear_square(globals.all_pieces_bitboard, start_index)
    globals.all_pieces_bitboard = set_square(globals.all_pieces_bitboard, end_index)

    if piece.startswith('white'):
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, start_index)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, end_index)
    else:
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, start_index)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, end_index)

    if target_piece:
        globals.piece_bitboards[target_piece] = clear_square(globals.piece_bitboards[target_piece], end_index)
        if target_piece.startswith('white'):
            globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, end_index)
        elif target_piece.startswith('black'):
            globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, end_index)

    globals.game_states.append(globals.piece_bitboards)




def get_queen_moves(square):
    return generate_rook_moves(square) | generate_bishop_moves(square)

def results_in_check(piece, start_index, end_index):

    saved_state = save_global_state()
    make_move(piece, start_index, end_index)

    player_index = COLOR_TO_INDEX[globals.player_turn]
    opponent_colour = 'white' if globals.player_turn == 'black' else 'black'
    king_square_index = find_msb_index(globals.piece_bitboards[f'{globals.player_turn}_king'])

    opponent_pawn_bitboard = globals.piece_bitboards[f'{opponent_colour}_pawn']
    if (precomputed_tables.PAWN_ATTACKS[player_index][king_square_index] & opponent_pawn_bitboard) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_knight_bitboard = globals.piece_bitboards[f'{opponent_colour}_knight']
    if (generate_knight_moves(king_square_index) & opponent_knight_bitboard) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_king_bitboard = globals.piece_bitboards[f'{opponent_colour}_king']
    if (calculate_king_moves(king_square_index) & opponent_king_bitboard) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_bishops_bitboard = globals.piece_bitboards[f'{opponent_colour}_bishop']
    opponent_queens_bitboard = globals.piece_bitboards[f'{opponent_colour}_queen']
    if (generate_bishop_moves(king_square_index) & (opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_rooks_bitboard = globals.piece_bitboards[f'{opponent_colour}_rook']
    if (generate_rook_moves(king_square_index) & (opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    restore_global_state(saved_state)

    return False

def is_square_attacked(square_index, board, player_turn):
    player_index = COLOR_TO_INDEX[player_turn]
    opponent_color = 'white' if player_turn == 'black' else 'black'

    # Retrieve opponent piece bitboards
    opponent_pawn_bitboard = board[f'{opponent_color}_pawn']
    opponent_knight_bitboard = board[f'{opponent_color}_knight']
    opponent_king_bitboard = board[f'{opponent_color}_king']
    opponent_bishops_bitboard = board[f'{opponent_color}_bishop']
    opponent_rooks_bitboard = board[f'{opponent_color}_rook']
    opponent_queens_bitboard = board[f'{opponent_color}_queen']

    # Check if the square is attacked by opponent's pawns
    if (precomputed_tables.PAWN_ATTACKS[player_index][square_index] & opponent_pawn_bitboard) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's knights
    knight_moves = generate_knight_moves(square_index)
    if (knight_moves & opponent_knight_bitboard) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's kings
    king_moves = calculate_king_moves(square_index)
    if (king_moves & opponent_king_bitboard) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's bishops or queens
    bishop_moves = generate_bishop_moves(square_index)
    queen_moves = generate_rook_moves(square_index)  # Note: Assuming rook and queen moves are separate
    if (bishop_moves & (opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's rooks or queens
    if (queen_moves & (opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    return False


def gen_piece_moves(starting_square, piece):
    move_generators = {
        'pawn': generate_pawn_moves_bitboard,
        'knight': generate_knight_moves,
        'bishop': generate_bishop_moves,
        'rook': generate_rook_moves,
        'queen': get_queen_moves,
        'king': generate_king_moves_bitboard,
    }
    moves_bitboard = move_generators[piece.split('_')[1]](starting_square)
    moves = []
    while moves_bitboard != empty_bitboard:
        end_index = find_lsb_index(moves_bitboard)
        moves.append([piece, starting_square, end_index])
        moves_bitboard &= moves_bitboard - 1
    return moves

def find_all_moves():
    all_moves = []
    player_pieces = [piece for piece in globals.piece_bitboards if piece.startswith(globals.player_turn)]
    for piece in player_pieces:
        piece_bitboard = globals.piece_bitboards[piece]
        for starting_square in bit_manipulation.occupied_squares(piece_bitboard):
            moves = gen_piece_moves(starting_square, piece)
            all_moves.extend(moves)
    return all_moves


def gen_legal_moves():
    opponent_colour = 'white' if globals.player_turn == 'black' else 'black'
    opponent_bitboard = globals.black_pieces_bitboard if opponent_colour == 'black' else globals.white_pieces_bitboard
    attacking_moves = []
    non_attacking_moves = []
    legal_moves = []
    all_moves = find_all_moves()

    for move in all_moves:
        piece, starting_square, target_square = move
        if not results_in_check(piece, starting_square, target_square):
            if (np.uint64(1) << target_square) & opponent_bitboard:
                attacking_moves.append(move)
            else:
                non_attacking_moves.append(move)
    return attacking_moves, non_attacking_moves


def checkmate(winner):
    display_winner(winner)
    time.sleep(10)


