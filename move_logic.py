import time
import bit_manipulation
import precomputed_tables
from precomputed_tables import *
from bit_manipulation import *
from gui import display_draw, display_winner
from globals import save_global_state, restore_global_state

COLOR_TO_INDEX = {'black': 0, 'white': 1}
empty_bitboard = np.uint64(0)


def generate_knight_moves(index):
    if globals.player_turn == 'white':
        return precomputed_tables.KNIGHT_MOVES[index] & ~globals.white_pieces_bitboard
    elif globals.player_turn == 'black':
        return precomputed_tables.KNIGHT_MOVES[index] & ~globals.black_pieces_bitboard


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

def generate_bishop_moves(index):

    diagonal_moves = find_diagonal_moves(index, globals.all_pieces_bitboard)
    antidiagonal_moves = find_antidiagonal_moves(index, globals.all_pieces_bitboard)
    if globals.player_turn == 'white':
        return (diagonal_moves | antidiagonal_moves) & ~globals.white_pieces_bitboard
    elif globals.player_turn == 'black':
        return (diagonal_moves | antidiagonal_moves) & ~globals.black_pieces_bitboard



def generate_rook_moves(index):

    row_moves = get_row_moves_bitboard(index, globals.all_pieces_bitboard)
    column_moves = get_column_moves_bitboard(index, globals.all_pieces_bitboard)
    if globals.player_turn == 'white':
        return (row_moves ^ column_moves) & ~globals.white_pieces_bitboard
    elif globals.player_turn == 'black':
        return (row_moves ^ column_moves) & ~globals.black_pieces_bitboard


def compute_pawn_quiet_moves(index):
    def shift_forward(bb, color, shift):
        if globals.player_turn == 'white':
            return bb << (8 * shift)
        else:
            return bb >> (8 * shift)

    white_starting_rank = 0x000000000000FF00  # Rank 2
    black_starting_rank = 0x00FF000000000000  # Rank 7
    bb = 1 << index
    starting_rank = white_starting_rank if globals.player_turn == 'white' else black_starting_rank
    single_move = shift_forward(bb, globals.player_turn, 1)
    double_move = shift_forward(bb & starting_rank, globals.player_turn, 2)

    return single_move | double_move

def generate_pawn_moves(index):

    quiet_moves = compute_pawn_quiet_moves(index)
    potential_attacking_moves = compute_pawn_attack_moves(index)

    if globals.player_turn == 'white':
        valid_captures = potential_attacking_moves & globals.black_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.black_pieces_bitboard
    else:
        valid_captures = potential_attacking_moves & globals.white_pieces_bitboard
        valid_quiets = quiet_moves & ~globals.white_pieces_bitboard

    return valid_quiets | valid_captures

def generate_king_moves_bitboard(index):

    castling_moves = get_castling_options()
    if globals.player_turn == 'white':
        return (precomputed_tables.KING_MOVES[index] & ~globals.white_pieces_bitboard) | castling_moves
    elif globals.player_turn == 'black':
        return (precomputed_tables.KING_MOVES[index] &~globals.black_pieces_bitboard) | castling_moves



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
    if globals.player_turn == 'white':
        attacks = precomputed_tables.PAWN_ATTACKS[1][index] & globals.black_pieces_bitboard
        if len(globals.game_states) >= 4:
            en_passants = is_en_passant_legal()
        else:
            en_passants = np.uint64(0)
        quiets = empty_bitboard
        white_free = to_bitboard(index + np.uint8(8)) & globals.all_pieces_bitboard == empty_bitboard
        if globals.player_turn == 'white' and white_free:
            quiets = precomputed_tables.PAWN_QUIETS[0][index] & ~globals.all_pieces_bitboard

    elif globals.player_turn == 'black':
        attacks = precomputed_tables.PAWN_ATTACKS[0][index] & globals.white_pieces_bitboard
        if len(globals.game_states) > 3:
            en_passants = is_en_passant_legal()
        else:
            en_passants = np.uint64(0)
        quiets = empty_bitboard
        black_free = to_bitboard(index - np.uint8(8)) & globals.all_pieces_bitboard == empty_bitboard

        if globals.player_turn == 'black' and black_free:
            quiets = precomputed_tables.PAWN_QUIETS[1][index] & ~globals.all_pieces_bitboard

    return attacks | quiets | en_passants

