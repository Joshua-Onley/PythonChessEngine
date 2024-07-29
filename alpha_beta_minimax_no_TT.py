import globals

minimax_call_count = 0

from hand_crafted_evaluation import evaluate_position
from move_logic import gen_legal_moves, make_move
from globals import save_global_state, restore_global_state, switch_player_turn
from debugging_functions import print_binary_as_bitboard, print_binary_as_chessboard
import numpy as np
from move_ordering import order_moves
from PST_evaluation import evaluate
leaf_node_count = 0


def alpha_beta_minimax_(depth, maximizing_player, alpha, beta):
    global leaf_node_count

    if depth == 0:
        leaf_node_count += 1
        eval = evaluate(globals.piece_bitboards)
        return eval, None

    best_move = None
    if maximizing_player:
        captures, non_captures = gen_legal_moves()


        max_eval = float('-inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = alpha_beta_minimax_(depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            restore_global_state(saved_state)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        captures, non_captures = gen_legal_moves()

        min_eval = float('inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = alpha_beta_minimax_(depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            restore_global_state(saved_state)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move
