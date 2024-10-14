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
    # Calculate heuristic scores for all available moves
    move_scores = evaluate_all_moves(board, unoccupied)
    # Create a string representation of the move scores to pass into the prompt
    move_scores_str = ', '.join([f"{move}: {score}" for move, score in move_scores.items()])
    print(f"Move scores: {move_scores}")
    # Create a prompt for the AI model describing the current board state and unoccupied squares
    prompt = f"""
    ### Board Layout:
    The Tic-Tac-Toe board is indexed using a chess-like notation where:
    - 'a' refers to the left column, 'b' refers to the middle column, and 'c' refers to the right column.
    - '3' refers to the top row, '2' refers to the middle row, and '1' refers to the bottom row.
    The board is laid out as follows:
    a3 | b3 | c3
    a2 | b2 | c2
    a1 | b1 | c1
    ### Winning Combinations:
    To win the game, you need to place three 'O's in one of the following patterns:
    1. Horizontal wins: ['a1', 'a2', 'a3'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3']
    2. Vertical wins: ['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], ['a3', 'b3', 'c3']
    3. Diagonal wins: ['a1', 'b2', 'c3'], ['a3', 'b2', 'c1']
    ### Decision Strategy:
    1. **Immediate Win**: If you can win in this move, choose the move that completes one of the winning combinations listed above.
    2. **Block the Opponent**: If 'X' can win on their next move, block them by placing your 'O' in the square that prevents them from completing a winning combination.
    3. **Strategic Setup for Future Wins**: 
    - If neither you nor 'X' can win immediately, focus on setting yourself up for a future win by positioning your 'O' in a strong spot (especially the center 'b2' or corners 'a3', 'a1', 'c3', 'c1').
    - Think about creating two potential winning lines at once, which forces 'X' to block only one, giving you the advantage on your next turn.
    4. **Avoid Bad Moves**: Avoid moves that give 'X' an opportunity to create a fork or win on their next turn. Focus on disrupting their plans while advancing your strategy.
    You are playing Tic-Tac-Toe as 'O'. Your goal is to win the game. Here is the current state of the board:
    Squares occupied by X: [{', '.join([key for key, value in board.items() if value == 'X'])}]
    Squares occupied by O: [{', '.join([key for key, value in board.items() if value == 'O'])}]
    Unoccupied squares: [{', '.join(unoccupied)}]
    ### Heuristic Scores for Available Moves: {move_scores_str}
    Make sure your chosen move aligns with the strategy above and maximizes your chances of winning while minimizing 'X's advantage.
    Your response should be exactly one valid move string from the list of available squares: {unoccupied}, representing your chosen move.
    """
    try:
        max_retries = 5  # Allow a maximum of 5 retries
        attempts = 0

        while attempts < max_retries:
            try:
                # Send a single request to the model with the pre-calculated heuristic scores and strategy advice
                response = model.generate_content(prompt)
                ai_move = response.text.strip()  # Extract the move from the model's response

                # If the AI returns a valid move, return it
                if ai_move in unoccupied:
                    print(f"AI chose move '{ai_move}' with heuristic score {move_scores[ai_move]}.")
                    return ai_move, 0

                # Increment the number of attempts if the move is invalid
                attempts += 1
                print(f"Attempt {attempts}: Invalid move '{ai_move}'. Retrying...")

            except Exception as e:
                print(f"Error generating AI move on attempt {attempts + 1}: {e}")
                attempts += 1

        # If max retries are exceeded, fallback to a random move
        print(f"Max retries exceeded. Choosing a random move.")
        return random.choice(unoccupied), 1

    except Exception as e:
        print(f"Error generating AI move: {e}")
        return random.choice(unoccupied), 1

