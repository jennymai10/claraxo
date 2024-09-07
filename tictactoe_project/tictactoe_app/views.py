from django.shortcuts import render, redirect
from .forms.user_registration_form import UserRegistrationForm
from .models import TicTacToeUser, Game, GameLog
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms.login_form import LoginForm
from django.conf import settings
import random

import google.generativeai as genai # type: ignore
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json, os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

def check_win(board):
    """
    Check if there is a winning combination on the board.

    Args:
        board (dict): A dictionary representing the Tic-Tac-Toe board where keys are strings ('1', '2', ..., '9') 
                      and values are 'X', 'O', or an empty string.

    Returns:
        str: 'X' if X wins, 'O' if O wins, None if no winner yet.
    """
    # Define all possible winning combinations
    winning_combinations = [
        ['1', '2', '3'],  # Top row
        ['4', '5', '6'],  # Middle row
        ['7', '8', '9'],  # Bottom row
        ['1', '4', '7'],  # Left column
        ['2', '5', '8'],  # Middle column
        ['3', '6', '9'],  # Right column
        ['1', '5', '9'],  # Left diagonal
        ['3', '5', '7']   # Right diagonal
    ]

    # Check each winning combination
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] and board[combo[1]] == board[combo[2]] and board[combo[0]] != '':
            return board[combo[0]]  # Return 'X' or 'O' if we have a winner

    # No winner
    return None

def tictactoe_result(request):
    """
    Render the Tic Tac Toe result page showing the winner or draw and the final board.
    """
    # Get the winner and board from the session
    winner = request.session.get('winner', 'No winner')
    board = request.session.get('board', {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    })

    # Convert the board to a list of tuples (cell number, value) for easier display in the template
    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]

    return render(request, 'tictactoe_app/tictactoe_result.html', {'winner': winner, 'board_list': board_list})

