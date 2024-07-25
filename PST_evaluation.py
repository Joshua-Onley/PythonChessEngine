import globals
from piece_square_tables import OPENING, MIDDLEGAME, ENDGAME, PIECE_SQUARE_TABLES
from bit_manipulation import occupied_squares
import numpy as np

piece_value_dictionary = {
    'white_pawn': np.uint64(100), 'black_pawn': np.uint64(100),
    'white_knight': np.uint64(521), 'black_knight': np.uint64(521),
    'white_bishop': np.uint64(572), 'black_bishop': np.uint64(572),
    'white_rook': np.uint64(824), 'black_rook': np.uint64(824),
    'white_queen': np.uint64(1710), 'black_queen': np.uint64(1710),
    'white_king': np.uint64(20000), 'black_king': np.uint64(20000)
}


def determine_game_phase():
    number_of_pieces = len(list(occupied_squares(globals.all_pieces_bitboard)))
    if number_of_pieces > 25:
        return OPENING
    elif number_of_pieces > 12:
        return MIDDLEGAME
    else:
        return ENDGAME



def evaluate(board):
    phase = determine_game_phase()
    eval_score = 0

    # Dictionary for piece bitboards
    bitboard_map = {
        'pawn': ('white_pawn', 'black_pawn'),
        'knight': ('white_knight', 'black_knight'),
        'bishop': ('white_bishop', 'black_bishop'),
        'rook': ('white_rook', 'black_rook'),
        'queen': ('white_queen', 'black_queen'),
        'king': ('white_king', 'black_king')
    }

    for piece_type in bitboard_map:
        white_piece_key, black_piece_key = bitboard_map[piece_type]
        white_pieces = occupied_squares(board[white_piece_key])
        black_pieces = occupied_squares(board[black_piece_key])

        # Add piece values and piece-square table values for white pieces
        for sq in white_pieces:
            eval_score += PIECE_SQUARE_TABLES[piece_type][phase][63 - sq]
            eval_score += piece_value_dictionary[white_piece_key]

        # Subtract piece values and piece-square table values for black pieces
        for sq in black_pieces:
            eval_score -= PIECE_SQUARE_TABLES[piece_type][phase][sq]
            eval_score -= piece_value_dictionary[black_piece_key]

    return eval_score