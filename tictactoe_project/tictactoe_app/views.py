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

from django.middleware.csrf import get_token

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

load_dotenv()
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

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

@csrf_exempt
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

@csrf_exempt
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


# ___________________________________________________
@csrf_exempt
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