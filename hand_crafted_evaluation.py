from bit_manipulation import retrieve_occupied_squares, occupied_squares, pop_count
from precomputed_tables import FRONT_SPANS, neighbor_columns, KING_FRONT_SPANS, ADJACENT_SQUARES, PAWN_ATTACKS
from move_logic import generate_bishop_moves, generate_rook_moves, generate_knight_moves, gen_legal_moves
from debugging_functions import print_binary_as_bitboard
import numpy as np


def calculate_bishop_mobility_bonus(board):
    white_bonus = np.int64(0)
    black_bonus = np.int64(0)

    # calculate white bishop mobility bonus
    white_bishop_indexes = occupied_squares(board['white_bishop'])
    for index in white_bishop_indexes:
        moves_bitboard = generate_bishop_moves(index)
        white_bonus += pop_count(moves_bitboard) * 4

    # calculate black bishop mobility bonus
    black_bishop_indexes = occupied_squares(board['black_bishop'])
    for index in black_bishop_indexes:
        moves_bitboard = generate_bishop_moves(index)
        black_bonus += pop_count(moves_bitboard) * 4

    return white_bonus, black_bonus


def calculate_knight_bonuses(board):
    white_bonus = np.int64(0)
    black_bonus = np.int64(0)

    def mobility_bonus(knight_index, board, player_turn):
        bonus = 0
        moves_bitboard = generate_knight_moves(knight_index)
        bonus += pop_count(moves_bitboard) * 5
        return bonus

    def outpost_square_bonus(knight_index, is_white, friendly_pawn_bitboard, opp_pawn_bitboard):
        opponent_colour_index = 1 if is_white else 0
        colour_index = 0 if is_white else 1

        if (PAWN_ATTACKS[opponent_colour_index][knight_index] & friendly_pawn_bitboard) and (FRONT_SPANS[colour_index][knight_index] & opp_pawn_bitboard) == 0:
            return 9
        return 0


    white_knight_indexes = occupied_squares(board['white_knight'])
    black_knight_indexes = occupied_squares(board['black_knight'])

    for index in white_knight_indexes:
        white_bonus += mobility_bonus(index, board, 'white')
        white_bonus += outpost_square_bonus(index, True, board['white_pawn'], board['black_pawn'])

    for index in black_knight_indexes:
        black_bonus += mobility_bonus(index, board, 'black')
        black_bonus += outpost_square_bonus(index, False, board['black_pawn'], board['white_pawn'])

    return white_bonus, black_bonus


