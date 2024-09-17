from django.shortcuts import render, redirect
from ..models import Game, GameLog
from django.contrib.auth.decorators import login_required
import random

import google.generativeai as genai
from django.http import JsonResponse
import json, os
from dotenv import load_dotenv

from django.middleware.csrf import get_token

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

@login_required(login_url='/login/')
def game_history(request):
    """
    Display the list of completed games for the logged-in user.
    """
    user = request.user
    completed_games = Game.objects.filter(player=user, completed=True)

    return render(request, 'tictactoe_app/game_history.html', {'games': completed_games})

@login_required
def check_win(board):
    """
    Check if there is a winning combination on the board.
    Args:
        board (dict): A dictionary representing the Tic-Tac-Toe board where keys are strings ('a3', 'b3', ..., 'c1') 
                      and values are 'X', 'O', or an empty string.
    Returns:
        str: 'X' if X wins, 'O' if O wins, None if no winner yet.
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

@login_required(login_url='/login/')
def tictactoe_result(request):
    """
    Render the Tic Tac Toe result page showing the winner or draw and the final board.
    """
    winner = request.session.get('winner', 'No winner')
    board = request.session.get('board', {
        'a3': '', 'b3': '', 'c3': '',
        'a2': '', 'b2': '', 'c2': '',
        'a1': '', 'b1': '', 'c1': ''
    })

    # Update: create the board list using the actual keys
    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]

    return render(request, 'tictactoe_app/tictactoe_result.html', {'winner': winner, 'board_list': board_list})

@login_required(login_url='/login/')
def make_move(request):
    """
    Handle the player's move and respond with AI's move.
    """
    if request.method == 'POST':
        board = request.session.get('board', {
            'a3': '', 'b3': '', 'c3': '',
            'a2': '', 'b2': '', 'c2': '',
            'a1': '', 'b1': '', 'c1': ''
        })

        data = json.loads(request.body)
        move = data.get('move')

        if not request.session.get('game_id'):
            game = Game.objects.create(player=request.user)
            request.session['game_id'] = game.game_id
        else:
            game = Game.objects.get(game_id=request.session['game_id'])

        turn_number = GameLog.objects.filter(game=game).count() + 1

        board[move] = 'X'

        GameLog.objects.create(
            game=game,
            turn_number=turn_number,
            player='X',
            cell=move
        )

        winner = check_win(board)
        if winner:
            game.winner = winner
            game.completed = True
            game.save()
            request.session['winner'] = winner
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        occupied_x = [key for key, value in board.items() if value == 'X']
        occupied_o = [key for key, value in board.items() if value == 'O']
        unoccupied = [key for key, value in board.items() if value == '']

        prompt = f"""
        Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
        Squares occupied by X: [{', '.join(occupied_x)}]
        Squares occupied by O: [{', '.join(occupied_o)}]
        Unoccupied squares: [{', '.join(unoccupied)}]
        You are playing as O. Your chosen move should be one of the unoccupied squares above. In your response, return exactly one string from {unoccupied}, representing your chosen move.
        """
        print(prompt)
        ai_move = ''
        attempts = 0
        max_attempts = 5

        while ai_move not in unoccupied and attempts < max_attempts:
            try:
                response = model.generate_content(prompt)
                ai_move = response.text.strip()  # AI returns the cell name
                print("AI MOVE: ", ai_move)
            except ValueError:
                print(f"Invalid response from AI: {response.text.strip()}")
                ai_move = ''
            attempts += 1
        
        if ai_move not in unoccupied:
            print("Max attempts reached. Selecting a random move from unoccupied.")
            ai_move = random.choice(unoccupied)

        board[ai_move] = 'O'

        turn_number += 1
        GameLog.objects.create(
            game=game,
            turn_number=turn_number,
            player='O',
            cell=ai_move
        )

        winner = check_win(board)
        if winner:
            game.winner = winner
            game.completed = True
            game.save()
            request.session['winner'] = winner
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        if '' not in board.values():
            game.winner = 'Draw'
            game.completed = True
            game.save()

            request.session['winner'] = 'Draw'
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        request.session['board'] = board

        return JsonResponse({
            'status': 'success',
            'ai_move': ai_move
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def tictactoe_game(request):
    """
    Render the Tic Tac Toe game page.
    """
    board = request.session.get('board', {
        'a3': '', 'b3': '', 'c3': '',
        'a2': '', 'b2': '', 'c2': '',
        'a1': '', 'b1': '', 'c1': ''
    })

    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]

    grid_cells = board_keys
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': grid_cells, 'board_list': board_list})

@login_required
def reset_game(request):
    """
    Reset the game by clearing the session board.
    """
    board = {
        'a3': '', 'b3': '', 'c3': '',
        'a2': '', 'b2': '', 'c2': '',
        'a1': '', 'b1': '', 'c1': ''
    }
    request.session['board'] = board

    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': board_keys, 'board_list': board_list})