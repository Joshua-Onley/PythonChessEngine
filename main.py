import pygame
import move_logic
from move_logic import generate_pawn_moves, generate_bishop_moves, generate_rook_moves, generate_king_moves, generate_knight_moves, gen_legal_moves, generate_king_moves_bitboard, results_in_check
from precomputed_tables import BITBOARD_INDEX_TO_CHESS_SQUARE
from gui import draw_board_from_bitboards, display_winner
import globals
from bit_manipulation import clear_square, set_square
import cProfile
import pstats
import io
import alpha_beta_minimax
import quiescence_minimax
from globals import switch_player_turn
from utils import determine_what_piece_has_been_selected


pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
BOARD_HEIGHT = SQUARE_SIZE * ROWS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT_SIZE = 36
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Game')
font = pygame.font.Font(None, FONT_SIZE)

images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
for piece in pieces:
    images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece} copy.png'), (SQUARE_SIZE, SQUARE_SIZE))


def validate_move(piece, start_index, end_index):
    from move_logic import is_en_passant_legal

    move_generators = {
        'knight': generate_knight_moves,
        'king': generate_king_moves_bitboard,
        'pawn': generate_pawn_moves,
        'bishop': generate_bishop_moves,
        'rook': generate_rook_moves,
        'queen': lambda idx: generate_rook_moves(idx) | generate_bishop_moves(idx),
    }

    piece_type = piece.split('_')[1]

    if piece_type not in move_generators:
        return False

    potential_moves = move_generators[piece_type](start_index)

    if piece_type == 'pawn' and len(globals.game_states) > 2:
        en_passant_moves = is_en_passant_legal()
        if en_passant_moves:
            potential_moves |= en_passant_moves

    return (potential_moves >> end_index) & 1 == 1



def handle_move(piece, start_index, end_index):

    target_piece = determine_what_piece_has_been_selected(end_index, globals.piece_bitboards)

    if start_index == end_index:
        return None

    if target_piece:
        if (target_piece.startswith('white') and globals.player_turn == 'white') or (target_piece.startswith('black') and globals.player_turn == 'black'):
            return None

    if not validate_move(piece, start_index, end_index):
        return None

    from move_logic import results_in_check

    if results_in_check(piece, start_index, end_index):
        return None

    if piece == 'white_pawn' and (start_index == end_index - 9 or start_index == end_index - 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], start_index)
        globals.piece_bitboards['white_pawn'] = set_square(globals.piece_bitboards['white_pawn'], end_index)
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], end_index - 8)

    elif piece == 'white_pawn' and 56 <= end_index <= 63:
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], start_index)
        globals.piece_bitboards['white_queen'] = set_square(globals.piece_bitboards['white_queen'], end_index)

    elif piece == 'black_pawn' and (start_index == end_index + 9 or start_index == end_index + 7) and not (globals.all_pieces_bitboard >> end_index) & 1:
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], start_index)
        globals.piece_bitboards['black_pawn'] = set_square(globals.piece_bitboards['black_pawn'], end_index)
        globals.piece_bitboards['white_pawn'] = clear_square(globals.piece_bitboards['white_pawn'], end_index + 8)

    elif piece == 'black_pawn' and 0 <= end_index <= 7:
        globals.piece_bitboards['black_pawn'] = clear_square(globals.piece_bitboards['black_pawn'], start_index)
        globals.piece_bitboards['black_queen'] = set_square(globals.piece_bitboards['black_queen'], end_index)

    elif piece == 'white_king' and start_index == 4 and end_index == 6:
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 7)
        globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 5)
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 7)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 5)
        globals.white_king_has_moved = True

    elif piece == 'white_king' and start_index == 4 and end_index == 2:
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.piece_bitboards['white_rook'] = clear_square(globals.piece_bitboards['white_rook'], 0)
        globals.piece_bitboards['white_rook'] = set_square(globals.piece_bitboards['white_rook'], 3)
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, 0)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, 3)
        globals.white_king_has_moved = True

    elif piece == 'black_king' and start_index == 60 and end_index == 62:
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 63)
        globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 61)
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 63)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 61)
        globals.black_king_has_moved = True

    elif piece == 'black_king' and start_index == 60 and end_index == 58:
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.piece_bitboards['black_rook'] = clear_square(globals.piece_bitboards['black_rook'], 56)
        globals.piece_bitboards['black_rook'] = set_square(globals.piece_bitboards['black_rook'], 59)
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, 56)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, 59)
        globals.black_king_has_moved = True

    elif piece == 'white_king':
        globals.piece_bitboards['white_king'] = clear_square(globals.piece_bitboards['white_king'], start_index)
        globals.piece_bitboards['white_king'] = set_square(globals.piece_bitboards['white_king'], end_index)
        globals.white_king_has_moved = True

    elif piece == 'black_king':
        globals.piece_bitboards['black_king'] = clear_square(globals.piece_bitboards['black_king'], start_index)
        globals.piece_bitboards['black_king'] = set_square(globals.piece_bitboards['black_king'], end_index)
        globals.black_king_has_moved = True

    elif piece == 'white_rook' and start_index == 0:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.white_queenside_rook_has_moved = True

    elif piece == 'white_rook' and start_index == 7:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.white_kingside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 63:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.black_kingside_rook_has_moved = True

    elif piece == 'black_rook' and start_index == 56:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)
        globals.black_queenside_rook_has_moved = True


    else:
        globals.piece_bitboards[piece] = clear_square(globals.piece_bitboards[piece], start_index)
        globals.piece_bitboards[piece] = set_square(globals.piece_bitboards[piece], end_index)

    globals.all_pieces_bitboard = clear_square(globals.all_pieces_bitboard, start_index)
    globals.all_pieces_bitboard = set_square(globals.all_pieces_bitboard, end_index)

    if piece.startswith('white'):
        globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, start_index)
        globals.white_pieces_bitboard = set_square(globals.white_pieces_bitboard, end_index)
    else:
        globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, start_index)
        globals.black_pieces_bitboard = set_square(globals.black_pieces_bitboard, end_index)

    if target_piece:
        globals.piece_bitboards[target_piece] = clear_square(globals.piece_bitboards[target_piece], end_index)
        if target_piece.startswith('white'):
            globals.white_pieces_bitboard = clear_square(globals.white_pieces_bitboard, end_index)
        elif target_piece.startswith('black'):
            globals.black_pieces_bitboard = clear_square(globals.black_pieces_bitboard, end_index)

    globals.game_states.append(globals.piece_bitboards)
    globals.player_turn = 'black' if globals.player_turn == 'white' else 'white'

    return globals.all_pieces_bitboard, globals.white_pieces_bitboard, globals.black_pieces_bitboard, globals.piece_bitboards


