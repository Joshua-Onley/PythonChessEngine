
import globals

mvv_lva_indexes = {
    'king': 0,
    'queen': 1,
    'rook': 2,
    'bishop': 3,
    'knight': 4,
    'pawn': 5
}

mvv_lva = [
    [0, 0, 0, 0, 0, 0],       # victim K, attacker K, Q, R, B, N, P
    [50, 51, 52, 53, 54, 55], # victim Q, attacker K, Q, R, B, N, P
    [40, 41, 42, 43, 44, 45], # victim R, attacker K, Q, R, B, N, P
    [30, 31, 32, 33, 34, 35], # victim B, attacker K, Q, R, B, N, P
    [20, 21, 22, 23, 24, 25], # victim N, attacker K, Q, R, B, N, P
    [10, 11, 12, 13, 14, 15], # victim P, attacker K, Q, R, B, N, P       # victim None, attacker K, Q, R, B, N, P
]

def get_piece_type(bitboard_index):
    if (globals.piece_bitboards['white_pawn'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_pawn'] >> bitboard_index) & 1 == 1:
        return 'pawn'
    elif (globals.piece_bitboards['white_knight'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_knight'] >> bitboard_index) & 1 == 1:
        return 'knight'
    elif (globals.piece_bitboards['white_bishop'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_bishop'] >> bitboard_index) & 1 == 1:
        return 'bishop'
    elif (globals.piece_bitboards['white_rook'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_rook'] >> bitboard_index) & 1 == 1:
        return 'rook'
    elif (globals.piece_bitboards['white_queen'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_queen'] >> bitboard_index) & 1 == 1:
        return 'queen'
    elif (globals.piece_bitboards['white_king'] >> bitboard_index) & 1 == 1 or (globals.piece_bitboards['black_king'] >> bitboard_index) & 1 == 1:
        return 'king'

    return None

def score_move(move):
    piece, start_index, end_index = move
    attacker_type = piece[6:]
    victim_type = get_piece_type(end_index)
    if attacker_type is None or victim_type is None:
        return float('-inf')

    attacker_value = mvv_lva_indexes[attacker_type]
    victim_value = mvv_lva_indexes[victim_type]

    return mvv_lva[victim_value][attacker_value]


def order_moves(moves):
    return sorted(moves, key=score_move, reverse=True)
