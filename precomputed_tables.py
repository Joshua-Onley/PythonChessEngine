import numpy as np

import globals
from bit_manipulation import find_lsb_index, find_msb_index
from debugging_functions import print_binary_as_bitboard

BITBOARD_INDEX_TO_CHESS_SQUARE = {
    0: 'H1', 1: 'G1', 2: 'F1', 3: 'E1', 4: 'D1', 5: 'C1', 6: 'B1', 7: 'A1',
    8: 'H2', 9: 'G2', 10: 'F2', 11: 'E2', 12: 'D2', 13: 'C2', 14: 'B2', 15: 'A2',
    16: 'H3', 17: 'G3', 18: 'F3', 19: 'E3', 20: 'D3', 21: 'C3', 22: 'B3', 23: 'A3',
    24: 'H4', 25: 'G4', 26: 'F4', 27: 'E4', 28: 'D4', 29: 'C4', 30: 'B4', 31: 'A4',
    32: 'H5', 33: 'G5', 34: 'F5', 35: 'E5', 36: 'D5', 37: 'C5', 38: 'B5', 39: 'A5',
    40: 'H6', 41: 'G6', 42: 'F6', 43: 'E6', 44: 'D6', 45: 'C6', 46: 'B6', 47: 'A6',
    48: 'H7', 49: 'G7', 50: 'F7', 51: 'E7', 52: 'D7', 53: 'C7', 54: 'B7', 55: 'A7',
    56: 'H8', 57: 'G8', 58: 'F8', 59: 'E8', 60: 'D8', 61: 'C8', 62: 'B8', 63: 'A8'
}

# initialize constant variables
EMPTY_BITBOARD = np.uint64(0)

ROW_1 = np.uint64(0b0000000000000000000000000000000000000000000000000000000011111111)
ROW_2 = np.uint64(0b0000000000000000000000000000000000000000000000001111111100000000)
ROW_3 = np.uint64(0b0000000000000000000000000000000000000000111111110000000000000000)
ROW_4 = np.uint64(0b0000000000000000000000000000000011111111000000000000000000000000)
ROW_5 = np.uint64(0b0000000000000000000000001111111100000000000000000000000000000000)
ROW_6 = np.uint64(0b0000000000000000111111110000000000000000000000000000000000000000)
ROW_7 = np.uint64(0b0000000011111111000000000000000000000000000000000000000000000000)
ROW_8 = np.uint64(0b1111111100000000000000000000000000000000000000000000000000000000)

ROWS = np.array([ROW_1, ROW_2, ROW_3, ROW_4, ROW_5, ROW_6, ROW_7, ROW_8], dtype=np.uint64)

COL_A = 0b0000000100000001000000010000000100000001000000010000000100000001
COL_B = 0b0000001000000010000000100000001000000010000000100000001000000010
COL_C = 0b0000010000000100000001000000010000000100000001000000010000000100
COL_D = 0b0000100000001000000010000000100000001000000010000000100000001000
COL_E = 0b0001000000010000000100000001000000010000000100000001000000010000
COL_F = 0b0010000000100000001000000010000000100000001000000010000000100000
COL_G = 0b0100000001000000010000000100000001000000010000000100000001000000
COL_H = 0b1000000010000000100000001000000010000000100000001000000010000000

COLUMNS = np.array([COL_A, COL_B, COL_C, COL_D, COL_E, COL_F, COL_G, COL_H], dtype=np.uint64)

# this array has 64 elements - each element is a 64 bit bitboard
# each element corresponds to a square and the column that is occupies
COL_MASKS = np.array([
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # First col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Second col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Third col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Fourth col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Fifth col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Sixth col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080,  # Seventh col
    0x0101010101010101, 0x0202020202020202, 0x0404040404040404, 0x0808080808080808,
    0x1010101010101010, 0x2020202020202020, 0x4040404040404040, 0x8080808080808080  # Eighth col
], dtype=np.uint64)

