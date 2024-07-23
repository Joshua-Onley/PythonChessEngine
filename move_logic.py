import time

import numpy as np

import bit_manipulation
import globals
import precomputed_tables
from precomputed_tables import *
from debugging_functions import print_binary_as_bitboard
import itertools
import copy
from bit_manipulation import *
from precomputed_tables import BITBOARD_INDEX_TO_CHESS_SQUARE
from gui import display_draw, display_winner

COLOR_TO_INDEX = {'black': 0, 'white': 1}
empty_bitboard = np.uint64(0)


def calculate_knight_moves(index):
    knight_position_bitboard = np.uint64(1) << index

    # this mask will create a bitboard which has all 0s in columns A and B:
    # this will be used to avoid kight moves which can 'wrap around' to the wrong side of the board
    mask_col_AB = ~(COLUMNS[column['A']] | COLUMNS[column['B']])


    # mask for columns H and G
    mask_col_HG = ~(COLUMNS[column['H']] | COLUMNS[column['G']])

    # mask for column A
    mask_col_A = ~COLUMNS[column['A']]

    # mask for column H
    mask_col_H = ~(COLUMNS[column['H']])

    # move 1: 2 squares right, 1 square north
    move_1 = (knight_position_bitboard & mask_col_AB) << np.uint8(6) # if the knight is on column A or B move 1 is not possible

    # move 2: 2 squares north, 1 square right
    move_2 = (knight_position_bitboard & mask_col_A) << np.uint8(15) # move not possible if knight is on column A

    # move 3: 2 squares north, 1 square left
    move_3 = (knight_position_bitboard & mask_col_H) << np.uint8(17) # move is not possible if the knight is on column H

    # move 4: 2 squares left, 1 square north
    move_4 = (knight_position_bitboard & mask_col_HG) << np.uint8(10)

    # move_5: 2 squares left, 1 square south
    move_5 = (knight_position_bitboard & mask_col_HG) >> np.uint8(6)

    # move_6: 2 squares south, 1 square left
    move_6 = (knight_position_bitboard & mask_col_H) >> np.uint8(15)

    # move_7: 2 squares south, 1 square right
    move_7 = (knight_position_bitboard & mask_col_A) >> np.uint8(17)

    # move_8: 1 square south, 2 squares right
    move_8 = (knight_position_bitboard & mask_col_AB) >> np.uint8(10)

    knight_moves = move_1 | move_2 | move_3 | move_4 | move_5 | move_6 | move_7 | move_8

    return knight_moves


def generate_knight_moves(index, board, player_turn):
    white_pieces_bitboard = (board['white_pawn'] | board['white_knight'] |
                             board['white_bishop'] | board['white_rook'] |
                             board['white_queen'] | board['white_king'])

    black_pieces_bitboard = (board['black_pawn'] | board['black_knight'] |
                             board['black_bishop'] | board['black_rook'] |
                             board['black_queen'] | board['black_king'])

    if player_turn == 'white':
        return precomputed_tables.KNIGHT_MOVES[index] & ~white_pieces_bitboard

    elif player_turn == 'black':
        return precomputed_tables.KNIGHT_MOVES[index] & ~black_pieces_bitboard


def find_diagonal_moves(i, occupancy):
    col = i & np.uint8(7)
    occupancy = precomputed_tables.DIAGONAL_MASKS[i] & occupancy
    occupancy = (precomputed_tables.COLUMNS[0] * occupancy) >> np.uint8(56)
    occupancy = precomputed_tables.COLUMNS[0] * precomputed_tables.FIRST_ROW_MOVES[col][occupancy]
    return precomputed_tables.DIAGONAL_MASKS[i] & occupancy

def find_antidiagonal_moves(i, occupancy):
    col = i & np.uint8(7)
    occupancy = ANTIDIAGONAL_MASKS[i] & occupancy
    occupancy = (COLUMNS[0] * occupancy) >> np.uint8(56)
    occupancy = COLUMNS[0] * FIRST_ROW_MOVES[col][occupancy]
    return ANTIDIAGONAL_MASKS[i] & occupancy