def generate_ai_move_with_logging(board, unoccupied, model):
    """
    Generate the AI move with logging of the prompt and response for monitoring purposes.

    Args:
        board (dict): The current state of the Tic-Tac-Toe board.
        unoccupied (list): A list of unoccupied squares on the board.
        model (object): The external AI model used to generate the move.

    Returns:
        str: The chosen move for the AI, represented by a board position (e.g., 'a3').
        str: The prompt log for the researcher.
        str: The AI response log for the researcher.
    """
    # Calculate heuristic scores for all available moves
    move_scores = evaluate_all_moves(board, unoccupied)
    # Create a string representation of the move scores to pass into the prompt
    move_scores_str = ', '.join([f"{move}: {score}" for move, score in move_scores.items()])
    print(f"Move scores: {move_scores}")
    # Generate the prompt as before
    prompt = f"""
    ### Board Layout:
    The Tic-Tac-Toe board is indexed using a chess-like notation where:
    - 'a' refers to the left column, 'b' refers to the middle column, and 'c' refers to the right column.
    - '3' refers to the top row, '2' refers to the middle row, and '1' refers to the bottom row.
    The board is laid out as follows:
    a3 | b3 | c3
    a2 | b2 | c2
    a1 | b1 | c1
    ### Winning Combinations:
    To win the game, you need to place three 'O's in one of the following patterns:
    1. Horizontal wins: ['a1', 'a2', 'a3'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3']
    2. Vertical wins: ['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], ['a3', 'b3', 'c3']
    3. Diagonal wins: ['a1', 'b2', 'c3'], ['a3', 'b2', 'c1']
    ### Decision Strategy:
    1. **Immediate Win**: If you can win in this move, choose the move that completes one of the winning combinations listed above.
    2. **Block the Opponent**: If 'X' can win on their next move, block them by placing your 'O' in the square that prevents them from completing a winning combination.
    3. **Strategic Setup for Future Wins**: 
    - If neither you nor 'X' can win immediately, focus on setting yourself up for a future win by positioning your 'O' in a strong spot (especially the center 'b2' or corners 'a3', 'a1', 'c3', 'c1').
    - Think about creating two potential winning lines at once, which forces 'X' to block only one, giving you the advantage on your next turn.
    4. **Avoid Bad Moves**: Avoid moves that give 'X' an opportunity to create a fork or win on their next turn. Focus on disrupting their plans while advancing your strategy.
    You are playing Tic-Tac-Toe as 'O'. Your goal is to win the game. Here is the current state of the board:
    Squares occupied by X: [{', '.join([key for key, value in board.items() if value == 'X'])}]
    Squares occupied by O: [{', '.join([key for key, value in board.items() if value == 'O'])}]
    Unoccupied squares: [{', '.join(unoccupied)}]
    ### Heuristic Scores for Available Moves: {move_scores_str}
    Make sure your chosen move aligns with the strategy above and maximizes your chances of winning while minimizing 'X's advantage.
    Your response should be exactly one valid move string from the list of available squares: {unoccupied}, representing your chosen move.
    """
    try:
        # Log the prompt sent to Gemini
        prompt_log = prompt

        # Send the prompt to the AI and capture the response
        response = model.generate_content(prompt)
        ai_move = response.text.strip()

        # Log the response from Gemini
        ai_response_log = response.text

        # Validate the AI's move
        if ai_move in unoccupied:
            return ai_move, 0, prompt_log, ai_response_log  # Return valid move and logs

        # Fall back if AI gives an invalid move
        return random.choice(unoccupied), 1, prompt_log, ai_response_log

    except Exception as e:
        print(f"Error generating AI move: {e}")
        return random.choice(unoccupied), 1, prompt_log, "Error: Failed to get a response from AI"


def evaluate_move(board, move, is_ai_turn=True):
    """
    Heuristic function to evaluate a move.
    
    Args:
        board (dict): The current board state.
        move (str): The move being evaluated (e.g., 'a3').
        is_ai_turn (bool): True if evaluating for AI (O), False if for player (X).
    
    Returns:
        int: The heuristic score of the move.
    """
    score = 0
    
    # Create a copy of the board with the move applied
    board_copy = board.copy()
    board_copy[move] = 'O' if is_ai_turn else 'X'  # Assume 'O' is AI, 'X' is the player
    
    # Define winning patterns
    win_patterns = [
        ['a1', 'a2', 'a3'], 
        ['b1', 'b2', 'b3'], 
        ['c1', 'c2', 'c3'], 
        ['a1', 'b1', 'c1'], 
        ['a2', 'b2', 'c2'], 
        ['a3', 'b3', 'c3'], 
        ['a1', 'b2', 'c3'], 
        ['a3', 'b2', 'c1']  
    ]
    
    # Check if the move results in a win
    for pattern in win_patterns:
        if all(board_copy[square] == ('O' if is_ai_turn else 'X') for square in pattern):
            score += 100  # High score for winning move
    
    # Check if the move blocks the opponent from winning
    if is_ai_turn:  # AI's turn (we want to block 'X' from winning)
        for pattern in win_patterns:
            # Check if 'X' has two out of three in a winning pattern, and the move would block them
            x_count = sum(1 for square in pattern if board[square] == 'X')
            empty_count = sum(1 for square in pattern if board[square] == '')
            if x_count == 2 and empty_count == 1 and move in pattern:
                score += 50  # High score for blocking player's winning move
    
    # Additional heuristic: prioritize center and corners
    if move == 'b2':
        score += 10  # Center is a good strategic position
    elif move in ['a3', 'c3', 'a1', 'c1']:
        score += 5  # Corners are also valuable positions
    
    return score

def evaluate_all_moves(board, unoccupied):
    """
    Evaluate heuristic scores for all possible moves for the AI.
    
    Args:
        board (dict): The current board state.
        unoccupied (list): A list of unoccupied squares on the board.
    
    Returns:
        dict: A dictionary where keys are unoccupied squares and values are their heuristic scores.
    """
    move_scores = {}
    for move in unoccupied:
        # Evaluate the move using the heuristic function
        score = evaluate_move(board, move)
        move_scores[move] = score
    return move_scores

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
    if '' not in board.values() or winner == None:
        game.winner = 'Draw'  # Set the winner as 'Draw'
        game.completed = True  # Mark the game as completed
        game.save()  # Save the updated game state to the database
        request.session['winner'] = 'Draw'  # Store the draw result in the session
        return "Draw" # JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

    # If the game is not over, return None
    return None