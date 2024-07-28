import numpy as np
from debugging_functions import print_binary_as_bitboard

# Define the initial counts for each piece type
piece_counts = {
    'white_pawn': 5,
    'black_pawn': 5,
    'white_knight': 1,
    'black_knight': 2,
    'white_bishop': 2,
    'black_bishop': 1,
    'white_rook': 1,
    'black_rook': 1,
    'white_queen': 1,
    'black_queen': 1,
    'white_king': 1,
    'black_king': 1
}
all_positions = list(range(64))
random_positions = []
for _ in range(100):
    np.random.shuffle(all_positions)
    board = {}
    position_index = 0
    for piece, count in piece_counts.items():
        positions = all_positions[position_index:position_index + count]
        position_index += count
        bitboard = np.uint64(0)
        for pos in positions:
            bitboard |= np.uint64(1) << np.uint64(pos)

        board[piece] = bitboard
    random_positions.append(board)

print(random_positions)
