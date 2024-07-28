import copy
import time
from globals import switch_player_turn
import pygame

import globals
from main import determine_what_piece_has_been_selected
from bit_manipulation import clear_square, set_square
from debugging_functions import print_binary_as_bitboard
from move_logic import checkmate, make_move

from alpha_beta_minimax import alpha_beta_minimax
from quiescence_minimax import alpha_beta_quiescence_minimax
from standard_minimax import minimax
from alpha_beta_minimax_no_TT import alpha_beta_minimax_
import standard_minimax
import alpha_beta_minimax_no_TT

def make_computer_move(colour):


    depth = 3
    if colour == 'black':
        start_time = time.time()
        min_eval, best_move = alpha_beta_minimax_(depth, False, float('-inf'), float('inf'))
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'time taken: {time_taken}')
        print(f'leaf nodes evaluated: {alpha_beta_minimax_no_TT.leaf_node_count}')
        alpha_beta_minimax_no_TT.leaf_node_count = 0 # reset counter

    else:
        min_eval, best_move = alpha_beta_minimax_(depth, True, float('-inf'), float('inf'))
    if best_move:
        piece, start_index, end_index = best_move
        make_move(piece, start_index, end_index)
        print(f'minimum evaluation: {min_eval}')
        globals.player_turn = 'white'
    else:
        checkmate('white')


