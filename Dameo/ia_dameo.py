# ia_dameo.py
import random
import math # Para +/- infinito
# Importa funções necessárias de utils
from Dameo import utils # type: ignore
from Dameo.utils import ( # type: ignore
    BOARD_SIZE, EMPTY, WHITE_MAN, BLACK_MAN, WHITE_KING, BLACK_KING, # Constantes
    get_all_captures_for_player, get_possible_moves, is_game_over, get_winner, # Lógica Jogo
    apply_move, count_pieces, is_within_bounds, get_piece_directions, is_king, # Utilitários IA
    promote_pawn # Necessário para verificar promoção
)

# --- Constantes para Heurísticas (usadas por evaluate_board) ---
MOBILITY_WEIGHT = 0.1
CENTER_CONTROL_WEIGHT = 0.05
KING_ADVANCEMENT_WEIGHT = 0.08
CENTER_START = 2
CENTER_END = BOARD_SIZE - 1 - CENTER_START
SAFETY_WEIGHT = 0.04
STRUCTURE_WEIGHT = 0.03

class AIPlayer:
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def is_safe(self, board, r, c, player):
        """Verifica se uma peça na posição (r, c) está segura de captura imediata."""
        opponent = BLACK_MAN if player == WHITE_MAN else WHITE_MAN
        opponent_king = BLACK_KING if player == WHITE_MAN else WHITE_KING
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Todas as direções diagonais

        for dr, dc in directions:
            # Verificar captura simples do oponente
            nr1, nc1 = r + dr, c + dc
            nr2, nc2 = r + 2 * dr, c + 2 * dc

            if utils.is_within_bounds(nr1, nc1) and utils.is_within_bounds(nr2, nc2):
                opponent_piece = board[nr1][nc1]
                landing_square = board[nr2][nc2]

                if landing_square == EMPTY and opponent_piece != EMPTY and opponent_piece.lower() == opponent.lower():
                    # Verificar se o oponente pode capturar esta peça
                    opponent_directions = utils.get_piece_directions(opponent_piece, capture_only=True)
                    for odr, odc in opponent_directions:
                        if odr == -dr and odc == -dc: # Direção oposta à da nossa peça
                            return False
        return True

    def count_adjacent_pieces(self, board, r, c, player):
        """Conta o número de peças adjacentes diagonalmente do mesmo jogador."""
        count = 0
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if utils.is_within_bounds(nr, nc) and board[nr][nc] != EMPTY and board[nr][nc].lower() == player.lower():
                count += 1
        return count

    def quick_evaluate_move(self, board, path, piece_type):
        """Avalia rapidamente um movimento para fins de ordenação."""
        score = 0
        start_pos = path[0]
        end_pos = path[-1]

        # Pontuação alta para capturas
        if len(path) > 2:  # Indica uma captura (ou múltipla captura)
            score += 10

        # Pontuação alta para promoção
        if (piece_type == WHITE_MAN and end_pos[0] == 0) or \
           (piece_type == BLACK_MAN and end_pos[0] == utils.BOARD_SIZE - 1):
            score += 8

        # Pequena pontuação para avançar para o centro
        center_r = utils.BOARD_SIZE // 2
        center_c = utils.BOARD_SIZE // 2
        start_dist_center = abs(start_pos[0] - center_r) + abs(start_pos[1] - center_c)
        end_dist_center = abs(end_pos[0] - center_r) + abs(end_pos[1] - center_c)
        if end_dist_center < start_dist_center:
            score += 1

        # Pequena pontuação para mover para uma casa segura (simplificado)
        # Podemos verificar se a casa de destino não está adjacente a um oponente
        opponent = BLACK_MAN if piece_type.lower() == WHITE_MAN.lower() else WHITE_MAN
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        is_destination_attacked = False
        for dr, dc in directions:
            nr, nc = end_pos[0] + dr, end_pos[1] + dc
            if utils.is_within_bounds(nr, nc) and board[nr][nc] != EMPTY and board[nr][nc].lower() == opponent.lower():
                is_destination_attacked = True
                break
        if not is_destination_attacked:
            score += 1

        return score

    def minimax(self, board, current_player, depth, alpha=-math.inf, beta=math.inf, possible_paths=None):
        """
        Algoritmo Minimax com poda Alpha-Beta e ordenação de movimentos.
        MODIFICADO: Escolhe aleatoriamente entre os melhores movimentos com a mesma avaliação.
        """
        opponent = BLACK_MAN if current_player == WHITE_MAN else WHITE_MAN

        if depth == 0 or not utils.has_moves(board, current_player):
             return self.evaluate_board(board), None

        if possible_paths is None:
             paths_to_evaluate = self.get_all_normal_paths(board, current_player)
             if not paths_to_evaluate:
                 paths_to_evaluate = get_all_captures_for_player(board, current_player)
        else:
             paths_to_evaluate = possible_paths

        if not paths_to_evaluate:
             return self.evaluate_board(board), None

        # Ordenar os movimentos (apenas para profundidades maiores)
        if depth > 1:  # Evitar ordenar na camada folha
            paths_to_evaluate.sort(key=lambda path: self.quick_evaluate_move(board, path, board[path[0][0]][path[0][1]]), reverse=(current_player == WHITE_MAN))

        best_paths_list = []

        if current_player == WHITE_MAN: # Maximizando
            max_eval = -math.inf

            for path in paths_to_evaluate:
                temp_board = [row[:] for row in board]
                start_r, start_c = path[0]
                piece_type = board[start_r][start_c]
                if piece_type == EMPTY or piece_type.lower() != current_player.lower(): continue

                utils.apply_move(temp_board, path, piece_type)
                evaluation, _ = self.minimax(temp_board, opponent, depth - 1, alpha, beta)

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_paths_list = [path]
                elif evaluation == max_eval:
                    best_paths_list.append(path)

                alpha = max(alpha, evaluation)
                if beta <= alpha: break

            chosen_path = random.choice(best_paths_list) if best_paths_list else None
            return max_eval, chosen_path

        else: # Minimizando (Preto)
            min_eval = math.inf

            for path in paths_to_evaluate:
                temp_board = [row[:] for row in board]
                start_r, start_c = path[0]
                piece_type = board[start_r][start_c]
                if piece_type == EMPTY or piece_type.lower() != current_player.lower(): continue

                utils.apply_move(temp_board, path, piece_type)
                evaluation, _ = self.minimax(temp_board, opponent, depth - 1, alpha, beta)

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_paths_list = [path]
                elif evaluation == min_eval:
                    best_paths_list.append(path)

                beta = min(beta, evaluation)
                if beta <= alpha: break

            chosen_path = random.choice(best_paths_list) if best_paths_list else None
            return min_eval, chosen_path

    def choose_move(self, board, current_player):
        """
        Escolhe o melhor movimento (caminho) para o jogador atual.
        Retorna um caminho (lista de coordenadas) ou None.
        """
        possible_capture_paths = get_all_captures_for_player(board, current_player)
        best_path = None

        # --- Lógica de Captura ---
        if possible_capture_paths:
            if self.difficulty == 'facil':
                best_path = random.choice(possible_capture_paths)
            elif self.difficulty == 'medio':
                 # Profundidade MÉDIO = 3
                 _, best_path = self.minimax(board, current_player, depth=3, possible_paths=possible_capture_paths)
            else:  # difícil
                # Profundidade DIFÍCIL = 4
                _, best_path = self.minimax(board, current_player, depth=4, possible_paths=possible_capture_paths)

        # --- Lógica de Movimento Normal ---
        else:
            if self.difficulty == 'facil':
                # Lógica 'facil' com avaliação simples e prioridade a promoções
                all_normal_paths = self.get_all_normal_paths(board, current_player)
                if not all_normal_paths: return None

                promoting_moves = []
                for path in all_normal_paths:
                    start_pos, end_pos = path
                    piece = board[start_pos[0]][start_pos[1]]
                    if (piece == WHITE_MAN or piece == BLACK_MAN) and \
                       promote_pawn(piece, end_pos[0]) != piece:
                           promoting_moves.append(path)

                if promoting_moves:
                    best_path = random.choice(promoting_moves)
                else:
                    best_score = -math.inf if current_player == WHITE_MAN else math.inf
                    best_moves_list = []
                    for path in all_normal_paths:
                        temp_board = [row[:] for row in board]
                        start_r, start_c = path[0]
                        piece_type = board[start_r][start_c]
                        if piece_type == EMPTY: continue
                        utils.apply_move(temp_board, path, piece_type)
                        score = self.evaluate_board(temp_board)

                        is_better = (current_player == WHITE_MAN and score > best_score) or \
                                    (current_player == BLACK_MAN and score < best_score)
                        is_equal = (score == best_score)

                        if is_better:
                            best_score = score
                            best_moves_list = [path]
                        elif is_equal:
                            best_moves_list.append(path)

                    if best_moves_list:
                        best_path = random.choice(best_moves_list)
                    else:
                        best_path = random.choice(all_normal_paths) # Fallback

            elif self.difficulty == 'medio':
                 # Profundidade MÉDIO = 3
                 _, best_path = self.minimax(board, current_player, depth=3)
            else:  # difícil
                 # Profundidade DIFÍCIL = 4
                 _, best_path = self.minimax(board, current_player, depth=4)

        # --- Fallbacks e Retorno ---
        if best_path is None and utils.has_moves(board, current_player):
             # print(f"Warning: IA {self.difficulty} ({current_player}) retornou None, fallback final para aleatório.")
             all_moves = get_all_captures_for_player(board, current_player)
             if not all_moves:
                 all_moves = self.get_all_normal_paths(board, current_player)
             if all_moves:
                 best_path = random.choice(all_moves)

        return best_path

    # --- Funções Auxiliares (calculate_mobility, etc.) ---
    # (mantêm-se iguais à versão anterior)
    def _get_normal_moves_for_piece(self, board, r, c):
        piece = board[r][c]
        moves = []
        if piece == EMPTY: return moves
        move_directions = utils.get_piece_directions(piece, capture_only=False)
        if utils.is_king(piece):
            for dx, dy in move_directions:
                for i in range(1, utils.BOARD_SIZE):
                    nr, nc = r + i * dx, c + i * dy
                    if not utils.is_within_bounds(nr, nc): break
                    if board[nr][nc] == EMPTY: moves.append((nr, nc))
                    else: break
        else:
            for dx, dy in move_directions:
                 nr, nc = r + dx, c + dy
                 if utils.is_within_bounds(nr, nc) and board[nr][nc] == EMPTY:
                     moves.append((nr, nc))
        return moves

    def calculate_mobility(self, board, player):
        total_moves = 0
        player_char = player.lower()
        for r in range(utils.BOARD_SIZE):
            for c in range(utils.BOARD_SIZE):
                piece = board[r][c]
                if piece != EMPTY and piece.lower() == player_char:
                    total_moves += len(self._get_normal_moves_for_piece(board, r, c))
        return total_moves

    def get_all_normal_paths(self, board, player):
        normal_paths = []
        player_char = player.lower()
        for r in range(utils.BOARD_SIZE):
            for c in range(utils.BOARD_SIZE):
                piece = board[r][c]
                start_pos = (r, c)
                if piece != EMPTY and piece.lower() == player_char:
                    destinations = self._get_normal_moves_for_piece(board, r, c)
                    for end_pos in destinations:
                        normal_paths.append([start_pos, end_pos])
        return normal_paths

    def random_normal_move(self, board, current_player):
        possible_normal_paths = self.get_all_normal_paths(board, current_player)
        if possible_normal_paths:
            return random.choice(possible_normal_paths)
        return None

    def evaluate_board(self, board):
        """ Função de avaliação heurística com heurísticas adicionadas. """
        winner = get_winner(board)
        if winner == WHITE_MAN: return 10000 + count_pieces(board)[WHITE_MAN]
        if winner == BLACK_MAN: return -10000 - count_pieces(board)[BLACK_MAN]
        if winner == 'draw': return 0

        score = 0
        piece_values = {WHITE_MAN: 1, BLACK_MAN: -1, WHITE_KING: 3, BLACK_KING: -3}
        white_pawn_advancement = 0
        black_pawn_advancement = 0
        white_king_advancement = 0
        black_king_advancement = 0
        white_center_control = 0
        black_center_control = 0
        white_safety = 0
        black_safety = 0
        white_structure = 0
        black_structure = 0

        for r in range(utils.BOARD_SIZE):
            for c in range(utils.BOARD_SIZE):
                piece = board[r][c]
                if piece == EMPTY: continue

                score += piece_values.get(piece, 0)

                if piece == WHITE_MAN:
                    white_pawn_advancement += (utils.BOARD_SIZE - 1 - r)
                    if self.is_safe(board, r, c, WHITE_MAN): white_safety += 1
                    white_structure += self.count_adjacent_pieces(board, r, c, WHITE_MAN)
                elif piece == BLACK_MAN:
                    black_pawn_advancement += r
                    if self.is_safe(board, r, c, BLACK_MAN): black_safety += 1
                    black_structure += self.count_adjacent_pieces(board, r, c, BLACK_MAN)
                elif piece == WHITE_KING:
                    white_king_advancement += (utils.BOARD_SIZE - 1 - r)
                    if self.is_safe(board, r, c, WHITE_MAN): white_safety += 1 # Damas também precisam de segurança
                    white_structure += self.count_adjacent_pieces(board, r, c, WHITE_MAN)
                elif piece == BLACK_KING:
                    black_king_advancement += r
                    if self.is_safe(board, r, c, BLACK_MAN): black_safety += 1 # Damas também precisam de segurança
                    black_structure += self.count_adjacent_pieces(board, r, c, BLACK_MAN)

                is_center = (CENTER_START <= r <= CENTER_END and CENTER_START <= c <= CENTER_END)
                if is_center:
                    if piece.lower() == WHITE_MAN.lower(): white_center_control += 1
                    elif piece.lower() == BLACK_MAN.lower(): black_center_control += 1

        score += white_pawn_advancement * 0.05
        score -= black_pawn_advancement * 0.05
        score += white_king_advancement * KING_ADVANCEMENT_WEIGHT
        score -= black_king_advancement * KING_ADVANCEMENT_WEIGHT
        score += white_center_control * CENTER_CONTROL_WEIGHT
        score -= black_center_control * CENTER_CONTROL_WEIGHT
        score += white_safety * SAFETY_WEIGHT
        score -= black_safety * SAFETY_WEIGHT
        score += white_structure * STRUCTURE_WEIGHT / 2 # Dividir por 2 porque cada adjacência conta para duas peças
        score -= black_structure * STRUCTURE_WEIGHT / 2

        white_mobility = self.calculate_mobility(board, WHITE_MAN)
        black_mobility = self.calculate_mobility(board, BLACK_MAN)
        score += (white_mobility - black_mobility) * MOBILITY_WEIGHT

        return score

# --- Função Fábrica ---
def get_ai_player(difficulty):
    """Função fábrica para criar instâncias da IA com diferentes dificuldades."""
    return AIPlayer(difficulty)

# Adiciona as funções minimax e quick_evaluate_move à classe AIPlayer
AIPlayer.minimax = AIPlayer.minimax
AIPlayer.quick_evaluate_move = AIPlayer.quick_evaluate_move