# This array has 64 elements - one for each square of the chess board
# each element corresponds to a square and the row that it occupies
# to avoid writing out hundreds of 0s and 1s the bitboards are represented in hex
# for example, 0x000000FF is equivalent to 0b00000000 00000000 00000000 00000000 00000000 00000000 00000000 11111111
ROW_MASKS = np.array([0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF,
                      0x0000FF00, 0x0000FF00, 0x0000FF00, 0x0000FF00, 0x0000FF00, 0x0000FF00, 0x0000FF00, 0x0000FF00,
                      0x00FF0000, 0x00FF0000, 0x00FF0000, 0x00FF0000, 0x00FF0000, 0x00FF0000, 0x00FF0000, 0x00FF0000,
                      0xFF000000, 0xFF000000, 0xFF000000, 0xFF000000, 0xFF000000, 0xFF000000, 0xFF000000, 0xFF000000,
                      0xFF00000000, 0xFF00000000, 0xFF00000000, 0xFF00000000, 0xFF00000000, 0xFF00000000, 0xFF00000000,
                      0xFF00000000,
                      0xFF0000000000, 0xFF0000000000, 0xFF0000000000, 0xFF0000000000, 0xFF0000000000, 0xFF0000000000,
                      0xFF0000000000, 0xFF0000000000,
                      0xFF000000000000, 0xFF000000000000, 0xFF000000000000, 0xFF000000000000, 0xFF000000000000,
                      0xFF000000000000, 0xFF000000000000, 0xFF000000000000,
                      0xFF00000000000000, 0xFF00000000000000, 0xFF00000000000000, 0xFF00000000000000,
                      0xFF00000000000000, 0xFF00000000000000, 0xFF00000000000000, 0xFF00000000000000], dtype=np.uint64)

# the A1 to H8 diagonal can be represented as a bitboard
# 10000000
# 01000000
# 00100000
# 00010000
# 00001000
# 00000100
# 00000010
# 00000001
A1_to_H8_DIAGONAL_MASK = np.uint64(0b1000000001000000001000000001000000001000000001000000001000000001)

# the H1 to H8 diagonal can also be represented as a bitboard:
# 00000001
# 00000010
# 00000100
# 00001000
# 00010000
# 00100000
# 01000000
# 10000000
H1_to_A8_DIAGONAL_MASK = np.uint64(0b0000000100000010000001000000100000010000001000000100000010000000)

# Bitboard representing the central squares of the board (useful for evaluation)
# 00000000
# 00000000
# 00111100
# 00111100
# 00111100
# 00111100
# 00000000
# 00000000
CENTER = np.uint64(0b0000000000000000001111000011110000111100001111000000000000000000)

debruijn_table = np.array(
    [0, 1, 48, 2, 57, 49, 28, 3,
     61, 58, 50, 42, 38, 29, 17, 4,
     62, 55, 59, 36, 53, 51, 43, 22,
     45, 39, 33, 30, 24, 18, 12, 5,
     63, 47, 56, 27, 60, 41, 37, 16,
     54, 35, 52, 21, 44, 32, 23, 11,
     46, 26, 40, 15, 34, 20, 31, 10,
     25, 14, 19, 9, 13, 8, 7, 6], dtype=np.uint8
)

column = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7
}

def generate_neighbor_columns(i):
    col = i % 8

    left_neighbor_columns = np.uint64(0)
    right_neighbor_columns = np.uint64(0)

    if col > 0:  # If not on the 'a' file
        left_neighbor_columns = np.uint64(0x0101010101010101) << (col - 1)
    if col < 7:  # If not on the 'h' file
        right_neighbor_columns = np.uint64(0x0101010101010101) << (col + 1)

    return left_neighbor_columns | right_neighbor_columns


# Create the neighbor files lookup table
neighbor_columns = np.fromiter(
    (generate_neighbor_columns(i)
     for i in range(64)),
    dtype=np.uint64,
    count=64)

neighbor_columns.shape = (64,)

