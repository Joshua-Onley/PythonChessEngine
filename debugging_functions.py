# print_binary_as_bitboard prints the bitboard representation
# print_binary_as_chessboard prints the bitboard with all the rows reversed which is how the game is displayed in the gui


def print_binary_as_bitboard(binary_number):
    binary_str = bin(binary_number)[2:]
    padded_binary_str = binary_str.zfill(64)
    blocks = [padded_binary_str[i:i + 8] for i in range(0, 64, 8)]

    for block in blocks:
        print(block)

def print_binary_as_chessboard(binary_number):
    binary_str = bin(binary_number)[2:]
    padded_binary_str = binary_str.zfill(64)
    blocks = [padded_binary_str[i:i + 8] for i in range(0, 64, 8)]

    for block in blocks:
        reversed_block = ''.join(reversed(block))
        print(reversed_block)