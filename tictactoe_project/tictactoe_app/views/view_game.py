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
    
    # Initialize the Secret Manager client to access Google Cloud secrets
    client = secretmanager.SecretManagerServiceClient()

    # Define the project ID and format the secret version path for access
    project_id = 'c-lara'
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    # Access the latest version of the specified secret
    response = client.access_secret_version(name=name)

    # Decode the secret payload from bytes to a UTF-8 string and return it
    return response.payload.data.decode('UTF-8')

@swagger_auto_schema(
    method='get',
    operation_description="Get the game history of the logged-in user",
    responses={
        200: openapi.Response(
            'Game History', 
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'games': openapi.Schema(
                        type=openapi.TYPE_ARRAY, 
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Unique game ID"),
                                'player': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the player"),
                                'date': openapi.Schema(type=openapi.TYPE_STRING, description="Date of the game"),
                                'completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Status of the game completion"),
                                'winner': openapi.Schema(type=openapi.TYPE_STRING, description="Winner of the game"),
                                'ai_difficulty': openapi.Schema(type=openapi.TYPE_STRING, description="AI difficulty level for the game"),
                            }
                        )
                    )
                }
            )
        ),
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['GET'])
def game_history(request):
    """
    Retrieve the completed game history for the logged-in user.
    Returns a JSON response with game details including ID, AI difficulty, date,
    completion status, and winner.
    """
    
    user = request.user  # Get the current user

    # Fetch completed games for the user, selecting relevant fields only
    completed_games = Game.objects.filter(player_id=user.id).values(
        'game_id', 'ai_difficulty', 'date', 'completed', 'winner'
    )

    # Convert QuerySet to a list of dictionaries for JSON response
    games_list = list(completed_games)

    return JsonResponse({'games': games_list}, status=200)  # Return data with HTTP 200 status

@swagger_auto_schema(
    method='post',
    operation_description="Retrieve the moves for a specific game by its ID",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['game_id'],
        properties={
            'game_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Unique identifier for the game"),
        }
    ),
    responses={
        200: openapi.Response(
            'Moves Retrieved Successfully',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'moves': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'turn_number': openapi.Schema(type=openapi.TYPE_INTEGER, description="Turn sequence number"),
                                'player': openapi.Schema(type=openapi.TYPE_STRING, description="Player who made the move"),
                                'cell': openapi.Schema(type=openapi.TYPE_STRING, description="Cell position of the move"),
                                'timestamp': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Time of move"),
                            }
                        )
                    )
                }
            )
        ),
        400: 'Bad Request: Game ID is required',
        401: 'Unauthorized',
    }
)
@login_required
@api_view(['POST'])
def game_moves(request):
    """
    Retrieve move history for a specified game.
    Expects a game ID in the request data and returns the ordered list of moves
    including turn number, player, cell, and timestamp.
    """
    
    game_id = request.data.get('game_id')  # Get game ID from request data
    
    # Check if game_id is provided, else return error
    if not game_id:
        return JsonResponse({'error': 'Game ID is required.'}, status=400)
    
    # Query game moves by game ID, ordered by turn number
    game_moves = GameLog.objects.filter(game_id=game_id).values(
        'turn_number', 'player', 'cell', 'timestamp'
    ).order_by('turn_number')

    moves_list = list(game_moves)  # Convert QuerySet to list format for JSON response

    return JsonResponse({'moves': moves_list}, status=200)  # Return moves with HTTP 200 status

