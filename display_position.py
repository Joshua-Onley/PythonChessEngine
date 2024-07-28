import pygame
import numpy as np
from gui import draw_board_from_bitboards  # Make sure this function is correctly implemented

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (255, 255, 255)

# Set up display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess Game')

# Load piece images
images = {}
pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
for piece in pieces:
    images[piece] = pygame.transform.scale(pygame.image.load(f'images/{piece} copy.png'), (SQUARE_SIZE, SQUARE_SIZE))


def show_board_sequence(board_states):
    """Render the chessboard and pieces, allowing navigation through multiple board states."""
    current_index = 0
    num_states = len(board_states)

    while True:
        # Clear the screen
        WIN.fill(WHITE)

        # Draw the current board state
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

        # Update the display
        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:  # Scroll forward
                    current_index = (current_index + 1) % num_states
                elif event.key == pygame.K_LEFT:  # Scroll backward
                    current_index = (current_index - 1) % num_states
                elif event.key == pygame.K_ESCAPE:  # Quit the program
                    pygame.quit()
                    return


if __name__ == "__main__":
    # Example board states (12 bitboards as placeholders)
    board_states = [{
'white_pawn': np.uint64(0x000000081000e700),
'black_pawn': np.uint64(0x002d500002800000),
'white_knight': np.uint64(0x0000001000040000),
'black_knight': np.uint64(0x0000220000000000),
'white_bishop': np.uint64(0x0000000000001800),
'black_bishop': np.uint64(0x0040010000000000),
'white_rook': np.uint64(0x0000000000000081),
'black_rook': np.uint64(0x8100000000000000),
'white_queen': np.uint64(0x0000000000200000),
'black_queen': np.uint64(0x0010000000000000),
'white_king': np.uint64(0x0000000000000010),
'black_king': np.uint64(0x1000000000000000)
}]
    show_board_sequence(board_states)
