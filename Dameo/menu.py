# menu.py
import pygame
import sys

# --- Função para Exibir as Regras (com texto simplificado) ---
def show_rules(screen):
    if not pygame.font.get_init(): pygame.font.init()

    rule_font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 45)
    back_font = pygame.font.Font(None, 35)

    WIDTH, HEIGHT = screen.get_size()
    screen.fill((30, 30, 30))

    # --- TEXTO DAS REGRAS SIMPLIFICADO ---
    rules_text = [
        "Regras Básicas do Dameo:",
        "",
        "Objetivo: Capturar todas as peças inimigas ou bloquear",
        "          totalmente os seus movimentos.",
        "",
        "Movimento:",
        " - Peões: 1 casa para frente (vertical ou diagonal).",
        " - Reis (Damas): Qualquer casa livre em qualquer direção.",
        "",
        "Captura (Obrigatória!):",
        " - Saltar sobre peça inimiga para casa vazia a seguir.",
        " - Peões só capturam para a frente.",
        " - Reis capturam em qualquer direção.",
        " - Capturas em cadeia são possíveis.",
        " - Se houver várias capturas, deve escolher a que",
        "   captura MAIS peças.",
        "",
        "Promoção:",
        " - Peão que chega à última linha vira Rei.",
        "",
        "Vitória:",
        " - Oponente sem peças ou sem movimentos.",
    ]
    # --- FIM DO TEXTO SIMPLIFICADO ---

    # Título
    title_surface = title_font.render("Regras do Dameo", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title_surface, title_rect)

    # Renderizar linhas de regras
    line_height = rule_font.get_linesize()
    start_y = title_rect.bottom + 30
    current_y = start_y
    for line in rules_text:
        # Verifica se ainda cabe na tela (com margem inferior)
        if current_y + line_height > HEIGHT - 60:
            break # Para de desenhar se não couber mais
        line_surface = rule_font.render(line, True, (220, 220, 220))
        line_rect = line_surface.get_rect(topleft=(40, current_y))
        screen.blit(line_surface, line_rect)
        current_y += line_height

    # Mensagem para voltar
    back_surface = back_font.render("Clique em qualquer lugar para Voltar", True, (255, 255, 0))
    back_rect = back_surface.get_rect(center=(WIDTH // 2, HEIGHT - 40))
    screen.blit(back_surface, back_rect)

    pygame.display.flip()

    # Loop de espera para voltar
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                 waiting = False
        pygame.time.Clock().tick(30)

# --- Função show_menu (sem alterações nesta versão) ---
def show_menu(screen):
    if not pygame.font.get_init(): pygame.font.init()
    font = pygame.font.Font(None, 40)
    title_font = pygame.font.Font(None, 60)
    options = ["Jogador vs Jogador", "Jogador vs IA", "IA vs IA", "Regras", "Sair"]
    buttons = []
    WIDTH, HEIGHT = screen.get_size()
    title_surface = title_font.render("Dameo", True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))
    button_height = 55
    button_width = 300
    start_y = title_rect.bottom + 60
    button_spacing = 75
    for i, option in enumerate(options):
        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (WIDTH // 2, start_y + i * button_spacing)
        text_surface = font.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        option_index = i + 1
        buttons.append({'rect': rect, 'text_surface': text_surface, 'text_rect': text_rect, 'option_index': option_index})
    selected_button_index = None
    while True:
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()
        selected_button_index = None
        screen.blit(title_surface, title_rect)
        for i, button in enumerate(buttons):
             if button['rect'].collidepoint(mouse_pos):
                 selected_button_index = i
        for i, button in enumerate(buttons):
            button_color = (80, 80, 80) if selected_button_index == i else (50, 50, 50)
            pygame.draw.rect(screen, button_color, button['rect'], border_radius=10)
            screen.blit(button['text_surface'], button['text_rect'])
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            return button['option_index']

# --- Função show_difficulty_menu (sem alterações nesta versão) ---
def show_difficulty_menu(screen, title_text="Escolha a Dificuldade da IA"):
    if not pygame.font.get_init(): pygame.font.init()
    font = pygame.font.Font(None, 40)
    title_font = pygame.font.Font(None, 50)
    options = ["Fácil", "Médio", "Difícil", "Voltar"]
    buttons = []
    WIDTH, HEIGHT = screen.get_size()
    title_surface = title_font.render(title_text, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 100))
    button_height = 60
    button_width = 250
    start_y = title_rect.bottom + 80
    button_spacing = 80
    for i, option in enumerate(options):
        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (WIDTH // 2, start_y + i * button_spacing)
        text_surface = font.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        return_value = i if i < len(options) - 1 else -1
        buttons.append({'rect': rect, 'text_surface': text_surface, 'text_rect': text_rect, 'return_value': return_value})
    selected_button_index = None
    while True:
        screen.fill((30, 30, 30))
        mouse_pos = pygame.mouse.get_pos()
        selected_button_index = None
        screen.blit(title_surface, title_rect)
        for i, button in enumerate(buttons):
            if button['rect'].collidepoint(mouse_pos):
                selected_button_index = i
        for i, button in enumerate(buttons):
            button_color = (80, 80, 80) if selected_button_index == i else (50, 50, 50)
            pygame.draw.rect(screen, button_color, button['rect'], border_radius=10)
            screen.blit(button['text_surface'], button['text_rect'])
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            return button['return_value']