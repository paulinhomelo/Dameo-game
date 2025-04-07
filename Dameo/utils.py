# utils.py

import time # Para limite de tempo opcional no run_headless_game

BOARD_SIZE = 8
EMPTY = '.'
WHITE_MAN = 'w'
BLACK_MAN = 'b'
WHITE_KING = 'W'
BLACK_KING = 'B'

# --- Basic Helpers ---
def is_within_bounds(x, y):
    """Verifica se as coordenadas (x, y) estão dentro do tabuleiro."""
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def get_opponent(piece):
    """Retorna as peças do oponente."""
    piece_lower = piece.lower()
    if piece_lower == WHITE_MAN:
        return (BLACK_MAN, BLACK_KING)
    elif piece_lower == BLACK_MAN:
        return (WHITE_MAN, WHITE_KING)
    return tuple() # Retorna tuplo vazio se a peça for inválida

def is_king(piece):
    """Verifica se a peça é um rei."""
    return piece == WHITE_KING or piece == BLACK_KING

def promote_pawn(piece, row):
    """Promove um peão a rei se atingir a linha oposta."""
    if piece == WHITE_MAN and row == 0:
        return WHITE_KING
    elif piece == BLACK_MAN and row == BOARD_SIZE - 1:
        return BLACK_KING
    return piece