@csrf_exempt
def make_move(request):
    """
    Handle the player's move and respond with AI's move.
    """
    if request.method == 'POST':
        # Load the current board state from the session, or initialize a new one if it doesn't exist
        board = request.session.get('board', {
            '1': '', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        })

        # Get the player's move from the request
        data = json.loads(request.body)
        move = data.get('move')

        # Get or create the current game for the player (assuming authenticated)
        if not request.session.get('game_id'):
            game = Game.objects.create(player=request.user)
            request.session['game_id'] = game.game_id
        else:
            game = Game.objects.get(game_id=request.session['game_id'])

        # Get the current turn number (increment after each move)
        turn_number = GameLog.objects.filter(game=game).count() + 1

        # Update board with player's move
        board[move] = 'X'

        # Save the player's move to the GameLog
        GameLog.objects.create(
            game=game,
            turn_number=turn_number,
            player='X',
            cell=move
        )

        # Check if the player has won
        winner = check_win(board)
        if winner:
            # Store the winner and mark the game as completed
            game.winner = winner
            game.completed = True
            game.save()

            # Store the winner in the session and redirect to result page
            request.session['winner'] = winner
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        # Prepare the board state for the AI
        occupied_x = [key for key, value in board.items() if value == 'X']
        occupied_o = [key for key, value in board.items() if value == 'O']
        unoccupied = [key for key, value in board.items() if value == '']

        # Prepare input prompt for AI
        prompt = f"""
        Given the current Tic-Tac-Toe board state, where the squares occupied by X and O, and the unoccupied squares, are given using chess algebraic notation:
        Squares occupied by X: [{', '.join(occupied_x)}]
        Squares occupied by O: [{', '.join(occupied_o)}]
        Unoccupied squares: [{', '.join(unoccupied)}]
        You are playing as O. Your chosen move should be one of the unoccupied squares above. In your response, return exactly one integer digit from 1 to 9, representing your chosen move.
        """
        print(prompt)
        ai_move = -1
        attempts = 0  # Limit the number of retries
        max_attempts = 5  # Set a limit to avoid an infinite loop

        while str(ai_move) not in unoccupied and attempts < max_attempts:
            try:
                # Call the Gemini model to get the AI's move
                response = model.generate_content(prompt)
                ai_move = int(response.text.strip())  # Convert AI's response to an integer
                print("AI MOVE: ", ai_move)
            except ValueError:
                # Handle cases where the response isn't a valid integer
                print(f"Invalid response from AI: {response.text.strip()}")
                ai_move = -1  # Reset ai_move to an invalid value
            attempts += 1
        
        if str(ai_move) not in unoccupied:
            print("Max attempts reached. Selecting a random move from unoccupied.")
            ai_move = random.choice(unoccupied)

        # Update board with AI's move
        board[str(ai_move)] = 'O'

        # Save the AI's move to the GameLog
        turn_number += 1
        GameLog.objects.create(
            game=game,
            turn_number=turn_number,
            player='O',
            cell=str(ai_move)
        )

        # Check if the AI has won
        winner = check_win(board)
        if winner:
            # Store the winner and mark the game as completed
            game.winner = winner
            game.completed = True
            game.save()

            # Store the winner in the session and redirect to result page
            request.session['winner'] = winner
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        # Check if it's a draw
        if '' not in board.values():
            game.winner = 'Draw'
            game.completed = True
            game.save()

            request.session['winner'] = 'Draw'
            return JsonResponse({
                'status': 'success',
                'redirect_url': '/tictactoe_result/'
            })

        # Save the updated board state back to the session
        request.session['board'] = board

        # Return the AI's move
        return JsonResponse({
            'status': 'success',
            'ai_move': ai_move
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def tictactoe_game(request):
    """
    Render the Tic Tac Toe game page.
    """
    # Retrieve the current board from the session, or initialize it if it doesn't exist
    board = request.session.get('board', {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    })

    # Convert the dictionary to a list of tuples (cell number, value) for easier template access
    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]

    # Pass both the board list and grid cells to the template
    grid_cells = range(1, 10)
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': grid_cells, 'board_list': board_list})
    
@csrf_exempt
def reset_game(request):
    """
    Reset the game by clearing the session board.
    """
    # Clear the board from the session
    board = {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    }
    request.session['board'] = board
    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': range(1, 10), 'board_list': board_list})


# ___________________________________________________
def register_user(request):
    """
    Handle the user registration process.

    This view renders a registration form where a new user can input their details. 
    If the request method is POST, the form is validated, and if valid:
    - A new user instance is created with the form data.
    - A random 6-digit verification code is generated.
    - The user's 'is_active' field is set to False, so the user cannot log in until email verification.
    - An email with the verification code is sent to the user's email address.
    On successful registration, the user is redirected to the email verification page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered registration template with the form.
        HttpResponseRedirect: Redirect to the email verification page if the form is valid.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user temporarily without committing to add verification details
            user = form.save(commit=False)
            # Generate a random 6-digit verification code
            user.verification_code = random.randint(100000, 999999)
            # Mark the user as inactive until email is verified
            user.is_active = False
            user.save()

            # Send verification email with the generated code
            send_mail(
                'Email Verification',
                f'Your verification code is {user.verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            # Redirect to the email verification page
            return redirect('http://localhost:8000/verify_email/')
    else:
        # Display the empty registration form for a GET request
        form = UserRegistrationForm()

    return render(request, 'tictactoe_app/register.html', {'form': form})


def verify_email(request):
    """
    Handle email verification for new users.

    This view allows the user to input their username and the 6-digit verification code
    they received via email. If the code matches the one generated during registration,
    the user's account is activated, and they are logged in. Otherwise, an error message
    is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered email verification template with or without an error message.
        HttpResponseRedirect: Redirect to the login page after successful verification and activation.
    """
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        try:
            # Retrieve the user by their username and verification code
            user = TicTacToeUser.objects.get(username=username, verification_code=code)
            # Activate the user and clear the verification code
            user.is_active = True
            user.verification_code = None
            user.save()
            # Automatically log in the user after verification
            login(request, user)
            # Redirect to the login page
            return redirect('http://localhost:8000/login/')
        except TicTacToeUser.DoesNotExist:
            # If the username or code is incorrect, render the verification page with an error
            return render(request, 'tictactoe_app/verify_email.html', {'error': 'Invalid code or username'})
    return render(request, 'tictactoe_app/verify_email.html')


@login_required
def get_users(request):
    """
    Display all registered users.

    This view retrieves all TicTacToeUser instances from the database and displays
    them on the users page. It is only accessible to logged-in users due to the 
    @login_required decorator.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template with the list of registered users.
    """
    # Query all registered users from the TicTacToeUser model
    users = TicTacToeUser.objects.all()
    # Render the users template and pass the users data to the template
    return render(request, 'tictactoe_app/users.html', {'users': users})


def login_user(request):
    """
    Handle user login.

    This view processes the login form, where a user can input their username and password.
    If the credentials are valid, the user is logged in and redirected to the users page.
    If the user's account is not activated (i.e., email not verified), they are prompted
    to verify their email first. If the credentials are invalid, an error message is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered login template with the form and optional error messages.
        HttpResponseRedirect: Redirect to the users page after successful login.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate the user with the provided credentials
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if the user's email is verified (is_active is True)
                if user.is_active:
                    login(request, user)  # Log in the user
                    return redirect('http://localhost:8000/new_game/')  # Redirect to the users page
                else:
                    # If the user's email is not verified, display an error message
                    return render(request, 'tictactoe_app/login.html', {'error': 'Please verify your email before logging in.'})
            else:
                # If the credentials are invalid, add an error to the form
                form.add_error(None, 'Invalid username or password.')
    else:
        # Display the empty login form for a GET request
        form = LoginForm()

    return render(request, 'tictactoe_app/login.html', {'form': form})