@swagger_auto_schema(
    method='post',
    operation_description="Process the player's move, update the game state, and generate the AI's move in response.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['move'],
        properties={
            'move': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="The cell position where the player wants to make a move (e.g., 'a1', 'b2')."
            ),
            'difficulty': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="AI difficulty level (e.g., 'easy', 'medium', 'hard'). Defaults to 'medium'.",
                enum=['easy', 'medium', 'hard']
            ),
        }
    ),
    responses={
        200: openapi.Response(
            description="Move processed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="Indicates success of the operation, typically 'success'."
                    ),
                    'ai_move': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="The cell where the AI made its move."
                    ),
                    'prompt_log': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="Log of the prompt sent to the AI for move generation."
                    ),
                    'ai_response_log': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="Log of the response generated by the AI."
                    ),
                    'winner': openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="Indicates the winner ('X' for player, 'O' for AI) if the game ended with this move.",
                        enum=['X', 'O', None]
                    ),
                    'message': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Additional message regarding game outcome, e.g., 'Player X wins', 'The game is a draw'."
                    ),
                }
            )
        ),
        400: openapi.Response(
            description="Bad Request: Invalid move or game state",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates error status."),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the issue.")
                }
            )
        ),
        401: 'Unauthorized: Authentication required',
        405: 'Method Not Allowed: Only POST is allowed',
        500: openapi.Response(
            description="Server Error: Internal issue processing the move",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates error status."),
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description="Error message describing the server issue.")
                }
            )
        ),
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
            # Load the game board from the session or initialize a new board
            board = request.session.get('board', initialize_board())
            if not board:
                board = initialize_board()
            move = request.POST.get('move') # Get the player's move from the request data
            difficulty = request.POST.get('difficulty', 'medium') # Get the AI difficulty level from the request data
            
            # Validate the move: Check if the selected move is valid (the cell is empty)
            if not request.session.get('game_id'):
                game = Game.objects.create(player=request.user) # Create a new game instance
                request.session['game_id'] = game.game_id
            else:
                game = Game.objects.get(game_id=request.session['game_id'])

            # Validate the move: Check if the selected move is valid (the cell is empty)
            if board[move] != '':
                return JsonResponse({'status': 'error', 'message': 'Invalid move'}, status=400)

            # Check if the game log is empty, if so, initialize it
            if game.game_log == None or game.game_log == '':
                game.game_log = ""
                game.game_log = game.game_log + f"Game ID: {game.game_id}\n"
                game.game_log = game.game_log + f"Game Date: {game.date}\n"
                game.game_log = game.game_log + f"Game Difficulty: {game.ai_difficulty}\n"
                game.game_log = game.game_log + f"Player: {game.player.username}\nPlayer's Symbol: {game.player_symbol}\nAI's Symbol: {game.ai_symbol}\n"
                game.save()
            
            # Update the game difficulty level
            game.ai_difficulty = difficulty
            
            # Check if the player wins
            turn_number = GameLog.objects.filter(game=game).count() + 1 # Get the current turn number
            board[move] = 'X' # Place the player's move on the board
            GameLog.objects.create(game=game, turn_number=turn_number, player='X', cell=move) # Log the player's move
            
            # Log the player's move
            game.game_log = game.game_log + f"Turn {turn_number}: Player X played at {move}\n"
            game.game_log = game.game_log + f"Board state: \n{board['a3']} | {board['b3']} | {board['c3']}\n{board['a2']} | {board['b2']} | {board['c2']}\n{board['a1']} | {board['b1']} | {board['c1']}\n"
            game.save()


            # Check if the player wins
            winner = check_win(board)
            if winner == 'X':
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'Player X wins', 'winner': 'X', 'ai_move': None})

            # Check if the board is full (draw)
            unoccupied = [key for key, value in board.items() if value == '']
            if not unoccupied:
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'The game is a draw.'})

            # Generate AI's move
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

            # Log the AI's move
            game.game_log = game.game_log + f"Prompt: {prompt_log}\n"   
            game.game_log = game.game_log + f"AI Response: {ai_response_log}\n" 
            game.game_log = game.game_log + f"Turn {turn_number}: AI O played at {ai_move}\n"   
            game.game_log = game.game_log + f"Board state: \n{board['a3']} | {board['b3']} | {board['c3']}\n{board['a2']} | {board['b2']} | {board['c2']}\n{board['a1']} | {board['b1']} | {board['c1']}\n"  # Log the board state
            game.save()

            # Check if the AI wins
            winner = check_win(board)
            if winner == 'O':
                _ = game_end_handler(board, game, winner, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'success', 'message': 'AI wins', 'ai_move': ai_move, 'winner': 'O', 'prompt_log': prompt_log, 'ai_response_log': ai_response_log})

            # Check if the board is full (draw)
            unoccupied = [key for key, value in board.items() if value == '']
            if not unoccupied:
                _ = game_end_handler(board, game, None, request)
                request.session['board'] = None
                request.session['game_id'] = None
                return JsonResponse({'status': 'draw', 'ai_move': 'None\nThe game is a draw', 'message': 'The game is a draw.'})

            # Save the updated board to the session
            request.session['board'] = board
            game.save()
            return JsonResponse({'status': 'success', 'ai_move': ai_move, 'prompt_log': prompt_log, 'ai_response_log': ai_response_log})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@swagger_auto_schema(
    method='post',
    operation_description="Retrieve the game log for a specified game by game ID.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['game_id'],
        properties={
            'game_id': openapi.Schema(
                type=openapi.TYPE_INTEGER, 
                description="Unique identifier for the game"
            ),
        }
    ),
    responses={
        200: openapi.Response(
            'Game Log Retrieved',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'game_log': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="The log of moves for the specified game"
                    ),
                }
            )
        ),
        400: 'Bad Request: Invalid Game ID',
        401: 'Unauthorized',
    }
)
@api_view(['POST'])
def get_game_log(request):
    """
    Retrieve the game log for a specific game.

    Expects a game ID in the request data and returns the corresponding game log as JSON.
    """

    game_id = request.data.get('game_id')  # Get game ID from the request data

    # Validate that a game ID was provided
    if not game_id:
        return JsonResponse({'error': 'Invalid Game ID.'}, status=400)

    # Retrieve the game log for the given game ID
    game_log = Game.objects.get(game_id=game_id).game_log

    # Return the game log as a JSON response
    return JsonResponse({'game_log': game_log}, status=200)