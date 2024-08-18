import pygame
import numpy as np
from gui import draw_board_from_bitboards  # Make sure this function is correctly implemented

pygame.init()
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (255, 255, 255)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Game')

images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
for piece in pieces:
    images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece} copy.png'), (SQUARE_SIZE, SQUARE_SIZE))


def show_board_sequence(board_states):
    current_index = 0
    num_states = len(board_states)

    while True:
        WIN.fill(WHITE)

        draw_board_from_bitboards(
            WIN,
            board_states[current_index]['white_pawn'], board_states[current_index]['white_knight'],
            board_states[current_index]['white_bishop'], board_states[current_index]['white_rook'],
            board_states[current_index]['white_queen'], board_states[current_index]['white_king'],
            board_states[current_index]['black_pawn'], board_states[current_index]['black_knight'],
            board_states[current_index]['black_bishop'], board_states[current_index]['black_rook'],
            board_states[current_index]['black_queen'], board_states[current_index]['black_king'],
            images
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % num_states
                elif event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % num_states
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return


if __name__ == "__main__":
    board_states = [{'white_pawn': np.uint64(9224498074286559234), 'black_pawn': np.uint64(576462401973584256),
     'white_knight': np.uint64(16416), 'black_knight': np.uint64(34359740416),
     'white_bishop': np.uint64(18014400656965632), 'black_bishop': np.uint64(1073741832),
     'white_rook': np.uint64(4294967300), 'black_rook': np.uint64(40960), 'white_queen': np.uint64(512),
     'black_queen': np.uint64(33554432), 'white_king': np.uint64(72057594037927936),
     'black_king': np.uint64(8796093022208)}]
    show_board_sequence(board_states)
