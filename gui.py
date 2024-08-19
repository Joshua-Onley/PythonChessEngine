
import pygame


WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
BOARD_HEIGHT = SQUARE_SIZE * ROWS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 100, 15)
FONT_SIZE = 36
WIN = pygame.display.set_mode((WIDTH, HEIGHT))


def draw_board_from_bitboards(win, wp, wn, wb, wr, wq, wk, bp, bn, bb, br, bq, bk, images):
    colors = [WHITE, GRAY]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    piece_bitboards = {
        'wp': wp, 'wn': wn, 'wb': wb, 'wr': wr, 'wq': wq, 'wk': wk,
        'bp': bp, 'bn': bn, 'bb': bb, 'br': br, 'bq': bq, 'bk': bk
    }

    for piece, bitboard in piece_bitboards.items():
        for i in range(64):
            if (bitboard >> i) & 1:
                row = 7 - (i // 8)
                col = i % 8
                win.blit(images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


def display_winner(winner):
    font = pygame.font.SysFont(None, 200)
    text_surface = font.render(f"{winner} wins!", True, pygame.Color('green'))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.delay(5000)


def display_draw():
    font = pygame.font.SysFont(None, 200)
    text_surface = font.render(f"Stalemate!", True, pygame.Color('red'))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    WIN.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.delay(5000)