def get_row_moves_bitboard(i, occupancy):
    col = i & np.uint8(7)
    occupancy = ROW_MASKS[i] & occupancy
    occupancy = (COLUMNS[0] * occupancy) >> np.uint8(56)
    occupancy = COLUMNS[0] * FIRST_ROW_MOVES[col][occupancy]
    result = ROW_MASKS[i] & occupancy
    return result

def get_column_moves_bitboard(i, occupancy):
    column_index = i & np.uint8(7)
    occupancy = COLUMNS[0] & (occupancy >> column_index)
    occupancy = (A1_to_H8_DIAGONAL_MASK * occupancy) >> np.uint8(56)
    first_rank_index = (i ^ np.uint8(56)) >> np.uint8(3)
    occupancy = A1_to_H8_DIAGONAL_MASK * FIRST_ROW_MOVES[first_rank_index][occupancy]
    result = (COLUMNS[7] & occupancy) >> (column_index ^ np.uint8(7))
    return result

def generate_bishop_moves(index, board, player_turn):
    all_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king'] | board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    diagonal_moves = find_diagonal_moves(index, all_pieces_bitboard)
    antidiagonal_moves = find_antidiagonal_moves(index, all_pieces_bitboard)


    if player_turn == 'white':
        return (diagonal_moves | antidiagonal_moves) & ~white_pieces_bitboard
    elif player_turn == 'black':
        return (diagonal_moves | antidiagonal_moves) & ~black_pieces_bitboard



def generate_rook_moves(index, board, player_turn):
    all_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king'] | board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    row_moves = get_row_moves_bitboard(index, all_pieces_bitboard)
    column_moves = get_column_moves_bitboard(index, all_pieces_bitboard)

    if player_turn == 'white':
        return (row_moves ^ column_moves) & ~white_pieces_bitboard
    elif player_turn == 'black':
        return (row_moves ^ column_moves) & ~black_pieces_bitboard


def compute_pawn_quiet_moves(index):
    # Shift forward function for moving bitboards
    def shift_forward(bb, color, shift):
        if globals.player_turn == 'white':
            return bb << (8 * shift)
        else:
            return bb >> (8 * shift)

    # Define starting ranks for white and black pawns
    white_starting_rank = 0x000000000000FF00  # Rank 2
    black_starting_rank = 0x00FF000000000000  # Rank 7

    # Convert index to a bitboard
    bb = 1 << index

    # Determine starting rank bitboard based on colour
    starting_rank = white_starting_rank if globals.player_turn == 'white' else black_starting_rank

    # Calculate single and double pawn moves
    single_move = shift_forward(bb, globals.player_turn, 1)
    double_move = shift_forward(bb & starting_rank, globals.player_turn, 2)

    return single_move | double_move

def generate_pawn_moves(index, board):
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']

    quiet_moves = compute_pawn_quiet_moves(index)
    potential_attacking_moves = compute_pawn_attack_moves(index)

    if globals.player_turn == 'white':
        valid_captures = potential_attacking_moves & black_pieces_bitboard
        valid_quiets = quiet_moves & ~black_pieces_bitboard
    else:
        valid_captures = potential_attacking_moves & white_pieces_bitboard
        valid_quiets = quiet_moves & ~white_pieces_bitboard

    return valid_quiets | valid_captures

def generate_king_moves_bitboard(index, board, WKHM, BKHM, WK, WQ, BK, BQ, player_turn):
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']

    castling_moves = get_castling_options(board, player_turn, WKHM, BKHM, WK, WQ, BK, BQ)

    if player_turn == 'white':
        return (precomputed_tables.KING_MOVES[index] & ~white_pieces_bitboard) | castling_moves
    elif player_turn == 'black':
        return (precomputed_tables.KING_MOVES[index] &~black_pieces_bitboard) | castling_moves