def generate_king_front_span_table():
    # Initialize the table
    KING_FRONT_SPANS = np.zeros((2, 64), dtype=np.uint64)

    for sq in range(64):
        row, col = divmod(sq, 8)


        if row < 7:
            bitboard = 0
            if col > 0:  # Left file
                bitboard |= np.uint64(1) << ((row + 1) * 8 + (col - 1))
            bitboard |= np.uint64(1) << ((row + 1) * 8 + col)  # Same file
            if col < 7:  # Right file
                bitboard |= np.uint64(1) << ((row + 1) * 8 + (col + 1))
            KING_FRONT_SPANS[0][sq] = bitboard


        if row > 0:
            bitboard = 0
            if col > 0:  # Left file
                bitboard |= np.uint64(1) << ((row - 1) * 8 + (col - 1))
            bitboard |= np.uint64(1) << ((row - 1) * 8 + col)  # Same file
            if col < 7:  # Right file
                bitboard |= np.uint64(1) << ((row - 1) * 8 + (col + 1))
            KING_FRONT_SPANS[1][sq] = bitboard

    return KING_FRONT_SPANS

KING_FRONT_SPANS = generate_king_front_span_table()

def generate_LR_squares_table():
    NEIGHBOR_COLUMNS = np.zeros(64, dtype=np.uint64)

    for sq in range(64):
        row, col = divmod(sq, 8)
        bitboard = np.uint64(0)

        # Left neighbor
        if col > 0:
            bitboard |= np.uint64(1) << (row * 8 + (col - 1))

        # Right neighbor
        if col < 7:
            bitboard |= np.uint64(1) << (row * 8 + (col + 1))

        NEIGHBOR_COLUMNS[sq] = bitboard

    return NEIGHBOR_COLUMNS

ADJACENT_SQUARES = generate_LR_squares_table()

def generate_frontspan(i, colour):
    rank = i // 8
    file = i % 8

    frontspan = np.uint64(0)

    if colour == 'white':
        for r in range(rank + 1, 8):
            for f in range(max(0, file - 1), min(8, file + 2)):
                frontspan |= np.uint64(1) << (r * 8 + f)
    else:
        for r in range(rank - 1, -1, -1):
            for f in range(max(0, file - 1), min(8, file + 2)):
                frontspan |= np.uint64(1) << (r * 8 + f)

    return frontspan


FRONT_SPANS = np.fromiter(
    (generate_frontspan(i, colour)
     for colour in ['white', 'black']
     for i in range(64)),
    dtype=np.uint64,
    count=2 * 64)

FRONT_SPANS.shape = (2, 64)


def calculate_diagonal_mask(index):
    diagonal = 8 * (index & 7) - (index & 56)
    north = -diagonal & (diagonal >> 31)
    south = diagonal & (-diagonal >> 31)
    mask = (A1_to_H8_DIAGONAL_MASK >> np.uint8(south)) << np.uint8(north)
    return mask


def calculate_antidiag_mask(index):
    diagonal = 56 - 8 * (index & 7) - (index & 56)
    north = -diagonal & (diagonal >> 31)
    south = diagonal & (-diagonal >> 31)
    anti_diagonal_mask = (H1_to_A8_DIAGONAL_MASK >> np.uint8(south)) << np.uint8(north)
    return anti_diagonal_mask


ANTIDIAGONAL_MASKS = np.fromiter(
    (calculate_antidiag_mask(i) for i in range(64)),
    dtype=np.uint64,
    count=64)

DIAGONAL_MASKS = np.fromiter(
    (calculate_diagonal_mask(i) for i in range(64)),
    dtype=np.uint64,
    count=64)


def compute_first_row_moves(i, occ):
    left_ray = lambda x: x - np.uint8(1)
    right_ray = lambda x: (~x) & ~(x - np.uint8(1))

    x = np.uint8(1) << np.uint8(i)
    occ = np.uint8(occ)

    left_attacks = left_ray(x)
    left_blockers = left_attacks & occ
    if left_blockers != np.uint8(0):
        leftmost = np.uint8(1) << find_msb_index(np.uint64(left_blockers))
        left_garbage = left_ray(leftmost)
        left_attacks ^= left_garbage

    right_attacks = right_ray(x)
    right_blockers = right_attacks & occ
    if right_blockers != np.uint8(0):
        rightmost = np.uint8(1) << find_lsb_index(np.uint64(right_blockers))
        right_garbage = right_ray(rightmost)
        right_attacks ^= right_garbage

    return left_attacks ^ right_attacks


FIRST_ROW_MOVES = np.fromiter(
    (compute_first_row_moves(i, occ)
     for i in range(8)
     for occ in range(256)),
    dtype=np.uint8,
    count=8 * 256)
