import numpy as np


def fen_to_bitboards(fen):

    bitboards = {
        'white_pawn': np.uint64(0),
        'black_pawn': np.uint64(0),
        'white_knight': np.uint64(0),
        'black_knight': np.uint64(0),
        'white_bishop': np.uint64(0),
        'black_bishop': np.uint64(0),
        'white_rook': np.uint64(0),
        'black_rook': np.uint64(0),
        'white_queen': np.uint64(0),
        'black_queen': np.uint64(0),
        'white_king': np.uint64(0),
        'black_king': np.uint64(0),
    }

    parts = fen.split()
    piece_placement = parts[0]

    def update_bitboard(bitboard, position, piece):
        bitboard |= np.uint64(1) << position
        return bitboard

    rows = piece_placement.split('/')
    for rank, row in enumerate(rows):
        file_index = 0
        for char in row:
            if char.isdigit():
                file_index += int(char)
            else:
                position = (7 - rank) * 8 + file_index
                if char == 'p':
                    bitboards['black_pawn'] = update_bitboard(bitboards['black_pawn'], position, char)
                elif char == 'P':
                    bitboards['white_pawn'] = update_bitboard(bitboards['white_pawn'], position, char)
                elif char == 'n':
                    bitboards['black_knight'] = update_bitboard(bitboards['black_knight'], position, char)
                elif char == 'N':
                    bitboards['white_knight'] = update_bitboard(bitboards['white_knight'], position, char)
                elif char == 'b':
                    bitboards['black_bishop'] = update_bitboard(bitboards['black_bishop'], position, char)
                elif char == 'B':
                    bitboards['white_bishop'] = update_bitboard(bitboards['white_bishop'], position, char)
                elif char == 'r':
                    bitboards['black_rook'] = update_bitboard(bitboards['black_rook'], position, char)
                elif char == 'R':
                    bitboards['white_rook'] = update_bitboard(bitboards['white_rook'], position, char)
                elif char == 'q':
                    bitboards['black_queen'] = update_bitboard(bitboards['black_queen'], position, char)
                elif char == 'Q':
                    bitboards['white_queen'] = update_bitboard(bitboards['white_queen'], position, char)
                elif char == 'k':
                    bitboards['black_king'] = update_bitboard(bitboards['black_king'], position, char)
                elif char == 'K':
                    bitboards['white_king'] = update_bitboard(bitboards['white_king'], position, char)
                file_index += 1

    return bitboards

fen = "rn2k2r/pp1b1pp1/4p2p/8/1q1pPP2/5N2/P3PPBP/R1Q2RK1 b kq - 0 15"

bitboards = fen_to_bitboards(fen)

for piece, bitboard in bitboards.items():
    print(f"'{piece}': np.uint64({bitboard:#018x}),")
