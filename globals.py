import pygame
import numpy as np
import copy

import globals

game_states = []
player_turn = 'white'

white_king_has_moved = False
black_king_has_moved = False
white_kingside_rook_has_moved = False
black_kingside_rook_has_moved = False
white_queenside_rook_has_moved = False
black_queenside_rook_has_moved = False
half_move_counter = 0

piece_bitboards = {
    'white_pawn': np.uint64(0x000000000000FF00),
    'white_knight': np.uint64(0x0000000000000042),
    'white_bishop': np.uint64(0x0000000000000024),
    'white_rook': np.uint64(0x0000000000000081),
    'white_queen': np.uint64(0x0000000000000008),
    'white_king': np.uint64(0x0000000000000010),
    'black_pawn': np.uint64(0x00FF000000000000),
    'black_knight': np.uint64(0x4200000000000000),
    'black_bishop': np.uint64(0x2400000000000000),
    'black_rook': np.uint64(0x8100000000000000),
    'black_queen': np.uint64(0x0800000000000000),
    'black_king': np.uint64(0x1000000000000000)
}


# Separate bitboards for white and black pieces
white_pieces_bitboard = (
    piece_bitboards['white_pawn'] | piece_bitboards['white_knight'] |
    piece_bitboards['white_bishop'] | piece_bitboards['white_rook'] |
    piece_bitboards['white_queen'] | piece_bitboards['white_king']
)

black_pieces_bitboard = (
    piece_bitboards['black_pawn'] | piece_bitboards['black_knight'] |
    piece_bitboards['black_bishop'] | piece_bitboards['black_rook'] |
    piece_bitboards['black_queen'] | piece_bitboards['black_king']
)

all_pieces_bitboard = white_pieces_bitboard | black_pieces_bitboard

def switch_player_turn():
    globals.player_turn = 'white' if globals.player_turn == 'black' else 'black'

def save_global_state():
    return {
        'player_turn': player_turn,
        'white_king_has_moved': white_king_has_moved,
        'black_king_has_moved': black_king_has_moved,
        'white_kingside_rook_has_moved': white_kingside_rook_has_moved,
        'black_kingside_rook_has_moved': black_kingside_rook_has_moved,
        'white_queenside_rook_has_moved': white_queenside_rook_has_moved,
        'black_queenside_rook_has_moved': black_queenside_rook_has_moved,
        'piece_bitboards': piece_bitboards.copy(),  # Shallow copy of dictionary
        'white_pieces_bitboard': white_pieces_bitboard,
        'black_pieces_bitboard': black_pieces_bitboard,
        'all_pieces_bitboard': all_pieces_bitboard,
        'game_states': [dict(state) for state in game_states]  # Shallow copy of list of dictionaries
    }

def restore_global_state(state):
    global player_turn, white_king_has_moved, black_king_has_moved
    global white_kingside_rook_has_moved, black_kingside_rook_has_moved
    global white_queenside_rook_has_moved, black_queenside_rook_has_moved
    global piece_bitboards, white_pieces_bitboard, black_pieces_bitboard
    global all_pieces_bitboard, game_states

    player_turn = state['player_turn']
    white_king_has_moved = state['white_king_has_moved']
    black_king_has_moved = state['black_king_has_moved']
    white_kingside_rook_has_moved = state['white_kingside_rook_has_moved']
    black_kingside_rook_has_moved = state['black_kingside_rook_has_moved']
    white_queenside_rook_has_moved = state['white_queenside_rook_has_moved']
    black_queenside_rook_has_moved = state['black_queenside_rook_has_moved']

    piece_bitboards = state['piece_bitboards'].copy()
    white_pieces_bitboard = state['white_pieces_bitboard']
    black_pieces_bitboard = state['black_pieces_bitboard']
    all_pieces_bitboard = state['all_pieces_bitboard']
    game_states = [dict(state) for state in state['game_states']]