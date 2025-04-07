# main_pygame.py
import pygame
import sys
import time
import os  # Importa o módulo os
# Importa de game_logic apenas o necessário para iniciar
from Dameo.game_logic import create_board, WHITE_MAN, BLACK_MAN
# Importa a maioria das funções e constantes de utils
from Dameo import utils
from Dameo.utils import (
    apply_move,
    get_possible_moves,
    get_all_captures_for_player,  # Para verificar capturas obrigatórias do jogador
    has_moves,
    get_winner,
    BOARD_SIZE,
    EMPTY
)
# Importa funções de desenho
from Dameo.dameo_pygame import draw_board, COLOR_POSSIBLE_MOVE
# Importa IA
from Dameo.ia_dameo import get_ai_player

BOARD_SIZE_PIXELS = 600
INFO_AREA_HEIGHT = 80
SCREEN_HEIGHT = BOARD_SIZE_PIXELS + INFO_AREA_HEIGHT
SCREEN_WIDTH = BOARD_SIZE_PIXELS
FPS = 60
MESSAGE_DURATION = 2  # Segundos que a mensagem será exibida
MESSAGE_COLOR = (255, 0, 0)  # Vermelho para avisos
MESSAGE_BG_COLOR = (0, 0, 0, 180)  # Preto com alguma transparência
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (120, 120, 120)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
BUTTON_PADDING = 20
END_BUTTON_X = BUTTON_PADDING
END_BUTTON_Y = BOARD_SIZE_PIXELS + (INFO_AREA_HEIGHT - BUTTON_HEIGHT) // 2

