import copy
import time
from globals import switch_player_turn
import pygame

import globals
from main import determine_what_piece_has_been_selected
from bit_manipulation import clear_square, set_square
from debugging_functions import print_binary_as_bitboard
from move_logic import checkmate, make_move

import quiescence_minimax
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
        min_eval, best_move = alpha_beta_quiescence_minimax(depth, False, float('-inf'), float('inf'))
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'Move: `{globals.half_move_counter}')
        print(f'time taken: {time_taken}')
        print(f'leaf nodes evaluated: {quiescence_minimax.leaf_node_count}')
        print(f'leaf node evaluations retrieved from transposition table: {quiescence_minimax.leaf_node_evaluations_retrieved_from_transposition_table}')
        quiescence_minimax.leaf_node_count, quiescence_minimax.leaf_node_evaluations_retrieved_from_transposition_table = 0,0 # reset counter
        print('\n')

    else:
        start_time = time.time()
        min_eval, best_move = alpha_beta_quiescence_minimax(depth, True, float('-inf'), float('inf'))
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'Move: `{globals.half_move_counter}')
        print(f'time taken: {time_taken}')
        print(f'leaf nodes evaluated: {quiescence_minimax.leaf_node_count}')
        print(
            f'leaf node evaluations retrieved from transposition table: {quiescence_minimax.leaf_node_evaluations_retrieved_from_transposition_table}')
        quiescence_minimax.leaf_node_count, quiescence_minimax.leaf_node_evaluations_retrieved_from_transposition_table = 0, 0 # reset counter
        print('\n')

    if best_move:
        piece, start_index, end_index = best_move
        make_move(piece, start_index, end_index)
    else:
        checkmate('white')


