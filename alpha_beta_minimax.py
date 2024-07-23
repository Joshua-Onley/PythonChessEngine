import globals

minimax_call_count = 0

from hand_crafted_evaluation import evaluate_position
from move_logic import gen_legal_moves
from globals import save_global_state, restore_global_state
from debugging_functions import print_binary_as_bitboard, print_binary_as_chessboard
import numpy as np
from move_ordering import order_moves


leaf_node_count = 0
transposition_table = {}

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


def alpha_beta_minimax(depth, maximizing_player, alpha, beta):
    global leaf_node_count
    from computer_move import simulate_computer_move

    # Check the transposition table
    board_hash = hash_board_state()
    if board_hash in transposition_table:
        stored_eval, stored_depth = transposition_table[board_hash]
        if stored_depth >= depth:
            print('this position was stored in the transposition table')
            return stored_eval, None

    if depth == 0:
        leaf_node_count += 1
        eval = evaluate_position(globals.piece_bitboards, globals.white_pieces_bitboard,
                                 globals.black_pieces_bitboard, maximizing_player,
                                 globals.white_king_has_moved, globals.black_king_has_moved,
                                 globals.white_kingside_rook_has_moved,
                                 globals.white_queenside_rook_has_moved,
                                 globals.black_kingside_rook_has_moved,
                                 globals.black_queenside_rook_has_moved, globals.game_states)
        return eval, None

    best_move = None
    if maximizing_player:
        print('all pieces bitboard')
        print_binary_as_chessboard(globals.all_pieces_bitboard)
        print('\n')
        print('pawns bitboards')
        print_binary_as_chessboard(globals.piece_bitboards['white_pawn'] | globals.piece_bitboards['black_pawn'])
        captures, non_captures = gen_legal_moves()
        ordered_captures = order_moves(captures)
        max_eval = float('-inf')
        for move in ordered_captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
            eval, _ = alpha_beta_minimax(depth - 1, False, alpha, beta)
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
        print('all pieces bitboard')
        print_binary_as_chessboard(globals.all_pieces_bitboard)
        print('\n')
        print('pawns bitboards')
        print_binary_as_chessboard(globals.piece_bitboards['white_pawn'] | globals.piece_bitboards['black_pawn'])
        print('\n')
        captures, non_captures = gen_legal_moves()
        ordered_captures = order_moves(captures)
        min_eval = float('inf')
        for move in ordered_captures + non_captures:
            piece, start_index, end_index = move
            saved_state = save_global_state()
            simulate_computer_move(piece, start_index, end_index)
            eval, _ = alpha_beta_minimax(depth - 1, True, alpha, beta)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            restore_global_state(saved_state)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (min_eval, depth)
        return min_eval, best_move

