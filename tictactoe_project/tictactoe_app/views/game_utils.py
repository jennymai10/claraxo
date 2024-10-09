import random
from django.http import JsonResponse

def check_win(board):
    """
    Check if there is a winning combination on the board.

    This function iterates through all possible winning combinations (rows, columns, and diagonals)
    to determine if either 'X' or 'O' has won the game. It returns the winner if there is one.

    Args:
        board (dict): A dictionary representing the current state of the Tic-Tac-Toe board.
                      Keys are positions ('a3', 'b3', etc.), and values are either 'X', 'O', or ''.

    Returns:
        str or None: Returns 'X' or 'O' if there is a winner, otherwise returns None.
    """
    # Define all possible winning combinations
    winning_combinations = [
        ['a3', 'b3', 'c3'],  # Top row
        ['a2', 'b2', 'c2'],  # Middle row
        ['a1', 'b1', 'c1'],  # Bottom row
        ['a3', 'a2', 'a1'],  # Left column
        ['b3', 'b2', 'b1'],  # Middle column
        ['c3', 'c2', 'c1'],  # Right column
        ['a3', 'b2', 'c1'],  # Left diagonal
        ['c3', 'b2', 'a1']   # Right diagonal
    ]

    # Check each winning combination to see if all three positions are the same and not empty
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] and board[combo[1]] == board[combo[2]] and board[combo[0]] != '':
            return board[combo[0]]  # Return 'X' or 'O' if we have a winner
    return None # No winner found

def initialize_board():
    """
    Initialize a new Tic-Tac-Toe board.

    This function creates and returns a dictionary representing an empty Tic-Tac-Toe board.
    Each position on the board is represented by a key (e.g., 'a3'), and its value is an empty string.

    Returns:
        dict: A dictionary representing an empty Tic-Tac-Toe board.
    """
    return {
        'a3': '', 'b3': '', 'c3': '',
        'a2': '', 'b2': '', 'c2': '',
        'a1': '', 'b1': '', 'c1': ''
    }

def generate_ai_move(board, unoccupied, model):
    """
    Generate the AI move using an external model (Generative AI).

    This function uses an external AI model to generate the next move for the AI player ('O').
    It sends the current board state and the list of unoccupied squares to the model and receives
    a recommended move. If the model response is invalid or unavailable, it falls back to a random move.

    Args:
        board (dict): The current state of the Tic-Tac-Toe board.
        unoccupied (list): A list of unoccupied squares on the board.
        model (object): The external AI model used to generate the move.

    Returns:
        str: The chosen move for the AI, represented by a board position (e.g., 'a3').
    """
    # Create a prompt for the AI model describing the current board state and unoccupied squares
    prompt = f"""
    Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
    Squares occupied by X: [{', '.join([key for key, value in board.items() if value == 'X'])}]
    Squares occupied by O: [{', '.join([key for key, value in board.items() if value == 'O'])}]
    Unoccupied squares: [{', '.join(unoccupied)}]
    You are playing as O. Your chosen move should be one of the unoccupied squares above. In your response, return exactly one string from {unoccupied}, representing your chosen move.
    """
    try:
        ai_move = ''
        attempts = 0
        max_attempts = 5 # Maximum number of attempts to get a valid move from the model

        # Try to get a valid move from the AI model up to the maximum number of attempts
        while ai_move not in unoccupied and attempts < max_attempts:
            try:
                response = model.generate_content(prompt)  # Generate content using the AI model
                ai_move = response.text.strip()  # Extract the move from the model's response
            except ValueError:
                ai_move = ''  # Fallback in case of invalid response
            attempts += 1

        # If no valid move was generated, fall back to a random move
        if ai_move not in unoccupied:
            return random.choice(unoccupied), 1  # Return a random move and a flag indicating fallback
        else:
            return ai_move, 0
    except Exception as e:
        print(f"Error generating AI move: {e}")
        return random.choice(unoccupied), 1

def game_end_handler(board, game, winner, request):
    """
    Handle game ending scenarios such as a winner or a draw.

    This function updates the game state when the game ends, either because a player has won
    or because the board is full (resulting in a draw). It sets the winner, marks the game as
    completed, and saves these changes to the database. It also updates the session with the
    game result and returns a response to redirect the user to the result page.

    Args:
        board (dict): The current state of the Tic-Tac-Toe board.
        game (object): The game object representing the current game session.
        winner (str or None): The winner of the game ('X', 'O', or 'Draw').
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response with a status and redirect URL to the result page.
    """
    # If there is a winner, update the game object and session, and redirect to result page
    if winner:
        game.winner = winner  # Set the winner in the game object
        game.completed = True  # Mark the game as completed
        game.save()  # Save the updated game state to the database
        request.session['winner'] = winner  # Store the winner in the session
        return winner #JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

    # If the board is full and there is no winner, it's a draw
    if '' not in board.values():
        game.winner = 'Draw'  # Set the winner as 'Draw'
        game.completed = True  # Mark the game as completed
        game.save()  # Save the updated game state to the database
        request.session['winner'] = 'Draw'  # Store the draw result in the session
        return "Draw" # JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

    # If the game is not over, return None
    return None