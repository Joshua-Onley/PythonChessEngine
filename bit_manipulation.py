import numpy as np

np.seterr(over='ignore')

debruijn = np.uint64(0x03f79d71b4cb0a89)
empty_bitboard = np.uint64(0)

lsb_lookup = np.array(
        [ 0,  1, 48,  2, 57, 49, 28,  3,
         61, 58, 50, 42, 38, 29, 17,  4,
         62, 55, 59, 36, 53, 51, 43, 22,
         45, 39, 33, 30, 24, 18, 12,  5,
         63, 47, 56, 27, 60, 41, 37, 16,
         54, 35, 52, 21, 44, 32, 23, 11,
         46, 26, 40, 15, 34, 20, 31, 10,
         25, 14, 19,  9, 13,  8,  7,  6],
        dtype=np.uint8)

msb_lookup = np.array(
        [ 0, 47,  1, 56, 48, 27,  2, 60,
         57, 49, 41, 37, 28, 16,  3, 61,
         54, 58, 35, 52, 50, 42, 21, 44,
         38, 32, 29, 23, 17, 11,  4, 62,
         46, 55, 26, 59, 40, 36, 15, 53,
         34, 51, 20, 43, 31, 22, 10, 45,
         25, 39, 14, 33, 19, 30,  9, 24,
         13, 18,  8, 12,  7,  6,  5, 63],
        dtype=np.uint8)

def find_lsb_index(bitboard):
    return lsb_lookup[((bitboard & -bitboard) * debruijn) >> np.uint8(58)]

def find_msb_index(bitboard):
    bitboard |= bitboard >> np.uint8(1)
    bitboard |= bitboard >> np.uint8(2)
    bitboard |= bitboard >> np.uint8(4)
    bitboard |= bitboard >> np.uint8(8)
    bitboard |= bitboard >> np.uint8(16)
    bitboard |= bitboard >> np.uint8(32)
    return msb_lookup[(bitboard * debruijn) >> np.uint8(58)]


def clear_square(bitboard, square_index):
    index_bitboard = to_bitboard(square_index)
    return (~index_bitboard) & bitboard

def set_square(bitboard, square_index):
    index_bitboard = to_bitboard(square_index)
    return index_bitboard | bitboard

def to_bitboard(index):
    return np.uint64(1) << index

def occupied_squares(bitboard):
    while bitboard != empty_bitboard:
        lsb_square = find_lsb_index(bitboard)
        yield lsb_square
        bitboard ^= to_bitboard(lsb_square)

def retrieve_occupied_squares(bitboard):
    occupied = []
    for index in range(64):
        if bitboard & (1 << index):
            occupied.append(index)
    return occupied

import numpy as np

def pop_count(bitboard):
    return np.uint8(np.binary_repr(bitboard).count('1'))

