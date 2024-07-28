import globals

minimax_call_count = 0

from move_logic import gen_legal_moves, make_move
from globals import save_global_state, restore_global_state, switch_player_turn
from PST_evaluation import evaluate
from move_ordering import order_moves


leaf_node_count = 0
leaf_node_evaluations_retrieved_from_transposition_table = 0
quiescence_transposition_table = {}

def hash_board_state():

    board_state = (
        globals.piece_bitboards['white_pawn'], globals.piece_bitboards['white_knight'],
        globals.piece_bitboards['white_bishop'], globals.piece_bitboards['white_rook'],
        globals.piece_bitboards['white_queen'], globals.piece_bitboards['white_king'],
        globals.piece_bitboards['black_pawn'], globals.piece_bitboards['black_knight'],
        globals.piece_bitboards['black_bishop'], globals.piece_bitboards['black_rook'],
        globals.piece_bitboards['black_queen'], globals.piece_bitboards['black_king'],
        globals.white_pieces_bitboard, globals.black_pieces_bitboard, globals.all_pieces_bitboard,
        globals.white_king_has_moved, globals.black_king_has_moved,
        globals.white_kingside_rook_has_moved, globals.black_kingside_rook_has_moved,
        globals.white_queenside_rook_has_moved, globals.black_queenside_rook_has_moved
    )
    return hash(board_state)


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

    board_hash = hash_board_state()
    if board_hash in quiescence_transposition_table:
        stored_eval = quiescence_transposition_table[board_hash]
        leaf_node_evaluations_retrieved_from_transposition_table += 1
        leaf_node_count += 1
        return stored_eval

    stand_pat = evaluate(globals.piece_bitboards)
    leaf_node_count += 1

    if depth >= max_depth:
        return stand_pat

    if maximizing_player:
        #print(f'quiescence search | depth {depth}')
        if stand_pat >= beta:
            quiescence_transposition_table[board_hash] = beta
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        #print(f'quiescence search generating moves for white...')
        captures, _ = gen_legal_moves()
        ordered_captures = order_moves(captures)
        #print(f'ordered captures for white: {ordered_captures}')

        for move in ordered_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            score = quiescence_search(alpha, beta, False, depth + 1, max_depth)
            restore_global_state(saved_state)
            if score >= beta:
                quiescence_transposition_table[board_hash] = beta
                return beta
            if score > alpha:
                alpha = score
        quiescence_transposition_table[board_hash] = alpha
        return alpha
    else:
        if stand_pat <= alpha:
            quiescence_transposition_table[board_hash] = alpha
            return alpha
        if beta > stand_pat:
            beta = stand_pat

        #print(f'quiescence search generating moves for black...')
        captures, _ = gen_legal_moves()
        ordered_captures = order_moves(captures)
        #print(f'ordered captures for black: {ordered_captures}')
        for move in ordered_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            make_move(piece, start_index, end_index)
            switch_player_turn()
            score = quiescence_search(alpha, beta, True, depth + 1, max_depth)
            restore_global_state(saved_state)
            if score <= alpha:
                quiescence_transposition_table[board_hash] = alpha
                return alpha
            if score < beta:
                beta = score
        quiescence_transposition_table[board_hash] = beta
        return beta