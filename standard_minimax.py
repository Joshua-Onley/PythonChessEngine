import globals
from PST_evaluation import evaluate
from move_logic import gen_legal_moves
from globals import switch_player_turn, save_global_state, restore_global_state
leaf_node_count = 0

def minimax(depth, maximizing_player, alpha, beta):
    from computer_move import make_move
    global leaf_node_count
    if depth == 0:
        leaf_node_count += 1
        return evaluate(globals.piece_bitboards), None

    best_move = None
    if maximizing_player:
        captures, non_captures = gen_legal_moves()
        max_eval = float('-inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = minimax(depth - 1, False, alpha, beta)
            restore_global_state(saved_state)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        captures, non_captures = gen_legal_moves()
        min_eval = float('inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            eval, _ = minimax(depth - 1, True, alpha, beta)
            restore_global_state(saved_state)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move