def handle_piece_selection(index):

    if globals.player_turn == 'white' and (globals.white_pieces_bitboard >> index) & 1 == 0 and (globals.black_pieces_bitboard >> index) & 1 == 1:
            return False
    elif globals.player_turn == 'black' and (globals.black_pieces_bitboard >> index) & 1 == 0 and (globals.white_pieces_bitboard >> index) & 1 == 1:
            return False

    else:
        return True

import random
def choose_random_move(moves):
    if moves:
        return random.choice(moves)
    else:
        return None


def main():
    from computer_move import make_computer_move
    running = True
    selected_piece = None
    piece_selected = False
    piece = None

    draw_board_from_bitboards(WIN, globals.piece_bitboards['white_pawn'], globals.piece_bitboards['white_knight'],
                              globals.piece_bitboards['white_bishop'], globals.piece_bitboards['white_rook'],
                              globals.piece_bitboards['white_queen'], globals.piece_bitboards['white_king'],
                              globals.piece_bitboards['black_pawn'], globals.piece_bitboards['black_knight'],
                              globals.piece_bitboards['black_bishop'], globals.piece_bitboards['black_rook'],
                              globals.piece_bitboards['black_queen'], globals.piece_bitboards['black_king'], images)
    pygame.display.flip()

    while running:
        if globals.player_turn == 'black':

            make_computer_move('black')
            draw_board_from_bitboards(WIN, globals.piece_bitboards['white_pawn'],
                                      globals.piece_bitboards['white_knight'], globals.piece_bitboards['white_bishop'],
                                      globals.piece_bitboards['white_rook'], globals.piece_bitboards['white_queen'],
                                      globals.piece_bitboards['white_king'],
                                      globals.piece_bitboards['black_pawn'], globals.piece_bitboards['black_knight'],
                                      globals.piece_bitboards['black_bishop'], globals.piece_bitboards['black_rook'],
                                      globals.piece_bitboards['black_queen'], globals.piece_bitboards['black_king'],
                                      images)
            pygame.display.flip()
            globals.half_move_counter += 1
            globals.player_turn = 'white'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                col = (mouse_x // SQUARE_SIZE)
                row = 7 - (mouse_y // SQUARE_SIZE)
                index = row * 8 + col

                if globals.player_turn == 'white':
                    legal_moves = gen_legal_moves()
                    if len(legal_moves[0]) == 0 and len(legal_moves[1]) == 0:
                            display_winner('black')
                    if not piece_selected:
                        if handle_piece_selection(index):
                            selected_piece = index
                            piece_selected = True
                            piece = determine_what_piece_has_been_selected(index, globals.piece_bitboards)

                    else:
                        target_index = index
                        piece_selected = False

                        if piece:
                            if handle_move(piece, selected_piece, target_index):
                                draw_board_from_bitboards(WIN, globals.piece_bitboards['white_pawn'],
                                                          globals.piece_bitboards['white_knight'],
                                                          globals.piece_bitboards['white_bishop'],
                                                          globals.piece_bitboards['white_rook'],
                                                          globals.piece_bitboards['white_queen'],
                                                          globals.piece_bitboards['white_king'],
                                                          globals.piece_bitboards['black_pawn'],
                                                          globals.piece_bitboards['black_knight'],
                                                          globals.piece_bitboards['black_bishop'],
                                                          globals.piece_bitboards['black_rook'],
                                                          globals.piece_bitboards['black_queen'],
                                                          globals.piece_bitboards['black_king'], images)
                                pygame.display.flip()
                                selected_piece = None
                                piece = None
                                globals.half_move_counter += 1
                                globals.player_turn = 'black'
                            else:
                                print("Invalid move for white.")
    pygame.quit()


def f8_alt(x):
    return "%14.9f" % x
pstats.f8 = f8_alt

def profile_code():
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == '__main__':
    profile_code()

