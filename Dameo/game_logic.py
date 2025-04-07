# game_logic.py
# Importa utils que contém a maior parte da lógica
from Dameo import utils

# Constantes ainda úteis aqui para inicialização e símbolos
EMPTY = '.'
WHITE_MAN = 'w'
BLACK_MAN = 'b'
WHITE_KING = 'W'
BLACK_KING = 'B'
BOARD_SIZE = 8 # Ou utils.BOARD_SIZE  (perguntar Henrique!!!!)

PIECE_SYMBOLS = {
    '.': ".",
    'w': "⛀",
    'b': "⛂",
    'W': "⛁",
    'B': "⛃"
}

def create_board():
    """Cria o tabuleiro inicial de Dameo."""
    board = [[EMPTY for _ in range(utils.BOARD_SIZE)] for _ in range(utils.BOARD_SIZE)]

    # Peças Pretas (Black)
    for col in range(utils.BOARD_SIZE):
        board[0][col] = BLACK_MAN
    for col in range(1, utils.BOARD_SIZE - 1):
        board[1][col] = BLACK_MAN
    for col in range(2, utils.BOARD_SIZE - 2):
        board[2][col] = BLACK_MAN

    # Peças Brancas (White)
    for col in range(2, utils.BOARD_SIZE - 2):
        board[5][col] = WHITE_MAN
    for col in range(1, utils.BOARD_SIZE - 1):
        board[6][col] = WHITE_MAN
    for col in range(utils.BOARD_SIZE):
        board[7][col] = WHITE_MAN

    return board

def print_board(board):
    """Imprime o tabuleiro no terminal com símbolos unicode."""
    print("  " + " ".join(str(i) for i in range(utils.BOARD_SIZE)))
    for i, row in enumerate(board):
        print(f"{i} " + " ".join(PIECE_SYMBOLS.get(cell, cell) for cell in row))

# Todas as outras funções de lógica de jogo foram movidas ou
# estão agora implementadas corretamente em utils.py