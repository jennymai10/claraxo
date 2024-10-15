from django.shortcuts import render
from ..models import Game, GameLog
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from .game_utils import check_win, initialize_board, game_end_handler, generate_ai_move_with_logging
import google.generativeai as genai
from google.cloud import secretmanager
import os, random
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

def get_secret(secret_name):
    """
    Retrieve a secret value from Google Cloud Secret Manager.

    This function accesses the specified secret in Google Cloud Secret Manager and returns its value.

    Args:
        secret_name (str): The name of the secret to retrieve.

    Returns:
        str: The value of the secret.
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
    user = request.user  # Get the currently logged-in user
    completed_games = Game.objects.filter(player_id=user.id).values(
        'game_id', 'date', 'completed', 'winner'
    )  # Get relevant fields of completed games

    games_list = list(completed_games)  # Convert QuerySet to list of dicts

    return JsonResponse({'games': games_list}, status=200)


@login_required
@api_view(['POST'])
def game_moves(request):
    game_id = request.data.get('game_id')
    
    if not game_id:
        return JsonResponse({'error': 'Game ID is required.'}, status=400)
    
    # Fetch moves for the given game_id
    game_moves = GameLog.objects.filter(game_id=game_id).values(
        'turn_number', 'player', 'cell', 'timestamp'
    ).order_by('turn_number')  # Ensure the moves are ordered by turn number

    moves_list = list(game_moves)  # Convert QuerySet to list of dicts

    return JsonResponse({'moves': moves_list}, status=200)

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

        This view retrieves the winner and final board state from the session and renders
        them on the result page. If no winner is stored, it defaults to "No winner".

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Renders the result page with the game winner and final board state.
    """
    winner = request.session.get('winner', 'No winner')  # Retrieve the winner from the session
    board = request.session.get('board', initialize_board())  # Retrieve the board state or initialize if not found

    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']
    board_list = [(cell, board[cell]) for cell in board_keys]  # Create a list of board cells and their values

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
    This view processes the player's move, updates the game state, checks for a win or draw, 
    and generates the next move for the AI player.
    """
    if request.method == 'POST':
        try:
            # Retrieve or initialize the game board
            board = request.session.get('board', initialize_board())
            if not board:
                board = initialize_board()
            move = request.POST.get('move')  # Get the player's move from the request
            difficulty = request.POST.get('difficulty', 'medium')  # Get the AI difficulty level (default: medium)
            # Load or create the game object based on the session ID
            if not request.session.get('game_id'):
                game = Game.objects.create(player=request.user)  # Create a new game if not found
                request.session['game_id'] = game.game_id
            else:
                game = Game.objects.get(game_id=request.session['game_id'])
            # Validate the move: Check if the selected move is valid (the cell is empty)
            if board[move] != '':
                return JsonResponse({'status': 'error', 'message': 'Invalid move'}, status=400)

            # Player's move
            turn_number = GameLog.objects.filter(game=game).count() + 1  # Calculate the turn number
            board[move] = 'X'  # Place the player's move on the board
            GameLog.objects.create(game=game, turn_number=turn_number, player='X', cell=move)  # Log the move
            game.save()

            # Check if the player wins
            winner = check_win(board)
            if winner == 'X':
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'Player X wins', 'winner': 'X', 'ai_move': None})

            # Check for a draw (if all squares are filled and no winner)
            unoccupied = [key for key, value in board.items() if value == '']
            if not unoccupied:
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'The game is a draw.'})

            if not request.user.api_key_expiry_date:
                api_key = 'Invalid'
            else:
                api_key = get_secret(f"api-key-{request.user.api_key_secret_id}")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")  # Initialize the AI model

            # Generate AI's move
            ai_move, _, prompt_log, ai_response_log = generate_ai_move_with_logging(board, unoccupied, model, difficulty, move)  # Generate the AI's move

            board[ai_move] = 'O'  # Place the AI's move on the board

            # Log the AI's move
            turn_number += 1
            GameLog.objects.create(game=game, turn_number=turn_number, player='O', cell=ai_move)

            # Check if the AI wins
            winner = check_win(board)
            if winner == 'O':
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'AI wins', 'ai_move': ai_move, 'winner': 'O', 'prompt_log': prompt_log, 'ai_response_log': ai_response_log})

            # Check again for a draw after AI's move
            unoccupied = [key for key, value in board.items() if value == '']
            if not unoccupied:
                _ = game_end_handler(board, game, None, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'draw', 'ai_move': 'None\nThe game is a draw', 'message': 'The game is a draw.'})

            # Save the updated board state in the session
            request.session['board'] = board
            game.save()

            # if error_code == 1:
            #     return JsonResponse({
            #         'status': 'success',
            #         'ai_move': ai_move,
            #         'message': 'Invalid API key or Insufficient quota.\nA random move was played.',
            #         'errors': {'all': 'Invalid API key or Insufficient quota.\nA random move was played.'},
            #         'prompt_log': prompt_log,  # Include the prompt sent to Gemini
            #         'ai_response_log': ai_response_log  # Include the AI response from Gemini
            #     }, status=200)

            # Return AI move in the response, including prompt and AI response logs
            return JsonResponse({'status': 'success', 'ai_move': ai_move, 'prompt_log': prompt_log, 'ai_response_log': ai_response_log})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



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

    This view initializes or retrieves the current game board from the session and
    prepares it for display on the game page. The board is represented as a dictionary
    where each key corresponds to a cell on the Tic Tac Toe grid (e.g., 'a3', 'b2'),
    and each value is either 'X', 'O', or an empty string indicating an unoccupied cell.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the Tic Tac Toe game page with the current state of the game board.
    """
    # Retrieve the current board state from the session or initialize a new board if not found
    board = request.session.get('board', initialize_board())

    # Define the keys for each cell on the board in display order
    board_keys = ['a3', 'b3', 'c3', 'a2', 'b2', 'c2', 'a1', 'b1', 'c1']

    # Create a list of tuples containing each cell and its current value
    board_list = [(cell, board[cell]) for cell in board_keys]

    # Render the game page template with the grid cells and the board list
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': board_keys, 'board_list': board_list})


@login_required
@api_view(['POST'])
def reset_game(request):
    """
    Reset the game by clearing the session board.

    This view clears the current game state stored in the session and resets the game board.
    It then redirects the user to the main game page to start a new game. This function is
    typically used when a user wants to start a fresh game after finishing or abandoning a previous one.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects the user to the Tic Tac Toe game page.
    """
    # Initialize a new empty game board
    board = initialize_board()

    # Save the new board state in the session
    request.session['board'] = board

    # Remove the game ID from the session, effectively ending the current game
    request.session.pop('game_id', None)

    # Redirect the user to the Tic Tac Toe game page
    return JsonResponse({'status': 'success', 'message': 'Game reset successfully.'}, status=200)
