from django.shortcuts import render, redirect
from ..models import Game, GameLog
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .game_utils import check_win, initialize_board, generate_ai_move, game_end_handler
import google.generativeai as genai
from google.cloud import secretmanager
import os
from ..models import TicTacToeUser

# genai.configure(api_key=os.environ["API_KEY"])

def get_secret(secret_name):
    """
    Retrieve secret value from Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    project_id = 'c-lara'
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

@login_required
def game_history(request):
    """
    Display the list of completed games for the logged-in user.
    """
    user = request.user
    completed_games = Game.objects.filter(player=user, completed=True)
    return render(request, 'tictactoe_app/game_history.html', {'games': completed_games})

@login_required
def tictactoe_result(request):
    """
    Render the Tic Tac Toe result page showing the winner or draw and the final board.
    """
    winner = request.session.get('winner', 'No winner')
    board = request.session.get('board', initialize_board())

    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]

    return render(request, 'tictactoe_app/tictactoe_result.html', {'winner': winner, 'board_list': board_list})

@login_required
def make_move(request):
    """
    Handle the player's move and respond with AI's move.
    """
    if request.method == 'POST':
        board = request.session.get('board', initialize_board())
        data = json.loads(request.body)
        move = data.get('move')

        # Load or create the game
        if not request.session.get('game_id'):
            game = Game.objects.create(player=request.user)
            request.session['game_id'] = game.game_id
        else:
            game = Game.objects.get(game_id=request.session['game_id'])

        # Process player's move
        turn_number = GameLog.objects.filter(game=game).count() + 1
        board[move] = 'X'
        GameLog.objects.create(game=game, turn_number=turn_number, player='X', cell=move)
        game.save()

        # Check if the player wins
        winner = check_win(board)
        result = game_end_handler(board, game, winner, request)
        if result:
            return result

        # Retrieve the API key from the logged-in user's profile
        api_key = get_secret(f"api-key-{request.user.api_key_secret_id}")
        print(api_key)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # AI Move
        unoccupied = [key for key, value in board.items() if value == '']
        ai_move = generate_ai_move(board, unoccupied, model)
        board[ai_move] = 'O'

        turn_number += 1
        GameLog.objects.create(game=game, turn_number=turn_number, player='O', cell=ai_move)

        # Check if the AI wins
        winner = check_win(board)
        result = game_end_handler(board, game, winner, request)
        if result:
            return result

        # Save board state
        request.session['board'] = board
        request.session.modified = True
        game.save()
        return JsonResponse({'status': 'success', 'ai_move': ai_move})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def tictactoe_game(request):
    """
    Render the Tic Tac Toe game page.
    """
    board = request.session.get('board', initialize_board())
    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': board_keys, 'board_list': board_list})

@login_required
def reset_game(request):
    """
    Reset the game by clearing the session board.
    """
    board = initialize_board()
    request.session['board'] = board
    request.session.pop('game_id', None)
    return redirect('tictactoe_game')