import copy
import time
from globals import switch_player_turn
import pygame

import globals
from main import determine_what_piece_has_been_selected
from bit_manipulation import clear_square, set_square
from debugging_functions import print_binary_as_bitboard
from move_logic import checkmate, make_move


def make_computer_move(colour):
    from alpha_beta_minimax import alpha_beta_minimax
    from quiescence_minimax import alpha_beta_quiescence_minimax

    depth = 2
    if colour == 'black':
        start_time = time.time()
        min_eval, best_move = alpha_beta_quiescence_minimax(depth, False, float('-inf'), float('inf'))
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'time taken: {time_taken}')
    else:
        min_eval, best_move = alpha_beta_quiescence_minimax(depth, True, float('-inf'), float('inf'))
    if best_move:
        piece, start_index, end_index = best_move
        make_move(piece, start_index, end_index)
        print(f'minimum evaluation: {min_eval}')
        globals.player_turn = 'white'
    else:
        checkmate('white')


