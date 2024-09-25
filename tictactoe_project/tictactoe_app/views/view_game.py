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
    """
    Display the list of completed games for the logged-in user.

    This view retrieves and displays the game history of the currently logged-in user.
    It queries for games that the user has completed and renders them in the game history page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the game history page with the list of completed games.
    """
    user = request.user  # Get the currently logged-in user
    completed_games = Game.objects.filter(player=user, completed=True)  # Get the list of completed games
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

        This view processes the player's move, updates the game state, and checks for a win or draw condition.
        It then uses an AI model to generate the next move for the AI player, updates the board, and returns
        the AI's move in the response.

        Args:
            request (HttpRequest): The HTTP request object containing the player's move.

        Returns:
            JsonResponse: A JSON response with the AI's move and the status of the game.
    """
    if request.method == 'POST':
        board = request.session.get('board', initialize_board())  # Retrieve or initialize the game board
        data = json.loads(request.body) # Parse the JSON request body
        move = data.get('move')  # Get the player's move from the request

        # Load or create the game object based on the session ID
        if not request.session.get('game_id'):
            game = Game.objects.create(player=request.user)  # Create a new game if not found
            request.session['game_id'] = game.game_id
        else:
            game = Game.objects.get(game_id=request.session['game_id'])

        # Process player's move
        turn_number = GameLog.objects.filter(game=game).count() + 1  # Calculate the turn number
        board[move] = 'X'  # Place the player's move on the board
        GameLog.objects.create(game=game, turn_number=turn_number, player='X', cell=move)  # Log the move
        game.save()  # Save the game state

        # Check if the player wins
        winner = check_win(board)
        result = game_end_handler(board, game, winner, request)
        if result:
            return result  # Return the result if the game ends

        # Retrieve the API key for the AI model from the user's profile
        api_key = get_secret(f"api-key-{request.user.api_key_secret_id}")
        print(api_key)  # Print the API key for debugging (not recommended in production)
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")  # Initialize the AI model

        # AI Move
        unoccupied = [key for key, value in board.items() if value == '']  # Get list of unoccupied squares
        ai_move = generate_ai_move(board, unoccupied, model)  # Generate the AI's move
        board[ai_move] = 'O'  # Place the AI's move on the board

        turn_number += 1
        GameLog.objects.create(game=game, turn_number=turn_number, player='O', cell=ai_move)  # Log the AI's move

        # Check if the AI wins
        winner = check_win(board)
        result = game_end_handler(board, game, winner, request)
        if result:
            return result  # Return the result if the game ends

        # Save the updated board state in the session
        request.session['board'] = board
        request.session.modified = True
        game.save()
        return JsonResponse({'status': 'success', 'ai_move': ai_move})  # Respond with the AI's move

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})  # Handle invalid request methods

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
    return redirect('tictactoe_game')