FIRST_ROW_MOVES.shape = (8, 256)


def compute_pawn_attack_moves(colour, index):
    # Convert index to a bitboard
    bitboard = np.uint64(1 << index)

    column_a_mask = np.uint64(0x7F7F7F7F7F7F7F7F)
    column_h_mask = np.uint64(0xFEFEFEFEFEFEFEFE)

    if colour == 'white':
        left_attack = (bitboard & column_h_mask) << np.uint8(7)
        right_attack = (bitboard & column_a_mask) << np.uint8(9)
    else:
        left_attack = (bitboard & column_h_mask) >> np.uint8(9)
        right_attack = (bitboard & column_a_mask) >> np.uint8(7)

    return left_attack | right_attack

PAWN_ATTACKS = np.fromiter(
    (compute_pawn_attack_moves(colour, i)
     for colour in ['black', 'white']
     for i in range(64)),
    dtype=np.uint64,
    count=2 * 64)
PAWN_ATTACKS.shape = (2, 64)


def compute_pawn_quiet_moves(colour, i):
    shift_forward = lambda bitboard, colour, i: \
        bitboard << np.uint(8 * i) if colour == 'white' else bitboard >> np.uint8(8 * i)
    starting_rank = ROWS[1] if colour == 'white' else ROWS[6]

    bitboard = np.uint64(1) << i

    s1 = shift_forward(bitboard, colour, 1)
    s2 = shift_forward((bitboard & starting_rank), colour, 2)

    return s1 | s2

PAWN_QUIETS = np.fromiter(
    (compute_pawn_quiet_moves(colour, i)
     for colour in ['white', 'black']
     for i in range(64)),
    dtype=np.uint64,
    count=2 * 64)
PAWN_QUIETS.shape = (2, 64)


def calculate_knight_moves(index):
    knight_position_bitboard = np.uint64(1) << index

    column_AB_mask = ~(COLUMNS[column['A']] | COLUMNS[column['B']])
    column_HG_mask = ~(COLUMNS[column['H']] | COLUMNS[column['G']])
    column_A_mask = ~COLUMNS[column['A']]
    column_H_mask = ~(COLUMNS[column['H']])

    move_1 = (knight_position_bitboard & column_AB_mask) << np.uint8(6)
    move_2 = (knight_position_bitboard & column_A_mask) << np.uint8(15)
    move_3 = (knight_position_bitboard & column_H_mask) << np.uint8(17)
    move_4 = (knight_position_bitboard & column_HG_mask) << np.uint8(10)
    move_5 = (knight_position_bitboard & column_HG_mask) >> np.uint8(6)
    move_6 = (knight_position_bitboard & column_H_mask) >> np.uint8(15)
    move_7 = (knight_position_bitboard & column_A_mask) >> np.uint8(17)
    move_8 = (knight_position_bitboard & column_AB_mask) >> np.uint8(10)

    knight_moves = move_1 | move_2 | move_3 | move_4 | move_5 | move_6 | move_7 | move_8
    return knight_moves


KNIGHT_MOVES = np.fromiter(
    (calculate_knight_moves(i) for i in range(64)),
    dtype=np.uint64,
    count=64)


def generate_king_moves(index):
    square_bitboard = np.uint64(1) << index

    column_a_mask = np.uint64(0xFEFEFEFEFEFEFEFE)
    column_h_mask = np.uint64(0x7F7F7F7F7F7F7F7F)

    north_west = (square_bitboard & column_a_mask) << np.uint8(7)
    north = (square_bitboard << np.uint8(8))
    north_east = (square_bitboard & column_h_mask) << np.uint8(9)
    east = (square_bitboard & column_h_mask) << np.uint8(1)
    south_east = (square_bitboard & column_h_mask) >> np.uint8(7)
    south = (square_bitboard >> np.uint8(8))
    south_west = (square_bitboard & column_a_mask) >> np.uint8(9)
    west = (square_bitboard & column_a_mask) >> np.uint8(1)

    moves_bitboard = north_west | north | north_east | east | south_east | south | south_west | west
    return moves_bitboard


KING_MOVES = np.fromiter(
    (generate_king_moves(i) for i in range(64)),
    dtype=np.uint64,
    count=64)
