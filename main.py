# main.py

import pygame
import sys

from Dameo.ia_dameo import get_ai_player
from Dameo.main_pygame import game_loop
from Dameo import menu 

def main_menu():
    pygame.init()
    pygame.font.init()

    menu_screen_width = 600
    menu_screen_height = 700
    screen = pygame.display.set_mode((menu_screen_width, menu_screen_height))
    pygame.display.set_caption("Dameo - Menu")

    difficulty_map = {0: "facil", 1: "medio", 2: "dificil"}

    while True:
        # Garante tamanho do ecrã do menu
        if screen.get_size() != (menu_screen_width, menu_screen_height):
             screen = pygame.display.set_mode((menu_screen_width, menu_screen_height))
             pygame.display.set_caption("Dameo - Menu")

        choice = menu.show_menu(screen)
        ai_opponent = None
        ai_white = None
        ai_black = None

        if choice == 1:  # Jogador vs Jogador
            screen = pygame.display.set_mode((800, 800))
            game_loop(mode_white="user", mode_black="user")
            # Após game_loop retornar, volta para o início do loop do menu
            continue
        elif choice == 2:  # Jogador vs IA
            difficulty_choice_index = menu.show_difficulty_menu(screen, "Escolha a Dificuldade da IA")
            if difficulty_choice_index != -1:
                difficulty_str = difficulty_map.get(difficulty_choice_index, "medio")
                ai_opponent = get_ai_player(difficulty_str)
            if ai_opponent:
                 screen = pygame.display.set_mode((800, 800))
                 game_loop(mode_white="user", mode_black="ai", ai_black=ai_opponent)
                 # Após game_loop retornar, volta para o início do loop do menu
                 continue

        elif choice == 3:  # IA vs IA
            difficulty_white_index = menu.show_difficulty_menu(screen, "Escolha Dificuldade IA Branca")
            if difficulty_white_index == -1: continue
            difficulty_black_index = menu.show_difficulty_menu(screen, "Escolha Dificuldade IA Preta")
            if difficulty_black_index == -1: continue

            difficulty_white_str = difficulty_map.get(difficulty_white_index, "medio")
            difficulty_black_str = difficulty_map.get(difficulty_black_index, "medio")
            ai_white = get_ai_player(difficulty_white_str)
            ai_black = get_ai_player(difficulty_black_str)

            print(f"Iniciando IA vs IA: Branco ({difficulty_white_str}) vs Preto ({difficulty_black_str})")
            screen = pygame.display.set_mode((800, 800))
            game_loop(mode_white="ai", mode_black="ai", ai_white=ai_white, ai_black=ai_black)
            # Após game_loop retornar, volta para o início do loop do menu
            continue

        elif choice == 4: # Regras
            menu.show_rules(screen)
            continue # Fica no loop do menu principal após mostrar as regras

        elif choice == 5: # Sair
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main_menu()