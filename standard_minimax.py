import globals
from PST_evaluation import evaluate
from move_logic import gen_legal_moves
from globals import switch_player_turn, save_global_state, restore_global_state
leaf_node_count = 0

leaf_node_evaluations_retrieved_from_transposition_table = 0
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

def minimax(depth, maximizing_player, alpha, beta):
    from computer_move import make_move
    global leaf_node_count
    global leaf_node_evaluations_retrieved_from_transposition_table

    board_hash = hash_board_state()
    if board_hash in transposition_table:
        stored_eval, stored_depth = transposition_table[board_hash]
        if stored_depth >= depth:
            leaf_node_evaluations_retrieved_from_transposition_table += 1
            return stored_eval, None

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
        transposition_table[board_hash] = (max_eval, depth)
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
        transposition_table[board_hash] = (min_eval, depth)
        return min_eval, best_move