def get_piece_directions(piece, capture_only=False):
    """
    Returns relevant directions.
    MODIFICADO: Agora permite movimento normal diagonal para a frente para peões.
    """
    if piece == WHITE_MAN:
        # Pawns move forward (row decreases)
        forward_orth = (-1, 0)
        forward_diag_left = (-1, -1)
        forward_diag_right = (-1, 1)
        if capture_only:
            # Captura usa todas as 3 direções frontais
            return [forward_orth, forward_diag_left, forward_diag_right]
        else:
            # Movimento normal AGORA inclui ortogonal E diagonal para a frente
            return [forward_orth, forward_diag_left, forward_diag_right] # <-- MUDANÇA AQUI
    elif piece == BLACK_MAN:
        # Pawns move forward (row increases)
        forward_orth = (1, 0)
        forward_diag_left = (1, -1)
        forward_diag_right = (1, 1)
        if capture_only:
            # Captura usa todas as 3 direções frontais
            return [forward_orth, forward_diag_left, forward_diag_right]
        else:
            # Movimento normal AGORA inclui ortogonal E diagonal para a frente
            return [forward_orth, forward_diag_left, forward_diag_right] # <-- MUDANÇA AQUI
    elif is_king(piece):
        # Kings use all 8 directions for move and capture
        return [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    return []

# --- Core Movement Logic ---

def _get_capture_paths_recursive(board, start_pos, piece, current_path, captured_on_path):
    """Internal recursive helper for finding capture sequences."""
    possible_sequences = []
    (start_x, start_y) = start_pos
    opponent_pieces = get_opponent(piece)

    if is_king(piece):
        # --- King Capture Logic ---
        init_capture_directions = get_piece_directions(piece, capture_only=True) # All 8 directions
        for dx, dy in init_capture_directions:
            potential_capture_pos = None
            landing_squares = []

            # Scan along the direction
            for i in range(1, BOARD_SIZE):
                check_x, check_y = start_x + i * dx, start_y + i * dy
                if not is_within_bounds(check_x, check_y): break # Off board
                piece_at_check = board[check_x][check_y]

                if potential_capture_pos is None: # Searching for capture target
                    if piece_at_check == EMPTY: continue # Path clear
                    elif piece_at_check in opponent_pieces:
                        potential_capture_pos = (check_x, check_y)
                        if potential_capture_pos in captured_on_path: # Cannot recapture same piece
                            potential_capture_pos = None; break
                        continue # Continue scan for landing squares
                    else: break # Blocked by friendly piece
                else: # Searching for landing squares after capture target
                    if piece_at_check == EMPTY: landing_squares.append((check_x, check_y))
                    else: break # Path blocked

            if potential_capture_pos and landing_squares: # If capture possible and landing possible
                for land_pos in landing_squares:
                    next_path = current_path + [land_pos]
                    next_captured = captured_on_path | {potential_capture_pos}
                    continuations = _get_capture_paths_recursive(board, land_pos, piece, next_path, next_captured)
                    if continuations: possible_sequences.extend(continuations)
                    else: possible_sequences.append(next_path) # End of this branch
    else:
        # --- Pawn Capture Logic ---
        pawn_capture_directions = get_piece_directions(piece, capture_only=True) # Get FORWARD dirs
        for dx, dy in pawn_capture_directions:
            # Ensure direction is actually forward for this pawn
            is_forward_direction = (piece == WHITE_MAN and dx == -1) or (piece == BLACK_MAN and dx == 1)
            if not is_forward_direction: continue # Skip if somehow wrong direction was included

            # Check short adjacent jump
            capture_x, capture_y = start_x + dx, start_y + dy
            land_x, land_y = start_x + 2 * dx, start_y + 2 * dy
            capture_pos = (capture_x, capture_y)

            if is_within_bounds(capture_x, capture_y) and \
               is_within_bounds(land_x, land_y) and \
               board[capture_x][capture_y] in opponent_pieces and \
               board[land_x][land_y] == EMPTY and \
               capture_pos not in captured_on_path:
                land_pos = (land_x, land_y)
                next_path = current_path + [land_pos]
                next_captured = captured_on_path | {capture_pos}
                continuations = _get_capture_paths_recursive(board, land_pos, piece, next_path, next_captured)
                if continuations: possible_sequences.extend(continuations)
                else: possible_sequences.append(next_path) # End of this branch

    return possible_sequences


def get_all_capture_sequences(board, r, c):
    """
    Finds all maximal capture sequences starting from (r, c).
    Returns a list of paths (lists of coordinates).
    """
    piece = board[r][c]
    if piece == EMPTY: return []
    start_pos = (r, c)
    initial_path = [start_pos]
    initial_captured = frozenset()
    all_sequences = _get_capture_paths_recursive(board, start_pos, piece, initial_path, initial_captured)

    if not all_sequences: return []
    valid_capture_sequences = [seq for seq in all_sequences if len(seq) > 1] # Must have >1 step
    if not valid_capture_sequences: return []

    max_len = max(len(seq) for seq in valid_capture_sequences)
    return [seq for seq in valid_capture_sequences if len(seq) == max_len]


def get_possible_moves(board, r, c):
    """
    Gets all valid moves for the piece at (r, c), prioritizing mandatory captures for this piece.
    Returns a list of paths (list of coordinates).
    """
    piece = board[r][c]
    start_pos = (r, c)
    if piece == EMPTY: return []

    # 1. Check for mandatory captures initiated by THIS piece
    capture_paths = get_all_capture_sequences(board, r, c)
    if capture_paths:
        return capture_paths # Mandatory captures take priority

    # 2. If no captures for this piece, find its normal moves
    normal_move_paths = []
    # Use directions for non-capture moves (includes diagonal forward for pawns now)
    move_directions = get_piece_directions(piece, capture_only=False)

    if is_king(piece): # King slides
        for dx, dy in move_directions: # All 8 directions
            for i in range(1, BOARD_SIZE):
                nr, nc = r + i * dx, c + i * dy
                if not is_within_bounds(nr, nc): break
                if board[nr][nc] == EMPTY: normal_move_paths.append([start_pos, (nr, nc)])
                else: break # Blocked
    else: # Pawn moves one step (includes orth & diag forward now)
        for dx, dy in move_directions:
             nr, nc = r + dx, c + dy
             if is_within_bounds(nr, nc) and board[nr][nc] == EMPTY:
                 normal_move_paths.append([start_pos, (nr, nc)])

    return normal_move_paths

# --- Apply Move ---

def find_captured_piece_pos(start_pos, end_pos, board, piece_moved):
    """Helper to find the position of the captured piece during a jump step."""
    sx, sy = start_pos
    ex, ey = end_pos
    dx_total = ex - sx
    dy_total = ey - sy

    # Check short jump (distance 2)
    if abs(dx_total) <= 2 and abs(dy_total) <= 2 and (abs(dx_total) == 2 or abs(dy_total) == 2):
        # Check if it's a valid distance-2 jump pattern
        if (abs(dx_total) == 2 and dy_total == 0) or \
           (dx_total == 0 and abs(dy_total) == 2) or \
           (abs(dx_total) == 2 and abs(dy_total) == 2):
            cap_x, cap_y = sx + dx_total // 2, sy + dy_total // 2
            if is_within_bounds(cap_x, cap_y) and board[cap_x][cap_y] in get_opponent(piece_moved):
                return (cap_x, cap_y)

    # Check King's long jump
    if is_king(piece_moved) and (abs(dx_total) > 2 or abs(dy_total) > 2):
        step_x = 1 if ex > sx else -1 if ex < sx else 0
        step_y = 1 if ey > sy else -1 if ey < sy else 0
        # Check if move is along a straight line
        if (ex == sx or ey == sy or abs(ex - sx) == abs(ey - sy)) and (step_x != 0 or step_y != 0):
            captured_pos = None
            opponent_pieces = get_opponent(piece_moved)
            cx, cy = sx + step_x, sy + step_y
            while (cx, cy) != (ex, ey): # Scan from start to end
                 if not is_within_bounds(cx, cy): break
                 piece_at_check = board[cx][cy]
                 if piece_at_check != EMPTY:
                      if piece_at_check in opponent_pieces:
                           if captured_pos is not None: return None # >1 piece jumped
                           captured_pos = (cx, cy)
                      else: return None # Jumped friendly
                 cx += step_x; cy += step_y
            return captured_pos # Return pos if exactly one opponent found
    return None # Not a capture jump


def apply_move(board, path, piece_type):
    """
    Applies a move (path) to the board. Modifies 'board' directly.
    piece_type: Type of the piece at the START of the move.
    """
    if not path or len(path) < 2: return
    start_pos = path[0]
    end_pos = path[-1]

    # 1. Get original piece type from board (safer) and clear start
    original_piece = EMPTY
    if is_within_bounds(start_pos[0], start_pos[1]):
        original_piece = board[start_pos[0]][start_pos[1]]
        board[start_pos[0]][start_pos[1]] = EMPTY
    else: return

    # Use passed type as fallback if start was somehow empty (shouldn't happen)
    if original_piece == EMPTY: original_piece = piece_type
    if original_piece == EMPTY: return # Still no piece type, cannot proceed

    # 2. Find and remove captured pieces along the path
    captured_pieces_positions = set()
    # Use a temp board reflecting state *before* captures for checks
    temp_board_for_check = [row[:] for row in board]
    if is_within_bounds(start_pos[0], start_pos[1]): # Put piece back for check context
         temp_board_for_check[start_pos[0]][start_pos[1]] = original_piece

    for i in range(len(path) - 1):
        step_start = path[i]; step_end = path[i+1]
        captured_pos = find_captured_piece_pos(step_start, step_end, temp_board_for_check, original_piece)
        if captured_pos:
             captured_pieces_positions.add(captured_pos)
             # Update temp board to reflect capture for subsequent checks in chain
             if is_within_bounds(captured_pos[0], captured_pos[1]):
                 temp_board_for_check[captured_pos[0]][captured_pos[1]] = EMPTY

    # Remove identified pieces from the actual board
    for r_cap, c_cap in captured_pieces_positions:
         if is_within_bounds(r_cap, c_cap) and (r_cap, c_cap) != end_pos:
              board[r_cap][c_cap] = EMPTY

    # 3. Place piece at end position and promote if applicable
    final_r, final_c = end_pos
    if is_within_bounds(final_r, final_c):
         final_piece = promote_pawn(original_piece, final_r) # Promote based on original type
         board[final_r][final_c] = final_piece

# --- Game State Functions ---

def get_all_captures_for_player(board, player):
    """Finds all mandatory (longest) capture sequences for a player."""
    all_capture_paths = []
    player_char = player.lower()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece != EMPTY and piece.lower() == player_char:
                sequences = get_all_capture_sequences(board, r, c) # Gets max captures for this piece
                all_capture_paths.extend(sequences)

    if not all_capture_paths: return []
    # Filter globally for the overall longest sequences
    max_len = max(len(path) for path in all_capture_paths)
    return [path for path in all_capture_paths if len(path) == max_len]


def has_moves(board, player):
    """Checks if a player has any valid move."""
    # Check captures first (mandatory)
    if get_all_captures_for_player(board, player): return True
    # If no captures, check for any normal move
    player_char = player.lower()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece != EMPTY and piece.lower() == player_char:
                # get_possible_moves returns [] if only captures exist but they aren't for THIS piece
                # or returns normal moves if no captures exist globally.
                if get_possible_moves(board, r, c): return True
    return False


def is_game_over(board, current_player):
    """Checks if the current player has no moves."""
    return not has_moves(board, current_player)


def get_winner(board):
    """Determines the winner ('w', 'b') or 'draw' or None if ongoing."""
    white_has_pieces = any(cell.lower() == WHITE_MAN for row in board for cell in row)
    black_has_pieces = any(cell.lower() == BLACK_MAN for row in board for cell in row)
    if not white_has_pieces: return BLACK_MAN # Black wins if White has no pieces
    if not black_has_pieces: return WHITE_MAN # White wins if Black has no pieces

    white_can_move = has_moves(board, WHITE_MAN)
    black_can_move = has_moves(board, BLACK_MAN)

    if not white_can_move and not black_can_move: return 'draw' # Stalemate
    if not white_can_move: return BLACK_MAN # White has pieces but cannot move
    if not black_can_move: return WHITE_MAN # Black has pieces but cannot move

    # Could add other draw conditions here (e.g., repetition, 50-move rule)
    return None # Game continues


def count_pieces(board):
    """Counts total pieces per player."""
    counts = {WHITE_MAN: 0, BLACK_MAN: 0}
    for row in board:
        for piece in row:
            if piece.lower() == WHITE_MAN: counts[WHITE_MAN] += 1
            elif piece.lower() == BLACK_MAN: counts[BLACK_MAN] += 1
    return counts

# --- Headless Game Runner (for AI vs AI tests) ---
# Note: Needs create_board from game_logic or defined here if standalone
from Dameo.game_logic import create_board # Assuming game_logic still has create_board

def run_headless_game(ai_white, ai_black, max_moves=300):
    """Runs a game between two AIs without graphics."""
    board = create_board()
    current_player = WHITE_MAN
    move_count = 0
    # Optional: Add history tracking for repetition draw
    # board_history = {} # Store board state tuples as keys, count as values

    while move_count < max_moves:
        # Check for win/loss/stalemate based on pieces and mobility
        game_winner = get_winner(board)
        if game_winner: return game_winner # 'w', 'b', or 'draw'

        # # Optional: Repetition Draw Check
        # current_board_tuple = tuple(map(tuple, board))
        # history_count = board_history.get(current_board_tuple, 0) + 1
        # board_history[current_board_tuple] = history_count
        # if history_count >= 3:
        #     # print("Draw by 3-fold repetition.")
        #     return 'draw'

        # Select AI and get move
        current_ai = ai_white if current_player == WHITE_MAN else ai_black
        chosen_path = current_ai.choose_move(board, current_player)

        # Validate and apply move
        if chosen_path:
            start_row, start_col = chosen_path[0]
            piece_type = board[start_row][start_col] # Get piece from board
            # Basic validation
            if piece_type == EMPTY or piece_type.lower() != current_player:
                print(f"FATAL ERROR in run_headless_game: IA {current_player} chose invalid path {chosen_path} from board state.")
                # print_board(board) # Print board state for debugging
                # Consider this a loss for the AI that made the error
                return BLACK_MAN if current_player == WHITE_MAN else WHITE_MAN
            apply_move(board, chosen_path, piece_type)
        else:
             # If has_moves was true but choose_move returned None, it's an AI error
             print(f"FATAL ERROR in run_headless_game: IA {current_player} failed to return a move when moves were available.")
             # Consider this a loss for the AI that made the error
             return BLACK_MAN if current_player == WHITE_MAN else WHITE_MAN

        # Switch player, increment count
        current_player = BLACK_MAN if current_player == WHITE_MAN else WHITE_MAN
        move_count += 1

    # Max moves reached
    # print(f"Draw by reaching max_moves limit ({max_moves}).")
    return 'draw'