def is_en_passant_legal():
    #for boards in game_states:
        #print('black pawns: ')
        #print_binary_as_bitboard(boards['black_pawn'])
        #print('white pawns: ')
        #print_binary_as_bitboard(boards['white_pawn'])


    if globals.player_turn == 'white':
        current_black_pawn_state = globals.piece_bitboards['black_pawn']
        #print('current_black_pawn_state: ')
        #print_binary_as_bitboard(current_black_pawn_state)
        #print('\n')
        previous_black_pawn_state = globals.game_states[-1]['black_pawn']
        #print('previous_black_pawn_state: ')
        #print_binary_as_bitboard(previous_black_pawn_state)
        if current_black_pawn_state != previous_black_pawn_state:
            start_square = previous_black_pawn_state & ~current_black_pawn_state
            end_square = ~previous_black_pawn_state & current_black_pawn_state
            if (start_square >> 16) & end_square:
                if (end_square >> 1) & globals.piece_bitboards['white_pawn'] or (end_square << 1) & globals.piece_bitboards['white_pawn']:
                    print('en passant is possible ##############################################################')
                    return end_square << 8

    if globals.player_turn == 'black':
        current_white_pawn_state = globals.piece_bitboards['white_pawn']
        #print('current white pawn state: ')
        #print_binary_as_bitboard(current_white_pawn_state)
        #print('\n')
        previous_white_pawn_state = globals.game_states[-1]['white_pawn']
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
                if (end_square << 1) & globals.piece_bitboards['black_pawn'] or (end_square >> 1) & globals.piece_bitboards['black_pawn']:
                    print('en passant is possible ##############')
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


def simulate_move(piece, start_index, end_index):
    from main import determine_what_piece_has_been_selected

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
    simulate_move(piece, start_index, end_index)

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

    # opp_color = ~board.color
    opponent_colour = 'white' if player_turn == 'black' else 'black'

    # opp_pawns = board.get_piece_bb(Piece.PAWN, color=opp_color)
    opponent_pawn_bitboard = board[f'{opponent_colour}_pawn']
    if (precomputed_tables.PAWN_ATTACKS[player_index][square_index] & opponent_pawn_bitboard) != empty_bitboard:
        return True

    # opp_knights = board.get_piece_bb(Piece.KNIGHT, color=opp_color)
    opponent_knight_bitboard = board[f'{opponent_colour}_knight']
    if (generate_knight_moves(square_index) & opponent_knight_bitboard) != empty_bitboard:
        return True

    # opp_king = board.get_piece_bb(Piece.KING, color=opp_color)
    opponent_king_bitboard = board[f'{opponent_colour}_king']
    if (calculate_king_moves(square_index) & opponent_king_bitboard) != empty_bitboard:
        return True

    # opp_bishops = board.get_piece_bb(Piece.BISHOP, color=opp_color)
    opponent_bishops_bitboard = board[f'{opponent_colour}_bishop']
    opponent_queens_bitboard = board[f'{opponent_colour}_queen']
    if (generate_bishop_moves(square_index) & (
            opponent_bishops_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    opponent_rooks_bitboard = board[f'{opponent_colour}_rook']
    if (generate_rook_moves(square_index) & (
            opponent_rooks_bitboard | opponent_queens_bitboard)) != empty_bitboard:
        return True

    return False

def gen_piece_moves(starting_square, piece):
    colour = globals.player_turn
    moves = []
    if piece == 'white_pawn' or piece == 'black_pawn':
        moves_bitboard = generate_pawn_moves_bitboard(starting_square)
    elif piece == 'white_knight' or piece == 'black_knight':
        moves_bitboard = generate_knight_moves(starting_square)
    elif piece == 'white_bishop' or piece == 'black_bishop':
        moves_bitboard = generate_bishop_moves(starting_square)
    elif piece == 'white_rook' or piece == 'black_rook':
        moves_bitboard = generate_rook_moves(starting_square)
    elif piece == 'white_queen' or piece == 'black_queen':
        moves_bitboard = get_queen_moves(starting_square)
    elif piece == 'white_king' or piece == 'black_king':
        moves_bitboard = generate_king_moves_bitboard(starting_square)

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
    opponent_bitboard = globals.black_pieces_bitboard if opponent_colour == 'black' else globals.white_pieces_bitboard
    attacking_moves = []
    non_attacking_moves = []
    all_moves = find_all_moves()
    for move in all_moves:
        piece, starting_square, target_square = move[0], move[1], move[2]
        if not results_in_check(piece, starting_square, target_square):
            if np.uint64(1) << target_square & opponent_bitboard:
                attacking_moves.append(move)
            else:
                non_attacking_moves.append(move)
    return attacking_moves, non_attacking_moves


def checkmate(winner):
    display_winner(winner)
    time.sleep(10)