def compute_pawn_attack_moves(index):

    # Convert index to a bitboard
    bb = np.uint64(1 << index)

    # Define file masks for A and H files to handle edge cases
    file_a_mask = np.uint64(0x7F7F7F7F7F7F7F7F)  # Masks to clear A file for left attacks
    file_h_mask = np.uint64(0xFEFEFEFEFEFEFEFE)  # Masks to clear H file for right attacks

    if globals.player_turn == 'white':
        # Calculate the attacks for white pawns
        left_attack = (bb & file_h_mask) << np.uint8(7)
        right_attack = (bb & file_a_mask) << np.uint8(9)

    else:
        # Calculate the attacks for black pawns
        left_attack = (bb & file_h_mask) >> np.uint8(9)
        right_attack = (bb & file_a_mask) >> np.uint8(7)

    return left_attack | right_attack



def calculate_king_moves(index, board):

    if globals.player_turn == 'white':
        return precomputed_tables.KING_MOVES[index] & ~(board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | board['white_queen'] | board['white_king'])
    elif globals.player_turn == 'black':
        return precomputed_tables.KING_MOVES[index] & ~(board['black_pawn'] | board['black_knight'] | board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king'])


def generate_pawn_moves_bitboard(index, board, player_turn, game_states):
    all_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king'] | board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    if player_turn == 'white':
        attacks = precomputed_tables.PAWN_ATTACKS[1][index] & black_pieces_bitboard
        if len(game_states) >= 4:
            en_passants = is_en_passant_legal(board, player_turn, game_states)
        else:
            en_passants = np.uint64(0)
        quiets = empty_bitboard
        white_free = to_bitboard(index + np.uint8(8)) & all_pieces_bitboard == empty_bitboard
        if (player_turn == 'white' and white_free):
            quiets = precomputed_tables.PAWN_QUIETS[0][index] & ~all_pieces_bitboard

    elif player_turn == 'black':
        attacks = precomputed_tables.PAWN_ATTACKS[0][index] & white_pieces_bitboard
        if len(game_states) > 3:
            en_passants = is_en_passant_legal(board, player_turn, game_states)
        else:
            en_passants = np.uint64(0)
        quiets = empty_bitboard
        black_free = to_bitboard(index - np.uint8(8)) & all_pieces_bitboard == empty_bitboard

        if (player_turn == 'black' and black_free):
            quiets = precomputed_tables.PAWN_QUIETS[1][index] & ~all_pieces_bitboard

    return attacks | quiets | en_passants

def is_en_passant_legal(board, player_turn, game_states):
    #for boards in game_states:
        #print('black pawns: ')
        #print_binary_as_bitboard(boards['black_pawn'])
        #print('white pawns: ')
        #print_binary_as_bitboard(boards['white_pawn'])


    if player_turn == 'white':
        current_black_pawn_state = board['black_pawn']
        #print('current_black_pawn_state: ')
        #print_binary_as_bitboard(current_black_pawn_state)
        #print('\n')
        previous_black_pawn_state = game_states[-1]['black_pawn']
        #print('previous_black_pawn_state: ')
        #print_binary_as_bitboard(previous_black_pawn_state)
        if current_black_pawn_state != previous_black_pawn_state:
            start_square = previous_black_pawn_state & ~current_black_pawn_state
            end_square = ~previous_black_pawn_state & current_black_pawn_state
            if (start_square >> 16) & end_square:
                if (end_square >> 1) & board['white_pawn'] or (end_square << 1) & board['white_pawn']:
                    print('en passant is possible ##############################################################')
                    return end_square << 8

    if player_turn == 'black':
        current_white_pawn_state = board['white_pawn']
        #print('current white pawn state: ')
        #print_binary_as_bitboard(current_white_pawn_state)
        #print('\n')
        previous_white_pawn_state = game_states[-1]['white_pawn']
        #print('previous whit pawn state: ')
        #print_binary_as_bitboard(previous_white_pawn_state)
        #print('\n')

        if current_white_pawn_state != previous_white_pawn_state:
            start_square = previous_white_pawn_state & ~current_white_pawn_state
            #print('start square')
            #print_binary_as_bitboard(start_square)
            #print('\n')
            end_square = ~previous_white_pawn_state & current_white_pawn_state
            #print('end square: ')
            #print_binary_as_bitboard(end_square)
            #print('\n')
            if (start_square << 16) & end_square:
                if (end_square << 1) & board['black_pawn'] or (end_square >> 1) & board['black_pawn']:
                    print('en passant is possible ##############')
                    return end_square >> 8
    return np.uint64(0)


def get_castling_options(board, player_turn, WKHM, BKHM, WQ, WK, BQ, BK):
    all_pieces_bitboard = (
            board['white_pawn'] | board['white_knight'] | board['white_bishop'] |
            board['white_rook'] | board['white_queen'] | board['white_king'] |
            board['black_pawn'] | board['black_knight'] | board['black_bishop'] |
            board['black_rook'] | board['black_queen'] | board['black_king']
    )

    castling_options = np.uint64(0)

    if player_turn == 'white':
        # White Kingside Castling
        if not (np.uint64(1) << 5 & all_pieces_bitboard) and not (np.uint64(1) << 6 & all_pieces_bitboard):
            if not is_square_attacked(4, board, 'white') and not is_square_attacked(5, board,
                                                                                     'white') and not is_square_attacked(
                    6, board, 'white') and not WKHM and not WK:
                castling_options |= np.uint64(1) << 6
        # White Queenside Castling
        if not (np.uint64(1) << 1 & all_pieces_bitboard) and not (np.uint64(1) << 2 & all_pieces_bitboard) and not (
                np.uint64(1) << 3 & all_pieces_bitboard):
            if not is_square_attacked(2, board, 'white') and not is_square_attacked(3, board,
                                                                                     'white') and not is_square_attacked(
                    4, board, 'white') and not WKHM and not WQ:
                castling_options |= np.uint64(1) << 2

    elif player_turn == 'black':
        # Black Kingside Castling
        if not (np.uint64(1) << 62 & all_pieces_bitboard) and not (np.uint64(1) << 61 & all_pieces_bitboard):
            if not is_square_attacked(60, board, 'black') and not is_square_attacked(61, board,
                                                                                    'black') and not is_square_attacked(
                    62, board, 'black') and not BKHM and not BK:
                castling_options |= np.uint64(1) << 62
        # Black Queenside Castling
        if not (np.uint64(1) << 57 & all_pieces_bitboard) and not (np.uint64(1) << 58 & all_pieces_bitboard) and not (
                np.uint64(1) << 59 & all_pieces_bitboard):
            if not is_square_attacked(60, board, 'black') and not is_square_attacked(59, board,
                                                                                    'black') and not is_square_attacked(
                    58, board, 'black') and not BKHM and not BQ:
                castling_options |= np.uint64(1) << 58

    return castling_options


def simulate_move(piece, start_index, end_index, piece_bitboards, all_pieces_bitboard, player_turn, white_pieces_bitboard, black_pieces_bitboard):
    from main import determine_what_piece_has_been_selected

    target_piece = determine_what_piece_has_been_selected(end_index, piece_bitboards)

    if piece == 'white_pawn' and (start_index == end_index - 9 or start_index == end_index - 7) and not (all_pieces_bitboard >> end_index) & 1:
        piece_bitboards['white_pawn'] = clear_square(piece_bitboards['white_pawn'], start_index)
        piece_bitboards['white_pawn'] = set_square(piece_bitboards['white_pawn'], end_index)
        piece_bitboards['black_pawn'] = clear_square(piece_bitboards['black_pawn'], end_index - 8)

    elif piece == 'white_pawn' and 56 <= end_index <= 63:
        piece_bitboards['white_pawn'] = clear_square(piece_bitboards['white_pawn'], start_index)
        piece_bitboards['white_queen'] = set_square(piece_bitboards['white_queen'], end_index)

    elif piece == 'black_pawn' and (start_index == end_index + 9 or start_index == end_index + 7) and not (all_pieces_bitboard >> end_index) & 1:
        piece_bitboards['black_pawn'] = clear_square(piece_bitboards['black_pawn'], start_index)
        piece_bitboards['black_pawn'] = set_square(piece_bitboards['black_pawn'], end_index)
        piece_bitboards['white_pawn'] = clear_square(piece_bitboards['white_pawn'], end_index + 8)

    elif piece == 'black_pawn' and 0 <= end_index <= 7:
        piece_bitboards['black_pawn'] = clear_square(piece_bitboards['black_pawn'], start_index)
        piece_bitboards['black_queen'] = set_square(piece_bitboards['black_queen'], end_index)

    elif piece == 'white_king' and start_index == 3 and end_index == 1:
        piece_bitboards['white_king'] = clear_square(piece_bitboards['white_king'], start_index)
        piece_bitboards['white_king'] = set_square(piece_bitboards['white_king'], end_index)
        piece_bitboards['white_rook'] = clear_square(piece_bitboards['white_rook'], 0)
        piece_bitboards['white_rook'] = set_square(piece_bitboards['white_rook'], 2)
        white_king_has_moved = True

    elif piece == 'white_king' and start_index == 3 and end_index == 5:
        piece_bitboards['white_king'] = clear_square(piece_bitboards['white_king'], start_index)
        piece_bitboards['white_king'] = set_square(piece_bitboards['white_king'], end_index)
        piece_bitboards['white_rook'] = clear_square(piece_bitboards['white_rook'], 7)
        piece_bitboards['white_rook'] = set_square(piece_bitboards['white_rook'], 4)
        white_king_has_moved = True

    elif piece == 'black_king' and start_index == 59 and end_index == 61:
        piece_bitboards['black_king'] = clear_square(piece_bitboards['black_king'], start_index)
        piece_bitboards['black_king'] = set_square(piece_bitboards['black_king'], end_index)
        piece_bitboards['black_rook'] = clear_square(piece_bitboards['black_rook'], 63)
        piece_bitboards['black_rook'] = set_square(piece_bitboards['black_rook'], 60)
        black_king_has_moved = True

    elif piece == 'black_king' and start_index == 59 and end_index == 57:
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 56)
        globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 58)
        black_king_has_moved = True

    elif piece == 'white_king':
        piece_bitboards['white_king'] = clear_square(piece_bitboards['white_king'], start_index)
        piece_bitboards['white_king'] = set_square(piece_bitboards['white_king'], end_index)
        white_king_has_moved = True

    elif piece == 'black_king':
        piece_bitboards['black_king'] = clear_square(piece_bitboards['black_king'], start_index)
        piece_bitboards['black_king'] = set_square(piece_bitboards['black_king'], end_index)
        black_king_has_moved = True

    elif piece == 'white_rook' and start_index == 0:
        piece_bitboards[piece] = clear_square(piece_bitboards[piece], start_index)
        piece_bitboards[piece] = set_square(piece_bitboards[piece], end_index)
        white_kingside_rook_has_moved = True

    elif piece == 'white_rook' and start_index == 7:
        piece_bitboards[piece] = clear_square(piece_bitboards[piece], start_index)
        piece_bitboards[piece] = set_square(piece_bitboards[piece], end_index)
        white_queenside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 63:
        piece_bitboards[piece] = clear_square(piece_bitboards[piece], start_index)
        piece_bitboards[piece] = set_square(piece_bitboards[piece], end_index)
        black_queenside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 56:
        piece_bitboards[piece] = clear_square(piece_bitboards[piece], start_index)
        piece_bitboards[piece] = set_square(piece_bitboards[piece], end_index)
        black_kingside_rook_has_moved = True


    else:
        piece_bitboards[piece] = clear_square(piece_bitboards[piece], start_index)
        piece_bitboards[piece] = set_square(piece_bitboards[piece], end_index)

    all_pieces_bitboard = clear_square(all_pieces_bitboard, start_index)
    all_pieces_bitboard = set_square(all_pieces_bitboard, end_index)

    if piece.startswith('white'):
        white_pieces_bitboard = clear_square(white_pieces_bitboard, start_index)
        white_pieces_bitboard = set_square(white_pieces_bitboard, end_index)
    else:
        black_pieces_bitboard = clear_square(black_pieces_bitboard, start_index)
        black_pieces_bitboard = set_square(black_pieces_bitboard, end_index)

    if target_piece:
        piece_bitboards[target_piece] = clear_square(piece_bitboards[target_piece], end_index)


    return all_pieces_bitboard, white_pieces_bitboard, black_pieces_bitboard, piece_bitboards

