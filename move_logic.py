import time
import bit_manipulation
import globals
import precomputed_tables
from precomputed_tables import *
from bit_manipulation import *
from gui import display_draw, display_winner
from globals import save_global_state, restore_global_state, switch_player_turn
from utils import determine_what_piece_has_been_selected
from debugging_functions import print_binary_as_chessboard
import bit_manipulation

COLOR_TO_INDEX = {'black': 0, 'white': 1}
empty_bitboard = np.uint64(0)


def generate_knight_moves_list(index):
    '''

    :param index:
    :return:
    '''
    moves = []
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    end_squares = bit_manipulation.extract_set_bits(KNIGHT_MOVES[index] & ~pieces_bitboard)
    for square in end_squares:
        if not results_in_check(f'{globals.player_turn}_knight', index, square):
            moves.append([f'{globals.player_turn}_knight', index, square])
    return moves

def generate_knight_moves_bitboard(index):
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return KNIGHT_MOVES[index] & ~pieces_bitboard

def find_diagonal_moves(i, occupancy):
    col = i & 7
    masked_occupancy = DIAGONAL_MASKS[i] & occupancy
    shift_val = (COLUMNS[0] * masked_occupancy) >> 56
    occupancy = COLUMNS[0] * FIRST_ROW_MOVES[col][shift_val]
    return DIAGONAL_MASKS[i] & occupancy

def find_antidiagonal_moves(i, occupancy):
    col = i & 7
    masked_occupancy = ANTIDIAGONAL_MASKS[i] & occupancy
    shift_val = (COLUMNS[0] * masked_occupancy) >> 56
    occupancy = COLUMNS[0] * FIRST_ROW_MOVES[col][shift_val]
    return ANTIDIAGONAL_MASKS[i] & occupancy

def get_row_moves_bitboard(i, occupancy):
    col = i & 7
    masked_occupancy = ROW_MASKS[i] & occupancy
    shift_val = (COLUMNS[0] * masked_occupancy) >> 56
    occupancy = COLUMNS[0] * FIRST_ROW_MOVES[col][shift_val]
    return ROW_MASKS[i] & occupancy

def get_column_moves_bitboard(i, occupancy):
    col_index = i & 7
    masked_occupancy = precomputed_tables.COLUMNS[0] & (occupancy >> col_index)
    shift_val = (precomputed_tables.A1_to_H8_DIAGONAL_MASK * masked_occupancy) >> 56
    first_rank_index = (i ^ 56) >> 3
    occupancy = precomputed_tables.A1_to_H8_DIAGONAL_MASK * precomputed_tables.FIRST_ROW_MOVES[first_rank_index][shift_val]
    return (precomputed_tables.COLUMNS[7] & occupancy) >> (col_index ^ 7)