END_BUTTON_RECT = pygame.Rect(END_BUTTON_X, END_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

class GameState:
    def __init__(self):
        self.board = create_board()
        self.current_player = WHITE_MAN
        self.selected_piece_pos = None
        self.possible_paths_for_selected = []
        self.mandatory_capture_paths = get_all_captures_for_player(self.board, self.current_player)
        self.message = None
        self.message_start_time = 0

game_state = GameState()

def center_window(width, height):
    """Centraliza a janela na tela."""
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    return screen

def show_message(message):
    """Exibe uma mensagem temporária na tela."""
    game_state.message = message
    game_state.message_start_time = time.time()

def display_game_message(screen, font):
    """Desenha a mensagem atual na área de informações."""
    if game_state.message and time.time() < game_state.message_start_time + MESSAGE_DURATION:
        message_surface = font.render(game_state.message, True, MESSAGE_COLOR)
        message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, BOARD_SIZE_PIXELS + INFO_AREA_HEIGHT // 2))

        # Desenha o fundo preto para a legibilidade
        bg_surface = pygame.Surface(message_rect.size, pygame.SRCALPHA)
        bg_surface.fill(MESSAGE_BG_COLOR)
        screen.blit(bg_surface, message_rect)

        screen.blit(message_surface, message_rect)

def draw_info_area(screen, font, mouse_pos):
    """Desenha a área de informações abaixo do tabuleiro."""
    pygame.draw.rect(screen, (50, 50, 50), (0, BOARD_SIZE_PIXELS, SCREEN_WIDTH, INFO_AREA_HEIGHT))
    draw_end_game_button(screen, font, mouse_pos)

def draw_end_game_button(screen, font, mouse_pos):
    """Desenha o botão de "Terminar Jogo"."""
    button_color = BUTTON_COLOR
    if END_BUTTON_RECT.collidepoint(mouse_pos):
        button_color = BUTTON_HOVER_COLOR
        pygame.draw.rect(screen, button_color, END_BUTTON_RECT, border_radius=5)
    else:
        pygame.draw.rect(screen, button_color, END_BUTTON_RECT, border_radius=5)

    text_surface = font.render("Terminar Jogo", True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=END_BUTTON_RECT.center)
    screen.blit(text_surface, text_rect)

def show_end_screen(screen, message, font):
    """Mostra uma mensagem de fim de jogo e espera por input."""
    screen.fill((0, 0, 0))
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text, text_rect)

    info = font.render("Clique para voltar ao menu", True, (180, 180, 180))
    info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(info, info_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False  # Sai da função e retorna ao menu

def game_loop(mode_white="user", mode_black="ai", ai_white=None, ai_black=None):
    screen = center_window(SCREEN_WIDTH, SCREEN_HEIGHT)  # Use a função para criar a tela
    pygame.display.set_caption("Dameo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)  # Fonte menor para a área de informações

    global game_state
    game_state = GameState()  # Reinicializa o estado do jogo

    square_size = BOARD_SIZE_PIXELS // BOARD_SIZE

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Verificar condição de fim de jogo ANTES do turno
        winner = get_winner(game_state.board)
        if winner:
            if winner == 'draw':
                message = "Empate!"
            else:
                winner_name = "Branco" if winner == WHITE_MAN else "Preto"
                message = f"Jogador {winner_name} venceu!"
            show_end_screen(screen, message, font)
            running = False
            continue

        # Verificar se jogador atual tem movimentos
        if not has_moves(game_state.board, game_state.current_player):
            opponent = BLACK_MAN if game_state.current_player == WHITE_MAN else WHITE_MAN
            winner_name = "Preto" if opponent == BLACK_MAN else "Branco"
            message = f"Jogador {winner_name} venceu (sem movimentos)!"
            show_end_screen(screen, message, font)
            running = False
            continue

        # Determinar se é a vez da IA
        is_ai_turn = (game_state.current_player == WHITE_MAN and mode_white == "ai") or \
                     (game_state.current_player == BLACK_MAN and mode_black == "ai")
        current_ai = ai_white if game_state.current_player == WHITE_MAN else ai_black

        # ---- Turno da IA ----
        if is_ai_turn and current_ai:
            pygame.display.set_caption(f"Dameo - Pensando... ({game_state.current_player.upper()})")
            pygame.event.pump()  # Processa eventos GUI

            start_time = time.time()
            chosen_path = current_ai.choose_move(game_state.board, game_state.current_player)
            end_time = time.time()

            if chosen_path:
                print(f"IA ({game_state.current_player}) escolheu: {chosen_path} em {end_time - start_time:.2f}s")
                start_row, start_col = chosen_path[0]
                # Obter tipo ANTES de mover, diretamente do tabuleiro
                piece_type = game_state.board[start_row][start_col]
                if piece_type == EMPTY:
                    print(f"ERRO GRAVE: IA tentou mover de uma casa vazia em ({start_row}, {start_col})")
                    # O que fazer aqui? Parar o jogo? Tentar outro movimento?
                    # Por agora, vamos apenas logar e talvez passar a vez
                    game_state.current_player = BLACK_MAN if game_state.current_player == WHITE_MAN else WHITE_MAN  # Passa a vez mesmo com erro?
                else:
                    apply_move(game_state.board, chosen_path, piece_type)  # Aplicar o movimento

                # Mudar jogador e limpar estado de seleção
                game_state.current_player = BLACK_MAN if game_state.current_player == WHITE_MAN else WHITE_MAN
                game_state.selected_piece_pos = None
                game_state.possible_paths_for_selected = []
                # Recalcular capturas obrigatórias para o próximo jogador humano/IA
                game_state.mandatory_capture_paths = get_all_captures_for_player(game_state.board, game_state.current_player)

            else:
                # Se a IA não encontrou movimento (pode acontecer em estados finais já tratados, ou erro na IA)
                print(f"AVISO: IA ({game_state.current_player}) não retornou movimento.")
                # A verificação no início do loop deve ter capturado estados sem movimento.
                # Se chegar aqui, pode ser um bug na IA ou estado inesperado.

            pygame.display.set_caption("Dameo")
            # Não precisa de 'continue', o loop vai naturalmente para desenho e próxima iteração

        # ---- Turno do Jogador Humano ----
        else:  # Só processa eventos se não for a vez da IA
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Botão esquerdo
                    x, y = pygame.mouse.get_pos()
                    clicked_pos_mouse = (x, y)

                    # Verificar se o botão de "Terminar Jogo" foi clicado (AGORA ANTES da verificação do tabuleiro)
                    if END_BUTTON_RECT.collidepoint(clicked_pos_mouse):
                        running = False
                        break # Sai do loop do jogo

                    clicked_row = y // square_size
                    clicked_col = x // square_size
                    clicked_board_pos = (clicked_row, clicked_col)

                    # Verificar se o clique está dentro dos limites do tabuleiro
                    if 0 <= clicked_row < BOARD_SIZE and 0 <= clicked_col < BOARD_SIZE:
                        # 1. Tentar executar um movimento se uma peça estiver selecionada
                        if game_state.selected_piece_pos and game_state.possible_paths_for_selected:
                            chosen_path = None
                            for path in game_state.possible_paths_for_selected:
                                if path[-1] == clicked_board_pos:  # Clicou no destino de um caminho possível?
                                    chosen_path = path
                                    break

                            if chosen_path:
                                # Se há capturas obrigatórias no tabuleiro, o movimento escolhido TEM que ser uma delas
                                is_valid_move = True
                                if game_state.mandatory_capture_paths:
                                    # O chosen_path tem que estar na lista de mandatory_capture_paths
                                    is_valid_move = any(p == chosen_path for p in game_state.mandatory_capture_paths)

                                if is_valid_move:
                                    # Aplicar o movimento escolhido
                                    piece_type = game_state.board[game_state.selected_piece_pos[0]][game_state.selected_piece_pos[1]]
                                    apply_move(game_state.board, chosen_path, piece_type)

                                    # Mudar jogador e limpar seleção/movimentos
                                    game_state.current_player = BLACK_MAN if game_state.current_player == WHITE_MAN else WHITE_MAN
                                    game_state.selected_piece_pos = None
                                    game_state.possible_paths_for_selected = []
                                    # Recalcular capturas obrigatórias para o próximo jogador
                                    game_state.mandatory_capture_paths = get_all_captures_for_player(game_state.board, game_state.current_player)
                                    # break # Sai do loop de eventos após fazer um movimento (importante)

                                else:
                                    show_message("Movimento inválido! Deve realizar uma captura obrigatória.")
                                    # Não faz o movimento, mantém seleção atual

                                # Sai do loop de eventos após tratar o clique num destino (válido ou inválido)
                                break

                        # 2. Tentar selecionar uma peça (se não executou movimento)
                        # Esta parte só executa se não clicou num destino válido acima
                        piece_at_click = game_state.board[clicked_row][clicked_col]
                        if piece_at_click != EMPTY and piece_at_click.lower() == game_state.current_player:
                            can_select = True
                            # Se há capturas obrigatórias, só pode selecionar peças que TÊM capturas
                            piece_has_mandatory_capture = False
                            if game_state.mandatory_capture_paths:
                                piece_has_mandatory_capture = any(path[0] == clicked_board_pos for path in game_state.mandatory_capture_paths)
                                if not piece_has_mandatory_capture:
                                    can_select = False  # Não pode selecionar esta se outras têm captura

                            if can_select:
                                game_state.selected_piece_pos = clicked_board_pos
                                # Obtém movimentos possíveis (serão capturas se houver para esta peça)
                                game_state.possible_paths_for_selected = get_possible_moves(game_state.board, clicked_row, clicked_col)
                                # Filtra para mostrar apenas capturas se houver capturas obrigatórias no geral
                                if game_state.mandatory_capture_paths:
                                    game_state.possible_paths_for_selected = [p for p in game_state.possible_paths_for_selected if len(p) > 2 or
                                                                           (len(p) == 2 and abs(p[0][0] - p[1][0]) >= 2 or abs(p[0][1] - p[1][1]) >= 2)]
                            else:
                                show_message("Seleção inválida! Captura obrigatória com outra peça.")
                                game_state.selected_piece_pos = None
                                game_state.possible_paths_for_selected = []
                        elif piece_at_click != EMPTY and piece_at_click.lower() != game_state.current_player:
                            show_message("Peça inválida! Não é a vez desse jogador.")
                            game_state.selected_piece_pos = None
                            game_state.possible_paths_for_selected = []
                        elif piece_at_click == EMPTY and game_state.selected_piece_pos:
                            show_message("Casa inválida para mover/capturar.")
                        elif piece_at_click == EMPTY and not game_state.selected_piece_pos:
                            pass # Clicou numa casa vazia sem ter selecionado nada
                    # Se o clique estiver fora do tabuleiro, não fazer nada ou logar um aviso (opcional)
                    # else:
                    #     print(f"Clique fora do tabuleiro em ({clicked_row}, {clicked_col})")

        # ---- Desenho ----
        screen.fill((0, 0, 0))
        draw_board(screen, game_state.board, game_state.selected_piece_pos, game_state.possible_paths_for_selected, square_size)
        draw_info_area(screen, font, mouse_pos)
        display_game_message(screen, font)  # Desenha a mensagem na área de informações
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()