def get_queen_moves(square, board, player_turn):
    return generate_rook_moves(square, board, player_turn) | generate_bishop_moves(square, board, player_turn)

def results_in_check(piece, start_index, end_index, board, player_turn):
    white_pieces_bitboard = board['white_pawn'] | board['white_knight'] | board['white_bishop'] | board['white_rook'] | \
                          board['white_queen'] | board['white_king']
    black_pieces_bitboard = board['black_pawn'] | board['black_knight'] | \
                          board['black_bishop'] | board['black_rook'] | board['black_queen'] | board['black_king']
    all_pieces_bitboard = white_pieces_bitboard | black_pieces_bitboard

    board_copy = copy.deepcopy(board)
    white_pieces_bitboard_copy = copy.deepcopy(white_pieces_bitboard)
    black_pieces_bitboard_copy = copy.deepcopy(black_pieces_bitboard)
    all_pieces_bitboard_copy = copy.deepcopy(all_pieces_bitboard)
    player_turn_copy = copy.deepcopy(player_turn)

    result = simulate_move(piece, start_index, end_index, board_copy, all_pieces_bitboard_copy, player_turn_copy, white_pieces_bitboard_copy, black_pieces_bitboard_copy)
    all_pieces_bitboard, white_pieces_bitboard, black_pieces_bitboard, piece_bitboards = result
    player_index = COLOR_TO_INDEX[player_turn]
    opponent_colour = 'white' if player_turn == 'black' else 'black'
    king_square_index = find_msb_index(piece_bitboards[f'{player_turn}_king'])

    opponent_pawn_bitboard = piece_bitboards[f'{opponent_colour}_pawn']
    if (precomputed_tables.PAWN_ATTACKS[player_index][king_square_index] & opponent_pawn_bitboard) != empty_bitboard:
        return True

    opponent_knight_bitboard = piece_bitboards[f'{opponent_colour}_knight']
    if (generate_knight_moves(king_square_index, piece_bitboards, player_turn) & opponent_knight_bitboard) != empty_bitboard:
        return True

    opponent_king_bitboard = piece_bitboards[f'{opponent_colour}_king']
    if (calculate_king_moves(king_square_index, piece_bitboards) & opponent_king_bitboard) != empty_bitboard:
        return True

    opponent_bishops_bitboard = piece_bitboards[f'{opponent_colour}_bishop']
    opponent_queens_bitboard = piece_bitboards[f'{opponent_colour}_queen']
    if (generate_bishop_moves(king_square_index, piece_bitboards, player_turn) & (opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    opponent_rooks_bitboard = piece_bitboards[f'{opponent_colour}_rook']
    if (generate_rook_moves(king_square_index, piece_bitboards, player_turn) & (opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    return False

def is_square_attacked(square_index, board, player_turn):

    player_index = COLOR_TO_INDEX[player_turn]

    # opp_color = ~board.color
    opponent_colour = 'white' if player_turn == 'black' else 'black'

    # opp_pawns = board.get_piece_bb(Piece.PAWN, color=opp_color)
    opponent_pawn_bitboard = board[f'{opponent_colour}_pawn']
    if (precomputed_tables.PAWN_ATTACKS[player_index][square_index] & opponent_pawn_bitboard) != empty_bitboard:
        return True

    # opp_knights = board.get_piece_bb(Piece.KNIGHT, color=opp_color)
    opponent_knight_bitboard = board[f'{opponent_colour}_knight']
    if (generate_knight_moves(square_index, board, player_turn) & opponent_knight_bitboard) != empty_bitboard:
        return True

    # opp_king = board.get_piece_bb(Piece.KING, color=opp_color)
    opponent_king_bitboard = board[f'{opponent_colour}_king']
    if (calculate_king_moves(square_index, board) & opponent_king_bitboard) != empty_bitboard:
        return True

    # opp_bishops = board.get_piece_bb(Piece.BISHOP, color=opp_color)
    opponent_bishops_bitboard = board[f'{opponent_colour}_bishop']
    opponent_queens_bitboard = board[f'{opponent_colour}_queen']
    if (generate_bishop_moves(square_index, board, player_turn) & (
            opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    opponent_rooks_bitboard = board[f'{opponent_colour}_rook']
    if (generate_rook_moves(square_index, board, player_turn) & (
            opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    return False

def gen_piece_moves(starting_square, piece):
    colour = globals.player_turn
    moves = []
    if piece == 'white_pawn' or piece == 'black_pawn':
        moves_bitboard = generate_pawn_moves_bitboard(starting_square, globals.piece_bitboards, colour, globals.game_states)
    elif piece == 'white_knight' or piece == 'black_knight':
        moves_bitboard = generate_knight_moves(starting_square, globals.piece_bitboards, colour)
    elif piece == 'white_bishop' or piece == 'black_bishop':
        moves_bitboard = generate_bishop_moves(starting_square, globals.piece_bitboards, colour)
    elif piece == 'white_rook' or piece == 'black_rook':
        moves_bitboard = generate_rook_moves(starting_square, globals.piece_bitboards, colour)
    elif piece == 'white_queen' or piece == 'black_queen':
        moves_bitboard = get_queen_moves(starting_square, globals.piece_bitboards, colour)
    elif piece == 'white_king' or piece == 'black_king':
        moves_bitboard = generate_king_moves_bitboard(starting_square, globals.piece_bitboards, globals.white_king_has_moved, globals.black_king_has_moved, globals.white_kingside_rook_has_moved, globals.white_queenside_rook_has_moved, globals.black_kingside_rook_has_moved, globals.black_queenside_rook_has_moved, colour)

    while moves_bitboard != empty_bitboard:
        end_index = find_lsb_index(moves_bitboard)
        start_index = starting_square
        moves.append([piece, start_index, end_index])
        moves_bitboard &= moves_bitboard - 1

    return moves


def find_all_moves():
    all_moves = []
    if globals.player_turn == 'white':
        for piece in ['white_pawn', 'white_knight', 'white_bishop', 'white_rook', 'white_queen', 'white_king']:
            piece_bitboard = globals.piece_bitboards[piece]
            for starting_square in bit_manipulation.occupied_squares(piece_bitboard):
                moves = gen_piece_moves(starting_square, piece)
                all_moves.extend(moves)
    elif globals.player_turn == 'black':
        for piece in ['black_pawn', 'black_knight', 'black_bishop', 'black_rook', 'black_queen', 'black_king']:
            piece_bitboard = globals.piece_bitboards[piece]
            for starting_square in bit_manipulation.occupied_squares(piece_bitboard):
                moves = gen_piece_moves(starting_square, piece)
                all_moves.extend(moves)
    return all_moves


def gen_legal_moves():
    opponent_colour = 'white' if globals.player_turn == 'black' else 'black'
    opponent_bitboard = (globals.piece_bitboards[f'{opponent_colour}_pawn'] |
                         globals.piece_bitboards[f'{opponent_colour}_knight'] |
                         globals.piece_bitboards[f'{opponent_colour}_bishop'] |
                         globals.piece_bitboards[f'{opponent_colour}_rook'] |
                         globals.piece_bitboards[f'{opponent_colour}_queen'] |
                         globals.piece_bitboards[f'{opponent_colour}_king'])
    attacking_moves = []
    non_attacking_moves = []
    all_moves = find_all_moves()
    for move in all_moves:
        piece, starting_square, target_square = move[0], move[1], move[2]
        if not results_in_check(piece, starting_square, target_square, globals.piece_bitboards, globals.player_turn):
            if np.uint64(1) << target_square & opponent_bitboard:
                attacking_moves.append(move)
            else:
                non_attacking_moves.append(move)
    return attacking_moves, non_attacking_moves


def checkmate(winner):
    display_winner(winner)
    time.sleep(10)


