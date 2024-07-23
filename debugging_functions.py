def print_binary_as_bitboard(binary_number):
    # Convert the binary number to a string and remove the '0b' prefix
    binary_str = bin(binary_number)[2:]

    # Pad the binary string with leading zeros to ensure it is 64 bits long
    padded_binary_str = binary_str.zfill(64)

    # Split the padded binary string into blocks of 8 bits
    blocks = [padded_binary_str[i:i + 8] for i in range(0, 64, 8)]

    # Print each block on a new line
    for block in blocks:
        print(block)

def print_binary_as_chessboard(binary_number):
    # Convert the binary number to a string and remove the '0b' prefix
    binary_str = bin(binary_number)[2:]

    # Pad the binary string with leading zeros to ensure it is 64 bits long
    padded_binary_str = binary_str.zfill(64)

    # Split the padded binary string into blocks of 8 bits
    blocks = [padded_binary_str[i:i + 8] for i in range(0, 64, 8)]

    # Print each block on a new line
    for block in blocks:
        reversed_block = ''.join(reversed(block))
        print(reversed_block)