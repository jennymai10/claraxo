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
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

def get_secret(secret_name):
    """
    Retrieve secret value from Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    project_id = 'c-lara'
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode('UTF-8')

@swagger_auto_schema(
    method='get',
    operation_description="Get the game history of the logged-in user",
    responses={
        200: openapi.Response('Game History', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'games': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'player': openapi.Schema(type=openapi.TYPE_STRING),
                        'date': openapi.Schema(type=openapi.TYPE_STRING),
                        'completed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'winner': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )),
            }
        )),
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['GET'])
def game_history(request):
    """
    Display the list of completed games for the logged-in user.
    """
    user = request.user
    completed_games = Game.objects.filter(player=user, completed=True)
    return render(request, 'tictactoe_app/game_history.html', {'games': completed_games})

@swagger_auto_schema(
    method='get',
    operation_description="Get the result of the current game with the final board state",
    responses={
        200: openapi.Response('Game Result', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'winner': openapi.Schema(type=openapi.TYPE_STRING),
                'board_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cell': openapi.Schema(type=openapi.TYPE_STRING),
                        'value': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )),
            }
        )),
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['GET'])
def tictactoe_result(request):
    """
    Render the Tic Tac Toe result page showing the winner or draw and the final board.
    """
    winner = request.session.get('winner', 'No winner')
    board = request.session.get('board', initialize_board())

    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]

    return render(request, 'tictactoe_app/tictactoe_result.html', {'winner': winner, 'board_list': board_list})

@swagger_auto_schema(
    method='post',
    operation_description="Handle the player's move and respond with the AI's move",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'move': openapi.Schema(type=openapi.TYPE_STRING, description='The player\'s move in chess notation (e.g., a1, b2, etc.)')
        },
        required=['move']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'ai_move': openapi.Schema(type=openapi.TYPE_STRING, description='The AI\'s move in chess notation (e.g., a1, b2, etc.)'),
            }
        )),
        400: 'Invalid Request',
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['POST'])
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

@swagger_auto_schema(
    method='get',
    operation_description="Render the current state of the Tic-Tac-Toe game board",
    responses={
        200: openapi.Response('Game Board', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'grid_cells': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'board_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cell': openapi.Schema(type=openapi.TYPE_STRING),
                        'value': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )),
            }
        )),
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['GET'])
def tictactoe_game(request):
    """
    Render the Tic Tac Toe game page.
    """
    board = request.session.get('board', initialize_board())
    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': board_keys, 'board_list': board_list})

@swagger_auto_schema(
    method='get',
    operation_description="Reset the current game by clearing the session and starting a new game",
    responses={
        302: 'Redirect to the game page',
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['GET'])
def reset_game(request):
    """
    Reset the game by clearing the session board.
    """
    board = initialize_board()
    request.session['board'] = board
    request.session.pop('game_id', None)
    return redirect('tictactoe_game')