def generate_bishop_moves_list(index):
    moves = []
    diag_moves = find_diagonal_moves(index, globals.all_pieces_bitboard)
    antidiag_moves = find_antidiagonal_moves(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    end_squares = extract_set_bits((diag_moves | antidiag_moves) & ~pieces_bitboard)
    for square in end_squares:
        if not results_in_check(f'{globals.player_turn}_bishop', index, square):
            moves.append([f'{globals.player_turn}_bishop', index, square])
    return moves

def generate_bishop_moves_bitboard(index):
    diag_moves = find_diagonal_moves(index, globals.all_pieces_bitboard)
    antidiag_moves = find_antidiagonal_moves(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (diag_moves | antidiag_moves) & ~pieces_bitboard

def generate_queen_moves_list(index):
    moves = []
    diag_moves = find_diagonal_moves(index, globals.all_pieces_bitboard)
    antidiag_moves = find_antidiagonal_moves(index, globals.all_pieces_bitboard)
    row_moves = get_row_moves_bitboard(index, globals.all_pieces_bitboard)
    col_moves = get_column_moves_bitboard(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    end_squares = bit_manipulation.extract_set_bits((diag_moves | antidiag_moves | row_moves | col_moves) & ~pieces_bitboard)
    for square in end_squares:
        if not results_in_check(f'{globals.player_turn}_queen', index, square):
            moves.append([f'{globals.player_turn}_queen', index, square])
    return moves



def generate_rook_moves_list(index):
    moves = []
    row_moves = get_row_moves_bitboard(index, globals.all_pieces_bitboard)
    col_moves = get_column_moves_bitboard(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    end_squares = extract_set_bits((row_moves | col_moves) & ~pieces_bitboard)
    for square in end_squares:
        if not results_in_check(f'{globals.player_turn}_rook', index, square):
            moves.append([f'{globals.player_turn}_rook', index, square])
    return moves

def generate_rook_moves_bitboard(index):
    row_moves = get_row_moves_bitboard(index, globals.all_pieces_bitboard)
    col_moves = get_column_moves_bitboard(index, globals.all_pieces_bitboard)
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (row_moves | col_moves) & ~pieces_bitboard


def compute_pawn_quiet_moves(index):
    bb = np.uint64(1 << index)
    starting_rank = 0x000000000000FF00 if globals.player_turn == 'white' else 0x00FF000000000000
    single_move = bb << 8 if globals.player_turn == 'white' else bb >> 8
    double_move = (bb & starting_rank) << 16 if globals.player_turn == 'white' else (bb & starting_rank) >> 16
    white_clear_path = (to_bitboard(index + np.uint(8)) & globals.all_pieces_bitboard) == empty_bitboard
    black_clear_path = (to_bitboard(index - np.uint(8)) & globals.all_pieces_bitboard) == empty_bitboard
    if (globals.player_turn == 'white' and white_clear_path) or (globals.player_turn == 'black' and black_clear_path):
        return single_move | double_move
    return single_move | np.uint64(0)


def generate_king_moves_list(index):
    moves = []
    castling_moves = get_castling_options()
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    end_squares = extract_set_bits((precomputed_tables.KING_MOVES[index] & ~pieces_bitboard) | castling_moves)
    for square in end_squares:
        if not results_in_check(f'{globals.player_turn}_king', index, square):
            moves.append([f'{globals.player_turn}_king', index, square])
    return moves

def generate_king_moves_bitboard(index):
    castling_moves = get_castling_options()
    pieces_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'white' else globals.black_pieces_bitboard
    return (precomputed_tables.KING_MOVES[index] & ~pieces_bitboard) | castling_moves



def calculate_king_moves(index):
    if globals.player_turn == 'white':
        return precomputed_tables.KING_MOVES[index] & ~(globals.white_pieces_bitboard)
    elif globals.player_turn == 'black':
        return precomputed_tables.KING_MOVES[index] & ~(globals.black_pieces_bitboard)


def generate_pawn_moves_list(index):
    piece = 'white_pawn' if globals.player_turn == 'white' else 'black_pawn'
    moves = []
    if globals.player_turn == 'white':
        quiet_moves = compute_pawn_quiet_moves(index)
        attacking_moves = PAWN_ATTACKS[1][index]
        valid_captures = attacking_moves & globals.black_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.all_pieces_bitboard
    else:
        quiet_moves = compute_pawn_quiet_moves(index)
        attacking_moves = PAWN_ATTACKS[0][index]
        valid_captures = attacking_moves & globals.white_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.all_pieces_bitboard

    end_squares = extract_set_bits(valid_quiets | valid_captures)
    for square in end_squares:
        if not results_in_check(piece, index, square):
            move = (piece, index, square)
            moves.append(move)
    return moves


def is_en_passant_legal():
    if len(globals.game_states) < 3:
        return []
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

                if (masked_end_square_left & globals.piece_bitboards['white_pawn']):
                    return [f'{globals.player_turn}_pawn', int(find_msb_index(end_square)) - 1, int(find_msb_index(end_square)) + 8]
                elif (masked_end_square_right & globals.piece_bitboards['white_pawn']):
                    return [f'{globals.player_turn}_pawn', int(find_msb_index(end_square)) + 1, int(find_msb_index(end_square)) + 8]

    elif globals.player_turn == 'black':
        current_white_pawn_state = globals.game_states[-1]['white_pawn']
        previous_white_pawn_state = globals.game_states[-2]['white_pawn']

        if current_white_pawn_state != previous_white_pawn_state:
            start_square = previous_white_pawn_state & ~current_white_pawn_state
            end_square = ~previous_white_pawn_state & current_white_pawn_state

            if (start_square << 16) & end_square:
                masked_end_square_left = (end_square & COL_A_MASK) >> 1
                masked_end_square_right = (end_square & COL_H_MASK) << 1

                if (masked_end_square_left & globals.piece_bitboards['black_pawn']):
                    return [f'{globals.player_turn}_pawn', int(find_msb_index(end_square)) - 1, int(find_msb_index(end_square)) - 8]

                elif (masked_end_square_right & globals.piece_bitboards['black_pawn']):
                    return [f'{globals.player_turn}_pawn', int(find_msb_index(end_square)) + 1,
                            int(find_msb_index(end_square)) -8]

    return False


def get_castling_options():
    castling_options = np.uint64(0)
    if globals.player_turn == 'white':
        if not (np.uint64(1) << 5 & globals.all_pieces_bitboard) and not (np.uint64(1) << 6 & globals.all_pieces_bitboard):
            if not is_square_attacked(4, globals.piece_bitboards, 'white') and not is_square_attacked(5, globals.piece_bitboards, 'white') and not is_square_attacked(6, globals.piece_bitboards, 'white') and not globals.white_king_has_moved and not globals.white_kingside_rook_has_moved:
                castling_options |= np.uint64(1) << 6
        if not (np.uint64(1) << 1 & globals.all_pieces_bitboard) and not (np.uint64(1) << 2 & globals.all_pieces_bitboard) and not (np.uint64(1) << 3 & globals.all_pieces_bitboard):
            if not is_square_attacked(2, globals.piece_bitboards, 'white') and not is_square_attacked(3, globals.piece_bitboards, 'white') and not is_square_attacked(4, globals.piece_bitboards, 'white') and not globals.white_king_has_moved and not globals.white_queenside_rook_has_moved:
                castling_options |= np.uint64(1) << 2

    elif globals.player_turn == 'black':
        if not (np.uint64(1) << 62 & globals.all_pieces_bitboard) and not (np.uint64(1) << 61 & globals.all_pieces_bitboard):
            if not is_square_attacked(60, globals.piece_bitboards, 'black') and not is_square_attacked(61, globals.piece_bitboards, 'black') and not is_square_attacked(62, globals.piece_bitboards, 'black') and not globals.black_king_has_moved and not globals.black_kingside_rook_has_moved:
                castling_options |= np.uint64(1) << 62
        if not (np.uint64(1) << 57 & globals.all_pieces_bitboard) and not (np.uint64(1) << 58 & globals.all_pieces_bitboard) and not (np.uint64(1) << 59 & globals.all_pieces_bitboard):
            if not is_square_attacked(57, globals.piece_bitboards, 'black') and not is_square_attacked(58, globals.piece_bitboards, 'black') and not is_square_attacked(59, globals.piece_bitboards, 'black') and not globals.black_king_has_moved and not globals.black_queenside_rook_has_moved:
                castling_options |= np.uint64(1) << 58

    return castling_options


def make_move(piece, start_index, end_index):
        target_piece = determine_what_piece_has_been_selected(end_index, globals.piece_bitboards)

        if piece[6:] == 'pawn':
            if piece.startswith('white'):
                if (start_index == end_index - 9 or start_index == end_index - 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
                    globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'],
                                                                         start_index)
                    globals.piece_bitboards['white_pawn'] = set_square(globals.piece_bitboards['white_pawn'], end_index)
                    globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'],
                                                                         end_index - 8)
                    globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, end_index - 8)
                    globals.all_pieces_bitboard = clear_square(globals.all_pieces_bitboard, end_index - 8)
                elif 56 <= end_index <= 63:
                    globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'],
                                                                         start_index)
                    globals.piece_bitboards['white_queen'] = set_square(globals.piece_bitboards['white_queen'],
                                                                        end_index)
                else:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
            else:
                if (start_index == end_index + 9 or start_index == end_index + 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
                    globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'],
                                                                         start_index)
                    globals.piece_bitboards['black_pawn'] = set_square(globals.piece_bitboards['black_pawn'], end_index)
                    globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'],
                                                                         end_index + 8)
                    globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, end_index + 8)
                    globals.all_pieces_bitboard = clear_square(globals.all_pieces_bitboard, end_index + 8)
                elif 0 <= end_index <= 7:
                    globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'],
                                                                         start_index)
                    globals.piece_bitboards['black_queen'] = set_square(globals.piece_bitboards['black_queen'],
                                                                        end_index)
                else:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)

        elif piece[6:] == 'king':
            if piece.startswith('white'):
                if start_index == 4 and end_index == 6:
                    globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'],
                                                                         start_index)
                    globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
                    globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 7)
                    globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 5)
                    globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 7)
                    globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 5)
                    globals.white_king_has_moved = True

                elif start_index == 4 and end_index == 2:
                    globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'],
                                                                         start_index)
                    globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
                    globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 0)
                    globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 3)
                    globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 0)
                    globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 3)
                    globals.white_king_has_moved = True

                else:
                    globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'],
                                                                         start_index)
                    globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
                    globals.white_king_has_moved = True


            else:
                if start_index == 60 and end_index == 62:
                    globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'],
                                                                         start_index)
                    globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
                    globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 63)
                    globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 61)
                    globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 63)
                    globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 61)
                    globals.black_king_has_moved = True

                elif start_index == 60 and end_index == 58:
                    globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'],
                                                                         start_index)
                    globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
                    globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 56)
                    globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 59)
                    globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 56)
                    globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 59)
                    globals.black_king_has_moved = True

                else:
                    globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'],
                                                                         start_index)
                    globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
                    globals.black_king_has_moved = True

        elif piece[6:] == 'rook':
            if piece.startswith('white'):
                if start_index == 0:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
                    globals.white_queenside_rook_has_moved = True
                elif start_index == 7:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
                    globals.white_kingside_rook_has_moved = True
                else:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
            else:
                if start_index == 63:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
                    globals.black_kingside_rook_has_moved = True

                elif start_index == 56:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
                    globals.black_queenside_rook_has_moved = True
                else:
                    globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
                    globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
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
    if (generate_knight_moves_bitboard(king_square_index) & opponent_knight_bitboard) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_king_bitboard = globals.piece_bitboards[f'{opponent_colour}_king']
    if (calculate_king_moves(king_square_index) & opponent_king_bitboard) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_bishops_bitboard = globals.piece_bitboards[f'{opponent_colour}_bishop']
    opponent_queens_bitboard = globals.piece_bitboards[f'{opponent_colour}_queen']
    if (generate_bishop_moves_bitboard(king_square_index) & (opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        restore_global_state(saved_state)
        return True

    opponent_rooks_bitboard = globals.piece_bitboards[f'{opponent_colour}_rook']
    if (generate_rook_moves_bitboard(king_square_index) & (opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
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
    knight_moves = generate_knight_moves_bitboard(square_index)
    if (knight_moves & opponent_knight_bitboard) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's kings
    king_moves = calculate_king_moves(square_index)
    if (king_moves & opponent_king_bitboard) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's bishops or queens
    bishop_moves = generate_bishop_moves_bitboard(square_index)
    queen_moves = generate_rook_moves_bitboard(square_index)  # Note: Assuming rook and queen moves are separate
    if (bishop_moves & (opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    # Check if the square is attacked by opponent's rooks or queens
    if (queen_moves & (opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    return False



def gen_legal_moves():
    all_moves = []
    captures = []
    checks = []
    non_captures = []

    if is_en_passant_legal():
        captures.append(is_en_passant_legal())
    for piece_type in [f'{globals.player_turn}_pawn', f'{globals.player_turn}_knight', f'{globals.player_turn}_bishop', f'{globals.player_turn}_rook', f'{globals.player_turn}_queen', f'{globals.player_turn}_king']:
        for index in extract_set_bits(globals.piece_bitboards[piece_type]):
            if 'pawn' in piece_type:
                all_moves.extend(generate_pawn_moves_list(index))
            elif 'knight' in piece_type:
                all_moves.extend(generate_knight_moves_list(index))
            elif 'bishop' in piece_type:
                all_moves.extend(generate_bishop_moves_list(index))
            elif 'rook' in piece_type:
                all_moves.extend(generate_rook_moves_list(index))
            elif 'queen' in piece_type:
                all_moves.extend(generate_queen_moves_list(index))
            elif 'king' in piece_type:
                all_moves.extend(generate_king_moves_list(index))


    opponent_bitboard = globals.white_pieces_bitboard if globals.player_turn == 'black' else globals.black_pieces_bitboard

    for move in all_moves:
        piece, starting_square, target_square = move
        switch_player_turn()
        if results_in_check(piece, starting_square, target_square):
            checks.append(move)
            switch_player_turn()
            continue
        else:
            switch_player_turn()

        if (np.uint64(1) << target_square) & opponent_bitboard:
            captures.append(move)
        else:
            non_captures.append(move)
    return checks, captures, non_captures


def checkmate(winner):
    display_winner(winner)
    time.sleep(10)


