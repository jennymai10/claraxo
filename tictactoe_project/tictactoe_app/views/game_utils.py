import random
from django.http import JsonResponse

def check_win(board):
    """
    Check if there is a winning combination on the board.
    """
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
    
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] and board[combo[1]] == board[combo[2]] and board[combo[0]] != '':
            return board[combo[0]]  # Return 'X' or 'O' if we have a winner
    return None

def initialize_board():
    """
    Initialize a new Tic-Tac-Toe board.
    """
    return {
        'a3': '', 'b3': '', 'c3': '',
        'a2': '', 'b2': '', 'c2': '',
        'a1': '', 'b1': '', 'c1': ''
    }

def generate_ai_move(board, unoccupied, model):
    """
    Generate the AI move using an external model (Generative AI).
    """
    prompt = f"""
    Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
    Squares occupied by X: [{', '.join([key for key, value in board.items() if value == 'X'])}]
    Squares occupied by O: [{', '.join([key for key, value in board.items() if value == 'O'])}]
    Unoccupied squares: [{', '.join(unoccupied)}]
    You are playing as O. Your chosen move should be one of the unoccupied squares above. In your response, return exactly one string from {unoccupied}, representing your chosen move.
    """
    
    ai_move = ''
    attempts = 0
    max_attempts = 5
    
    while ai_move not in unoccupied and attempts < max_attempts:
        try:
            response = model.generate_content(prompt)
            ai_move = response.text.strip()  # AI returns the cell name
        except ValueError:
            ai_move = ''  # Fallback in case of invalid response
        attempts += 1
    
    if ai_move not in unoccupied:
        ai_move = random.choice(unoccupied)
    
    return ai_move

def game_end_handler(board, game, winner, request):
    """
    Handle game ending scenarios such as a winner or a draw.
    """
    if winner:
        game.winner = winner
        game.completed = True
        game.save()
        request.session['winner'] = winner
        return JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})


    if '' not in board.values():
        game.winner = 'Draw'
        game.completed = True
        game.save()
        request.session['winner'] = 'Draw'
        return JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})
    
    return None