def calculate_rook_bonuses(board, white_pieces, black_pieces, all_pieces_bitboard):
    white_bonus = 0
    black_bonus = 0

    def are_rooks_connected(rook_positions, all_pieces_bitboard):
        if len(rook_positions) != 2:
            return False
        rook1, rook2 = rook_positions
        same_rank = rook1 // 8 == rook2 // 8
        same_file = rook1 % 8 == rook2 % 8
        if same_rank:
            min_file = min(rook1 % 8, rook2 % 8)
            max_file = max(rook1 % 8, rook2 % 8)
            for file in range(min_file + 1, max_file):
                if (np.uint64(1) << (rook1 // 8 * 8 + file)) & all_pieces_bitboard:
                    return False
            return True
        if same_file:
            min_rank = min(rook1 // 8, rook2 // 8)
            max_rank = max(rook1 // 8, rook2 // 8)
            for rank in range(min_rank + 1, max_rank):
                if (np.uint64(1) << (rank * 8 + rook1 % 8)) & all_pieces_bitboard:
                    return False
            return True
        return False

    def rook_on_open_file(rook_index, friendly_pawns_bitboard):

        column = rook_index % 8
        for row in range(8):
            square_index = row * 8 + column
            if (np.uint64(1) << square_index) & friendly_pawns_bitboard:
                return False
        return True

    def rook_on_king_file(rook_index, opponent_king):
        column = rook_index % 8
        for row in range(8):
            square_index = row * 8 + column
            if (np.uint64(1) << square_index) & opponent_king:
                return True
        return False

    def rook_on_7th(rook_index, colour):
        if colour == 'white' and 48 <= rook_index < 56:
            return True
        elif colour == 'black' and 8 <= rook_index < 16:
            return True
        return False

    def rook_mobility_bonus(index, board, player_turn):
        bonus = 0

        moves_bitboard = generate_rook_moves(index)
        bonus += pop_count(moves_bitboard) * 4
        number_of_moves = pop_count(moves_bitboard)
        return bonus

    def rook_attack_king_adj_file(index, opp_king_bitboard):
        return (neighbor_columns[index] & opp_king_bitboard) != 0


    white_rooks_bitboard = board['white_rook']
    white_rook_indexes = list(occupied_squares(white_rooks_bitboard))
    black_rooks_bitboard = board['black_rook']
    black_rook_indexes = list(occupied_squares(black_rooks_bitboard))

    if are_rooks_connected(white_rook_indexes, all_pieces_bitboard):
        white_bonus += 6

    if are_rooks_connected(black_rook_indexes, all_pieces_bitboard):
        black_bonus += 6

    for index in white_rook_indexes:
        white_bonus += rook_mobility_bonus(index, board, 'white')
        if rook_on_open_file(index, board['white_pawn']):
            white_bonus += 27
        if rook_on_king_file(index, board['black_king']):
            white_bonus += 51
        if rook_on_7th(index, 'white'):
            white_bonus += 30
        if rook_attack_king_adj_file(index, board['black_king']):
            white_bonus += 8

    for index in black_rook_indexes:
        black_bonus += rook_mobility_bonus(index, board, 'black')
        if rook_on_open_file(index, board['black_pawn']):
            black_bonus += 27
        if rook_on_king_file(index, board['white_king']):
            black_bonus += 51
        if rook_on_7th(index, 'black'):
            black_bonus += 30
        if rook_attack_king_adj_file(index, board['white_king']):
            black_bonus += 8

    return white_bonus, black_bonus

def calculate_pawn_bonuses(board, white_pieces, black_pieces, all_pieces_bitboard):
    white_bonus = np.int64(0)
    black_bonus = np.int64(0)

    def doubled_pawns(index, pawns_bitboard):
        file_mask = np.uint64(0x0101010101010101) << (index % 8)
        pawns_in_file = pawns_bitboard & file_mask
        pawn_count = pop_count(pawns_in_file)
        return pawn_count > 1

    def advance_bonus(index, colour):
        rank = index // 8
        if colour == 'white':
            return (rank - 1) * 3
        elif colour == 'black':
            return (6 - rank) * 3
        return 0

    def is_passed_pawn(square, is_white, opponent_pawn_bitboard):
        colour_index = 0 if is_white else 1
        return (FRONT_SPANS[colour_index][square] & opponent_pawn_bitboard) == 0

    def is_isolated_pawn(square, friendly_pawn_bitboard):
        return (neighbor_columns[square] & friendly_pawn_bitboard) == 0

    white_pawns_bitboard = board['white_pawn']
    black_pawns_bitboard = board['black_pawn']

    white_pawn_indexes = list(occupied_squares(white_pawns_bitboard))
    black_pawn_indexes = list(occupied_squares(black_pawns_bitboard))

    for index in white_pawn_indexes:
        pawn_advance_bonus = advance_bonus(index, 'white')
        white_bonus += advance_bonus(index, 'white')

        if doubled_pawns(index, white_pawns_bitboard):
            white_bonus -= 7

        if is_passed_pawn(index, True, black_pawns_bitboard):
            white_bonus += 10

        if is_isolated_pawn(index, white_pawns_bitboard):
            white_bonus -= 8


    for index in black_pawn_indexes:
        black_pawn_advance_bonus = advance_bonus(index, 'black')
        black_bonus += advance_bonus(index, 'black')

        if doubled_pawns(index, black_pawns_bitboard):
            black_bonus -= 7

        if is_passed_pawn(index, False, white_pawns_bitboard):
            black_bonus += 10

        if is_isolated_pawn(index, black_pawns_bitboard):
            black_bonus -= 8

    return white_bonus, black_bonus

def calculate_king_bonuses(board, white_pieces, black_pieces, all_pieces_bitboard):
    white_bonus = 0
    black_bonus = 0
    def friendly_pawn_count(index, is_white, friendly_pawns_bitboard):
        if is_white:
            return pop_count(KING_FRONT_SPANS[0][index] & friendly_pawns_bitboard) * 9.5
        else:
            return pop_count(KING_FRONT_SPANS[1][index] & friendly_pawns_bitboard) * 9.5

    def friendly_adjacent_pawn_count(index, friendly_pawns_bitboard):
        return pop_count(ADJACENT_SQUARES[index] & friendly_pawns_bitboard) * 10


    def safe_king(is_white):
        if is_white:
            if (board['white_king'] >> 1) & 1 or (board['white_king'] >> 6) & 1 or (board['white_king'] >> 2) & 1:
                return True
        else:
            if (board['black_king'] >> 62) & 1 or (board['black_king'] >> 57) & 1 or (board['black_king']) >> 63 & 1:
                return True
        return False


    white_king_index = list(occupied_squares(board['white_king']))
    black_king_index = list(occupied_squares(board['black_king']))

    white_bonus += friendly_pawn_count(white_king_index[0], True, board['white_pawn'])
    white_bonus += friendly_adjacent_pawn_count(white_king_index[0], board['white_pawn'])
    if safe_king(True):
        white_bonus += 17

    black_bonus += friendly_pawn_count(black_king_index[0], False, board['black_pawn'])
    black_bonus += friendly_adjacent_pawn_count(black_king_index[0], board['black_pawn'])
    if safe_king(False):
        black_bonus += 17
    return white_bonus, black_bonus

def calculate_position_score(board, white_pieces_bitboard, black_pieces_bitboard, all_pieces_bitboard):
    white_score = 0
    black_score = 0

    white_bishop_mobility_bonus, black_bishop_mobility_bonus = calculate_bishop_mobility_bonus(board)
    white_score += int(white_bishop_mobility_bonus)
    black_score += int(black_bishop_mobility_bonus)

    white_knight_bonuses, black_knight_bonuses = calculate_knight_bonuses(board)
    white_score += int(white_knight_bonuses)
    black_score += int(black_knight_bonuses)

    white_rook_bonuses, black_rook_bonuses = calculate_rook_bonuses(board, white_pieces_bitboard, black_pieces_bitboard, all_pieces_bitboard)
    white_score += int(white_rook_bonuses)
    black_score += int(black_rook_bonuses)

    white_pawn_bonuses, black_pawn_bonuses = calculate_pawn_bonuses(board, white_pieces_bitboard, black_pieces_bitboard, all_pieces_bitboard)
    white_score += int(white_pawn_bonuses)
    black_score += int(black_pawn_bonuses)

    white_king_bonuses, black_king_bonuses = calculate_king_bonuses(board, white_pieces_bitboard, black_pieces_bitboard, all_pieces_bitboard)
    white_score += int(white_king_bonuses)
    black_score += int(black_king_bonuses)
    score = white_score - black_score

    return score



def evaluate_position(board, white_pieces_bitboard, black_pieces_bitboard, maximizing_player, WKHM, BKHM, WK, WQ, BK, BQ, game_states):
    all_pieces_bitboard = white_pieces_bitboard | black_pieces_bitboard
    white_position_value = 0
    black_position_value = 0
    piece_value_dictionary = {
        'white_pawn': np.uint64(100), 'black_pawn': np.uint64(100),
        'white_knight': np.uint64(521), 'black_knight': np.uint64(521),
        'white_bishop': np.uint64(572), 'black_bishop': np.uint64(572),
        'white_rook': np.uint64(824), 'black_rook': np.uint64(824),
        'white_queen': np.uint64(1710), 'black_queen': np.uint64(1710),
        'white_king': np.uint64(20000), 'black_king': np.uint64(20000)
    }
    score = calculate_position_score(board, white_pieces_bitboard, black_pieces_bitboard, all_pieces_bitboard)

    for piece_type, bitboard in board.items():
        piece_count = pop_count(bitboard)
        piece_value = piece_value_dictionary[piece_type]
        if 'white' in piece_type:
            white_position_value += piece_count * piece_value
        else:
            black_position_value += piece_count * piece_value

    score += int(white_position_value) - int(black_position_value)


    return score




