# dameo_pygame.py
import pygame
# Importa constantes do módulo utils
from .utils import WHITE_MAN, BLACK_MAN, WHITE_KING, BLACK_KING, BOARD_SIZE, EMPTY

# Cores (pode ajustar)
COLOR_LIGHT = (238, 238, 210)  # Bege claro
COLOR_DARK = (118, 150, 86)   # Verde escuro
COLOR_WHITE = (248, 248, 248) # Quase branco
COLOR_BLACK = (80, 80, 80)    # Cinza escuro
COLOR_SELECTED_BORDER = (255, 255, 0, 200) # Amarelo semi-transparente para borda de seleção
COLOR_POSSIBLE_MOVE = (0, 50, 200, 100) # Azul semi-transparente para movimentos possíveis

def draw_board(screen, board, selected_piece_pos, possible_paths, square_size):
    """Desenha o tabuleiro, as peças, a seleção e os movimentos possíveis."""

    # 1. Desenhar o tabuleiro (quadrados)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = COLOR_LIGHT if (row + col) % 2 == 0 else COLOR_DARK
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

    # 2. Desenhar as peças
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece == EMPTY:
                continue

            center_x = col * square_size + square_size // 2
            center_y = row * square_size + square_size // 2
            radius = int(square_size * 0.4) # Raio como percentagem do quadrado

            # Cor base da peça
            piece_color = COLOR_WHITE if piece.lower() == WHITE_MAN else COLOR_BLACK
            # Cor do contorno/sombra (opcional, para efeito 3D)
            shadow_color = tuple(max(0, c-40) for c in piece_color) # Cor ligeiramente mais escura

            # Desenhar sombra/borda (opcional)
            pygame.draw.circle(screen, shadow_color, (center_x + 2, center_y + 2), radius)
            # Desenhar peça principal
            pygame.draw.circle(screen, piece_color, (center_x, center_y), radius)

            # Desenhar indicação de Rei
            if piece == WHITE_KING or piece == BLACK_KING:
                # Coroa/Estrela simples no centro
                king_color = COLOR_BLACK if piece == WHITE_KING else COLOR_WHITE # Cor contrastante
                # Desenha um ponto central ou uma pequena estrela/coroa
                pygame.draw.circle(screen, king_color, (center_x, center_y), radius // 3)

    # 3. Desenhar a seleção (borda amarela na casa selecionada)
    if selected_piece_pos:
        row, col = selected_piece_pos
        sel_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
        pygame.draw.rect(sel_surface, COLOR_SELECTED_BORDER, (0, 0, square_size, square_size), 4) # Borda
        screen.blit(sel_surface, (col * square_size, row * square_size))

    # 4. Desenhar os movimentos possíveis (círculos nos destinos)
    if possible_paths:
        move_radius = square_size // 5 # Raio menor para indicar destino
        for path in possible_paths:
            if not path or len(path) < 2: continue # Ignora caminhos inválidos
            end_row, end_col = path[-1] # Pega a coordenada final do caminho

            move_surface = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            pygame.draw.circle(move_surface, COLOR_POSSIBLE_MOVE,
                               (square_size // 2, square_size // 2), move_radius)
            screen.blit(move_surface, (end_col * square_size, end_row * square_size))