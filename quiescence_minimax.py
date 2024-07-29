import globals

minimax_call_count = 0

from move_logic import gen_legal_moves, make_move
from globals import save_global_state, restore_global_state, switch_player_turn
from PST_evaluation import evaluate
from move_ordering import order_moves


leaf_node_count = 0
leaf_node_evaluations_retrieved_from_transposition_table = 0


def alpha_beta_quiescence_minimax(depth, maximizing_player, alpha, beta):
    global leaf_node_count

    if depth == 0:
        return quiescence_search(alpha, beta, maximizing_player, depth, 10), None

    best_move = None
    if maximizing_player:

        captures, non_captures = gen_legal_moves()
        ordered_captures = order_moves(captures)
        max_eval = float('-inf')
        for move in ordered_captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = alpha_beta_quiescence_minimax(depth - 1, False, alpha, beta)
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
        ordered_captures = order_moves(captures)
        min_eval = float('inf')
        for move in ordered_captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = alpha_beta_quiescence_minimax(depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            restore_global_state(saved_state)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move


def quiescence_search(alpha, beta, maximizing_player, depth, max_depth):
    global leaf_node_count
    global leaf_node_evaluations_retrieved_from_transposition_table


    stand_pat = evaluate(globals.piece_bitboards)
    leaf_node_count += 1

    # If the current depth is greater than or equal to max depth, return the stand-pat evaluation
    if depth >= max_depth:
        print('maximum depth reached ###########')
        return stand_pat

    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        captures, _ = gen_legal_moves()
        ordered_captures = order_moves(captures)

        for move in ordered_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            score = quiescence_search(alpha, beta, False, depth + 1, max_depth)
            restore_global_state(saved_state)
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

        captures, _ = gen_legal_moves()
        ordered_captures = order_moves(captures)
        for move in ordered_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            score = quiescence_search(alpha, beta, True, depth + 1, max_depth)
            restore_global_state(saved_state)
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta
