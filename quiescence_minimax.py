import globals

minimax_call_count = 0

from hand_crafted_evaluation import evaluate_position
from move_logic import gen_legal_moves
from globals import save_global_state, restore_global_state
from debugging_functions import print_binary_as_bitboard
import numpy as np
leaf_node_count = 0
transposition_table = {}
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
    from computer_move import simulate_computer_move

    board_hash = hash_board_state()
    if board_hash in transposition_table:
        stored_eval, stored_depth = transposition_table[board_hash]
        if stored_depth >= depth:
            return stored_eval, None

    if depth == 0:
        leaf_node_count += 1
        return quiescence_search(alpha, beta, maximizing_player, depth, 1), None

    best_move = None
    if maximizing_player:
        captures, non_captures = gen_legal_moves()
        max_eval = float('-inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
            eval, _ = alpha_beta_quiescence_minimax(depth - 1, False, alpha, beta)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            restore_global_state(saved_state)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (max_eval, depth)
        return max_eval, best_move
    else:
        captures, non_captures = gen_legal_moves()
        min_eval = float('inf')
        for move in captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
            eval, _ = alpha_beta_quiescence_minimax(depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            restore_global_state(saved_state)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (min_eval, depth)
        return min_eval, best_move


def quiescence_search(alpha, beta, maximizing_player, depth, max_depth):
    global leaf_node_count
    from computer_move import simulate_computer_move

    # Check quiescence transposition table
    board_hash = hash_board_state()
    if board_hash in quiescence_transposition_table:
        print('this position was stored in the quiescence transposition table')
        stored_eval = quiescence_transposition_table[board_hash]
        return stored_eval

    # Evaluate the static position
    stand_pat = evaluate_position(globals.piece_bitboards, globals.white_pieces_bitboard,
                                  globals.black_pieces_bitboard, maximizing_player,
                                  globals.white_king_has_moved, globals.black_king_has_moved,
                                  globals.white_kingside_rook_has_moved,
                                  globals.white_queenside_rook_has_moved,
                                  globals.black_kingside_rook_has_moved,
                                  globals.black_queenside_rook_has_moved, globals.game_states)

    # Increment leaf node count when we evaluate a position
    leaf_node_count += 1

    # Return the static evaluation if the maximum depth is reached
    if depth >= max_depth:
        print('maximim quiescence depth reached ##############')
        return stand_pat

    if maximizing_player:
        if stand_pat >= beta:
            quiescence_transposition_table[board_hash] = beta
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        captures, _ = gen_legal_moves()  # Generate only capturing moves

        for move in captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
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

        captures, _ = gen_legal_moves()
        for move in captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
            score = quiescence_search(alpha, beta, True, depth + 1, max_depth)
            restore_global_state(saved_state)
            if score <= alpha:
                quiescence_transposition_table[board_hash] = alpha
                return alpha
            if score < beta:
                beta = score
        quiescence_transposition_table[board_hash] = beta
        return beta