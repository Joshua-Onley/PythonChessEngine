def determine_what_piece_has_been_selected(index, board):
    if (board['white_pawn'] >> index) & 1 == 1:
        return 'white_pawn'
    elif (board['white_knight'] >> index) & 1 == 1:
        return 'white_knight'
    elif (board['white_bishop'] >> index) & 1 == 1:
        return 'white_bishop'
    elif (board['white_rook'] >> index) & 1 == 1:
        return 'white_rook'
    elif (board['white_queen'] >> index) & 1 == 1:
        return 'white_queen'
    elif (board['white_king'] >> index) & 1 == 1:
        return 'white_king'
    elif (board['black_pawn'] >> index) & 1 == 1:
        return 'black_pawn'
    elif (board['black_knight'] >> index) & 1 == 1:
        return 'black_knight'
    elif (board['black_bishop'] >> index) & 1 == 1:
        return 'black_bishop'
    elif (board['black_rook'] >> index) & 1 == 1:
        return 'black_rook'
    elif (board['black_queen'] >> index) & 1 == 1:
        return 'black_queen'
    elif (board['black_king'] >> index) & 1 == 1:
        return 'black_king'