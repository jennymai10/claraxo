from django.shortcuts import render, redirect
from .forms.user_registration_form import UserRegistrationForm
from .models import TicTacToeUser, Game, GameLog
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .forms.login_form import LoginForm
from django.conf import settings
import random
import google.generativeai as genai  # type: ignore
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
    """
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

    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] and board[combo[1]] == board[combo[2]] and board[combo[0]] != '':
            return board[combo[0]]
    return None


def tictactoe_result(request):
    """
    Render the Tic Tac Toe result page showing the winner or draw and the final board.
    """
    winner = request.session.get('winner', 'No winner')
    board = request.session.get('board', {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    })
    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]
    return render(request, 'tictactoe_app/tictactoe_result.html', {'winner': winner, 'board_list': board_list})


@csrf_exempt
def make_move(request):
    """
    Handle the player's move and respond with AI's move.
    """
    if request.method == 'POST':
        board = request.session.get('board', {
            '1': '', '2': '', '3': '',
            '4': '', '5': '', '6': '',
            '7': '', '8': '', '9': ''
        })

        data = json.loads(request.body)
        move = data.get('move')

        # Debugging: Check the move value
        print(f"Player's move: {move}")

        # Validate if the move is already occupied
        if board.get(move) != '':
            print("Move already occupied!")
            return JsonResponse({'status': 'error', 'message': 'Square already occupied'}, status=400)

        # Get or create the current game for the player
        if not request.session.get('game_id'):
            game = Game.objects.create(player=request.user)
            request.session['game_id'] = game.game_id
        else:
            game = Game.objects.get(game_id=request.session['game_id'])

        turn_number = GameLog.objects.filter(game=game).count() + 1

        # Update board with player's move
        board[move] = 'X'
        GameLog.objects.create(game=game, turn_number=turn_number, player='X', cell=move)

        winner = check_win(board)
        if winner:
            game.winner = winner
            game.completed = True
            game.save()
            request.session['winner'] = winner
            return JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

        unoccupied = [key for key, value in board.items() if value == '']
        if not unoccupied:
            game.winner = 'Draw'
            game.completed = True
            game.save()
            request.session['winner'] = 'Draw'
            return JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

        ai_move = random.choice(unoccupied)
        board[ai_move] = 'O'
        turn_number += 1
        GameLog.objects.create(game=game, turn_number=turn_number, player='O', cell=ai_move)

        winner = check_win(board)
        if winner:
            game.winner = winner
            game.completed = True
            game.save()
            request.session['winner'] = winner
            return JsonResponse({'status': 'success', 'redirect_url': '/tictactoe_result/'})

        request.session['board'] = board
        return JsonResponse({'status': 'success', 'ai_move': ai_move})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def tictactoe_game(request):
    """
    Render the Tic Tac Toe game page.
    """
    board = request.session.get('board', {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    })

    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]
    grid_cells = range(1, 10)
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': grid_cells, 'board_list': board_list})


@csrf_exempt
def reset_game(request):
    """
    Reset the game by clearing the session board.
    """
    board = {
        '1': '', '2': '', '3': '',
        '4': '', '5': '', '6': '',
        '7': '', '8': '', '9': ''
    }
    request.session['board'] = board
    board_list = [(cell, board[str(cell)]) for cell in range(1, 10)]
    return render(request, 'tictactoe_app/tictactoe_game.html', {'grid_cells': range(1, 10), 'board_list': board_list})


def register_user(request):
    """
    Handle the user registration process.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_code = random.randint(100000, 999999)
            user.is_active = False
            user.save()

            send_mail(
                'Email Verification',
                f'Your verification code is {user.verification_code}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect('http://localhost:8000/verify_email/')
        else:
            print(form.errors)  # Debugging form errors
    else:
        form = UserRegistrationForm()

    return render(request, 'tictactoe_app/register.html', {'form': form})


def verify_email(request):
    """
    Handle email verification for new users.
    """
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        try:
            user = TicTacToeUser.objects.get(username=username, verification_code=code)
            user.is_active = True
            user.verification_code = None
            user.save()
            login(request, user)
            return redirect('http://localhost:8000/login/')
        except TicTacToeUser.DoesNotExist:
            return render(request, 'tictactoe_app/verify_email.html', {'error': 'Invalid code or username'})
    return render(request, 'tictactoe_app/verify_email.html')


@login_required
def get_users(request):
    """
    Display all registered users.
    """
    users = TicTacToeUser.objects.all()
    return render(request, 'tictactoe_app/users.html', {'users': users})


def login_user(request):
    """
    Handle user login.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('http://localhost:8000/new_game/')
                else:
                    return render(request, 'tictactoe_app/login.html', {'error': 'Please verify your email before logging in.'})
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'tictactoe_app/login.html', {'form': form})
