# Dameo with AI

## Description

Dameo game with a Pygame graphical interface and an AI based on the Minimax algorithm. It allows playing against the AI with different difficulty levels, playing against another human, or simulating matches between two AIs. Includes a menu for mode selection and a screen with the basic game rules.

## Game Rules (Simplified)

* **Objective:** Capture all of the opponent's pieces or block all of their moves.
* **Movement:**
    * Men: Move 1 square forward (diagonally or vertically).
    * Kings: Move any number of free squares in any direction.
* **Capture:** Mandatory by jumping over an adjacent enemy piece to an empty square. Chain captures are possible. Men only capture forwards.
* **Promotion:** Men that reach the last row become Kings.
* **Victory:** Opponent has no pieces or no legal moves.

## Requirements

* Python 3.x
* Pygame (version tested with the latest available via pip)

    ```bash
    pip install pygame
    ```

## How to Run the Program

1.  Make sure you have the requirements installed.
2.  Navigate to the `dameo_game` directory.
3.  Run the `main.py` file from your terminal:

    ```bash
    python3 main.py
    ```

## Possible Modifications

* **AI Difficulty Levels:** The AI difficulty (Easy, Medium, Hard) is defined in the `Dameo/ia_dameo.py` file and selectable through the game menu. You can adjust the Minimax search depth for each level to change the AI's strength.
* **AI Heuristics:** The weight constants for the different heuristics (mobility, center control, safety, etc.) in the `Dameo/ia_dameo.py` file can be modified to alter the AI's evaluation strategy.
* **Colors and Appearance:** The colors of the board, pieces, and other visual elements can be changed in the `Dameo/dameo_pygame.py` file.
* **Rules (in code):** The game rules logic is mainly in the `Dameo/utils.py` file. Modifications to the movement, capture, or promotion functions can alter the game rules.

## Authors

This project was developed by Henrique Pilão and Paulo Pereira.

## Other Relevant Information

* The AI uses the Minimax algorithm with Alpha-Beta pruning for decision-making.
* Capturing is mandatory for the human player.
* The game offers modes for Player vs Player, Player vs AI, and AI vs AI.
* An interactive menu allows the selection of modes and AI difficulty.
* The basic game rules can be viewed through a menu option.
* An "End Game" button allows exiting the current match and returning to the menu.